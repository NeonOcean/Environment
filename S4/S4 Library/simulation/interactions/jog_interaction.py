from _math import Vector3
import itertools
from element_utils import do_all
from event_testing.results import TestResult
from interactions import TargetType
from interactions.base.super_interaction import SuperInteraction
from interactions.utils.routing import FollowPath, PlanRoute, get_route_element_for_path
from routing.walkstyle.walkstyle_request import WalkStyleRequest
from routing.waypoints.waypoint_generator_variant import TunableWaypointGeneratorVariant
from routing.waypoints.waypoint_stitching import WaypointStitchingVariant
from sims4.tuning.tunable import TunableRange
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import flexmethod
import element_utils
import routing
import sims4.log
logger = sims4.log.Logger('WaypointInteraction')

class _WaypointGeneratorRallyable:

    def __init__(self, waypoint_info):
        self._original_generator = waypoint_info

    def get_start_constraint(self):
        return self._original_generator.get_start_constraint()

    def get_waypoint_constraints_gen(self, sim, waypoint_count):
        yield from self._original_generator.get_waypoint_constraints_gen(sim, waypoint_count)

class WaypointInteraction(SuperInteraction):
    INSTANCE_TUNABLES = {'waypoint_constraint': TunableWaypointGeneratorVariant(tuning_group=GroupNames.ROUTING), 'waypoint_count': TunableRange(description='\n            The number of waypoints to select, from spawn points in the zone, to\n            visit for a Jog prior to returning to the original location.\n            ', tunable_type=int, default=2, minimum=2, tuning_group=GroupNames.ROUTING), 'waypoint_walk_style': WalkStyleRequest.TunableFactory(description='\n            The walkstyle to use when routing between waypoints.\n            ', tuning_group=GroupNames.ROUTING), 'waypoint_stitching': WaypointStitchingVariant(tuning_group=GroupNames.ROUTING)}

    def __init__(self, aop, *args, **kwargs):
        super().__init__(aop, *args, **kwargs)
        waypoint_info = kwargs.get('waypoint_info')
        if waypoint_info is not None:
            self._waypoint_generator = _WaypointGeneratorRallyable(waypoint_info)
        else:
            if aop.target is None and self.target_type is TargetType.ACTOR:
                target = self.sim
            else:
                target = aop.target
            self._waypoint_generator = self.waypoint_constraint(self.context, target)

    @classmethod
    def _test(cls, target, context, **interaction_parameters):
        sim = context.sim
        routing_master = sim.routing_master
        if routing_master is not None:
            return TestResult(False, '{} cannot run Waypoint interactions because they are slaved to {}', sim, routing_master)
        return super()._test(target, context, **interaction_parameters)

    @flexmethod
    def _constraint_gen(cls, inst, *args, **kwargs):
        inst_or_cls = inst if inst is not None else cls
        if inst is not None:
            constraint = inst._waypoint_generator.get_start_constraint()
            posture_constraint = inst._waypoint_generator.get_posture_constraint()
            constraint = constraint.intersect(posture_constraint)
            yield constraint
        yield from super(__class__, inst_or_cls)._constraint_gen(*args, **kwargs)

    def cancel(self, *args, **kwargs):
        for sim_primitive in list(self.sim.primitives):
            if isinstance(sim_primitive, FollowPath):
                sim_primitive.detach()
        return super().cancel(*args, **kwargs)

    def _get_goals_for_constraint(self, constraint):
        goals = []
        handles = constraint.get_connectivity_handles(self.sim)
        for handle in handles:
            goals.extend(handle.get_goals())
        return goals

    def _run_interaction_gen(self, timeline):
        waypoints = []
        for constraint in self._waypoint_generator.get_waypoint_constraints_gen(self.sim, self.waypoint_count):
            goals = self._get_goals_for_constraint(constraint)
            if not goals:
                continue
            waypoints.append(goals)
        if not waypoints:
            return False
            yield
        if self.staging:
            for route_waypoints in itertools.cycle(self.waypoint_stitching(waypoints, self._waypoint_generator.loops)):
                result = yield from self._do_route_to_constraint_gen(route_waypoints, timeline)
                if not result:
                    return result
                    yield
            else:
                return result
                yield
        else:
            for route_waypoints in self.waypoint_stitching(waypoints, self._waypoint_generator.loops):
                result = yield from self._do_route_to_constraint_gen(route_waypoints, timeline)
            return result
            yield
        return True
        yield

    def _do_route_to_constraint_gen(self, waypoints, timeline):
        if self.is_finishing:
            return False
            yield
        all_sims = self.required_sims()
        if not all_sims:
            return
        goal_size = max(sim.get_routing_context().agent_goal_radius for sim in all_sims)
        goal_size *= goal_size
        plan_primitives = []
        for (i, sim) in enumerate(all_sims):
            route = routing.Route(sim.routing_location, waypoints[-1], waypoints=waypoints[:-1], routing_context=sim.routing_context)
            plan_primitive = PlanRoute(route, sim)
            result = yield from element_utils.run_child(timeline, plan_primitive)
            if not result:
                return False
                yield
            if not (plan_primitive.path.nodes and plan_primitive.path.nodes.plan_success):
                return False
                yield
            plan_primitives.append(plan_primitive)
            if i == len(all_sims) - 1:
                continue
            for node in plan_primitive.path.nodes:
                position = Vector3(*node.position)
                for goal in itertools.chain.from_iterable(waypoints):
                    if goal.routing_surface_id != node.routing_surface_id:
                        continue
                    dist_sq = (Vector3(*goal.position) - position).magnitude_2d_squared()
                    if dist_sq < goal_size:
                        goal.cost = routing.get_default_obstacle_cost()
        route_primitives = []
        for plan_primitive in plan_primitives:
            sequence = get_route_element_for_path(plan_primitive.sim, plan_primitive.path, interaction=self, force_follow_path=True)
            walkstyle_request = self.waypoint_walk_style(plan_primitive.sim)
            sequence = walkstyle_request(sequence=sequence)
            route_primitives.append(sequence)
        result = yield from element_utils.run_child(timeline, do_all(*route_primitives))
        return result
        yield

    @classmethod
    def get_rallyable_aops_gen(cls, target, context, **kwargs):
        key = 'waypoint_info'
        if key not in kwargs:
            waypoint_generator = cls.waypoint_constraint(context, target)
            kwargs[key] = waypoint_generator
        yield from super().get_rallyable_aops_gen(target, context, rally_constraint=waypoint_generator.get_start_constraint(), **kwargs)
