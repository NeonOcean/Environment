import random
from build_buy import is_location_outside
from interactions.constraints import Circle, Nowhere, SmallAreaConstraint
from placement import FGLSearchFlagsDefaultForSim, FGLSearchFlag
from routing import Location
from routing.waypoints.waypoint_generator import _WaypointGeneratorBase
from sims4.tuning.geometric import TunableDistanceSquared
from sims4.tuning.tunable import TunableRange, Tunable
import placement
import routing
import services
import sims4.log
logger = sims4.log.Logger('WaypointGeneratorPacing', default_owner='rmcord')

class _WaypointGeneratorPacing(_WaypointGeneratorBase):
    FACTORY_TUNABLES = {'object_constraint_radius': TunableRange(description='\n            The radius, in meters, of the generated constraint around the \n            target object where the waypoints will be generated.\n            ', tunable_type=float, default=2, minimum=0), 'waypoint_constraint_radius': TunableRange(description='\n            The radius, in meters, for each generated waypoint inside the \n            object constraint radius for the Sim to route to.\n            ', tunable_type=float, default=1, minimum=0.1), 'waypoint_min_distance': TunableDistanceSquared(description='\n            Minimum distance between the waypoints. We want to space them out\n            as much as possible. If after several tries we still cannot get\n            a waypoint that satisfies this min distance, we pick the furthest. \n            ', default=1), 'outside_only': Tunable(description='\n            If enabled, we will attempt to place a jig outside to find a\n            starting location, then validate all goals in the constraint radius\n            to ensure they are outside. Otherwise, we will route fail.\n            \n            Note: This will generate points on the world routing surface.\n            ', tunable_type=bool, default=False)}
    MAX_WAYPOINT_RANDOM_TRIES = 5

    @classmethod
    def _verify_tuning_callback(cls):
        if cls.object_constraint_radius <= cls.waypoint_min_distance:
            logger.error('Constraint radius is smaller than waypoint minimum. Waypoints will not obey minimum distance for: {}', cls)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._target is None:
            self._start_constraint = Nowhere('No target for _WaypointGeneratorPacing')
            return
        if self.outside_only:
            self._routing_surface = routing.SurfaceIdentifier(services.current_zone_id(), 0, routing.SurfaceType.SURFACETYPE_WORLD)
            starting_location = Location(position=self._target.position, routing_surface=self._routing_surface)
            search_flags = FGLSearchFlagsDefaultForSim | FGLSearchFlag.STAY_OUTSIDE
            fgl_context = placement.FindGoodLocationContext(starting_location, routing_context=self._context.sim.routing_context, additional_avoid_sim_radius=routing.get_default_agent_radius(), max_results=1, max_steps=10, search_flags=search_flags)
            (trans, _) = placement.find_good_location(fgl_context)
            if trans is not None:
                geometry = sims4.geometry.RestrictedPolygon(sims4.geometry.CompoundPolygon(sims4.geometry.Polygon((trans,))), ())
                self._start_constraint = SmallAreaConstraint(geometry=geometry, debug_name='WaypointPacingStartingConstraint', routing_surface=self._routing_surface)
            else:
                self._start_constraint = Nowhere('WaypointGeneratorPacing requires outside, but we failed to find a good location.')
        else:
            self._start_constraint = Circle(self._target.position, self.object_constraint_radius, routing_surface=self._routing_surface, los_reference_point=self._target.position)

    def get_start_constraint(self):
        return self._start_constraint

    def get_waypoint_constraints_gen(self, sim, waypoint_count):
        target_position = self._target.position
        object_radius_constraint = Circle(target_position, self.object_constraint_radius, routing_surface=self._start_constraint.routing_surface, los_reference_point=self._target.position)
        area_goals = []
        handles = object_radius_constraint.get_connectivity_handles(sim)
        for handle in handles:
            area_goals.extend(handle.get_goals(relative_object=self._target))
        area_goals = [goal for goal in area_goals if is_location_outside(goal.location.routing_surface.primary_id, goal.position, goal.location.routing_surface.secondary_id)]
        if not (self.outside_only and area_goals):
            yield Circle(target_position, self.object_constraint_radius, routing_surface=self._start_constraint.routing_surface, los_reference_point=self._target.position)
            return
        min_dist_sq = self.waypoint_min_distance
        current_point = None
        for _ in range(waypoint_count):
            if current_point is None:
                current_point = random.choice(area_goals)
                yield Circle(current_point.position, self.waypoint_constraint_radius, routing_surface=self._start_constraint.routing_surface, los_reference_point=self._target.position)
            farthest_point = None
            farthest_dist = 0
            for _ in range(self.MAX_WAYPOINT_RANDOM_TRIES):
                try_point = random.choice(area_goals)
                try_dist = (try_point.position - current_point.position).magnitude_squared()
                farthest_point = try_point
                break
                if try_dist > min_dist_sq and (farthest_point is None or not farthest_point is not None) or try_dist > farthest_dist:
                    farthest_point = try_point
                    farthest_dist = try_dist
            current_point = farthest_point
            yield Circle(current_point.position, self.waypoint_constraint_radius, routing_surface=self._start_constraint.routing_surface, los_reference_point=self._target.position)
