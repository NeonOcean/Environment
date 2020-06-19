from _weakrefset import WeakSet
import itertools
from animation.object_animation import ObjectAnimationElement
from balloon.balloon_enums import BALLOON_TYPE_LOOKUP
from balloon.balloon_request import BalloonRequest
from balloon.balloon_variant import BalloonVariant
from balloon.tunable_balloon import TunableBalloon
from event_testing.resolver import SingleObjectResolver, DoubleObjectResolver
from event_testing.tests import TunableTestSet
from interactions.constraint_variants import TunableGeometricConstraintVariant
from interactions.constraints import Circle, Anywhere
from interactions.utils.animation_reference import TunableRoutingSlotConstraint
from interactions.utils.loot import LootActions
from objects.components import types
from objects.object_state_utils import all_objects_gen
from placement import find_good_location
from routing import Goal, SurfaceType, SurfaceIdentifier
from routing.object_routing.object_routing_behavior_actions import ObjectRoutingBehaviorActionAnimation, ObjectRoutingBehaviorActionDestroyObjects, ObjectRoutingBehaviorActionApplyLoot
from routing.waypoints.waypoint_generator import WaypointContext
from routing.waypoints.waypoint_generator_variant import TunableWaypointGeneratorVariant
from routing.waypoints.waypoint_stitching import WaypointStitchingVariant
from sims4 import random
from sims4.math import vector3_almost_equal
from sims4.random import weighted_random_item
from sims4.tuning.geometric import TunableDistanceSquared
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable import OptionalTunable, HasTunableFactory, AutoFactoryInit, Tunable, TunableReference, TunableEnumEntry, TunableList, TunablePercent, TunableVariant, HasTunableSingletonFactory
from sims4.tuning.tunable_base import GroupNames
from tag import TunableTags
import placement
import routing
import services
import sims4.resources
logger = sims4.log.Logger('ObjectRouteVariants', default_owner='miking')

class _ObjectRoutingBehaviorBase(HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'route_fail': OptionalTunable(description='\n            If enabled, show a route failure balloon if the agent is unable to\n            route to the routing slot constraint.\n            ', tunable=BalloonVariant.TunableFactory(), enabled_name='show_balloon')}

    def __init__(self, obj, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._obj = obj
        self._target = None

    def do_route_fail_gen(self, timeline):
        if self.route_fail is None:
            yield
        target = self.get_target()
        if target is None:
            resolver = SingleObjectResolver(self._obj)
        else:
            resolver = DoubleObjectResolver(self._obj, target)
        balloons = self.route_fail.get_balloon_icons(resolver)
        if not balloons:
            yield
        balloon = weighted_random_item(balloons)
        if balloon is None:
            yield
        icon_info = balloon.icon(resolver, balloon_target_override=None)
        if icon_info[0] is None and icon_info[1] is None:
            yield
        category_icon = None
        if balloon.category_icon is not None:
            category_icon = balloon.category_icon(resolver, balloon_target_override=None)
        (balloon_type, priority) = BALLOON_TYPE_LOOKUP[balloon.balloon_type]
        balloon_overlay = balloon.overlay
        request = BalloonRequest(self._obj, icon_info[0], icon_info[1], balloon_overlay, balloon_type, priority, TunableBalloon.BALLOON_DURATION, 0, 0, category_icon)
        request.distribute()

    def get_routes_gen(self):
        raise NotImplementedError

    def get_target(self):
        return self._target

    def get_randomize_orientation(self):
        return False

    def do_target_action_rules_gen(self, timeline):
        return False
        yield

    def on_no_target(self):
        pass

class ObjectRoutingBehaviorFromWaypointGenerator(_ObjectRoutingBehaviorBase):
    FACTORY_TUNABLES = {'waypoint_generator': TunableWaypointGeneratorVariant(tuning_group=GroupNames.ROUTING), 'waypoint_count': Tunable(description='\n            The number of waypoints per loop.\n            ', tunable_type=int, default=10), 'waypoint_stitching': WaypointStitchingVariant(tuning_group=GroupNames.ROUTING), 'return_to_starting_point': OptionalTunable(description='\n            If enabled then the route will return to the starting position\n            within a circle constraint that has a radius of the value tuned\n            here.\n            ', tunable=Tunable(description='\n                The radius of the circle constraint to build to satisfy the\n                return to starting point feature.\n                ', tunable_type=int, default=6), enabled_name='radius_to_return_within'), 'randomize_orientation': Tunable(description='\n            Make Waypoint orientation random.  Default is velocity aligned.\n            ', tunable_type=bool, default=False)}

    def get_routes_gen(self):
        waypoint_generator = self.waypoint_generator(WaypointContext(self._obj), None)
        waypoints = []
        constraints = itertools.chain((waypoint_generator.get_start_constraint(),), waypoint_generator.get_waypoint_constraints_gen(self._obj, self.waypoint_count))
        obj_start_constraint = Circle(self._obj.position, self.return_to_starting_point, routing_surface=self._obj.routing_surface, los_reference_point=None)
        constraints = itertools.chain(constraints, obj_start_constraint)
        for constraint in constraints:
            goals = list(itertools.chain.from_iterable(h.get_goals() for h in constraint.get_connectivity_handles(self._obj)))
            if not goals:
                continue
            for goal in goals:
                goal.orientation = sims4.math.angle_to_yaw_quaternion(random.uniform(0.0, sims4.math.TWO_PI))
            waypoints.append(goals)
        if not (self.return_to_starting_point is not None and waypoints):
            return False
            yield
        routing_context = self._obj.get_routing_context()
        for route_waypoints in self.waypoint_stitching(waypoints, waypoint_generator.loops):
            route = routing.Route(self._obj.routing_location, route_waypoints[-1], waypoints=route_waypoints[:-1], routing_context=routing_context)
            yield route
        return True
        yield

    def get_randomize_orientation(self):
        return self.randomize_orientation

class ObjectRoutingBehaviorFromRoutingSlotConstraint(_ObjectRoutingBehaviorBase):
    _unavailable_objects = WeakSet()
    FACTORY_TUNABLES = {'tags': TunableTags(description='\n            Route to an object matching these tags.\n            ', filter_prefixes=('Func',)), 'constraint': TunableRoutingSlotConstraint(description='\n            Use the point on the found object defined by this animation boundary\n            condition.\n            ', class_restrictions=(ObjectAnimationElement,)), 'route_fail': OptionalTunable(description='\n            If enabled, show a route failure balloon if the agent is unable to\n            route to the routing slot constraint.\n            ', tunable=BalloonVariant.TunableFactory(), enabled_name='show_balloon'), 'parent_relation': Tunable(description="\n            If checked, then this routing behavior is affected by the object's\n            parenting relation:\n             * We'll prefer to route to our previous parent, if it still exists\n             * We'll only route to objects that have no children\n             * We won't route to objects that other objects have picked to route to\n             * We'll stop routing if an object becomes the target's child\n            ", tunable_type=bool, default=False)}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        objects = services.object_manager().get_objects_matching_tags(self.tags)
        if self.parent_relation:
            object_routing_component = self._obj.get_component(types.OBJECT_ROUTING_COMPONENT)
            objects = sorted(objects, key=lambda o: o is not object_routing_component.previous_parent)
        for target in objects:
            if not target.is_connected(self._obj):
                continue
            if self.parent_relation:
                if target.children:
                    continue
                if target in self._unavailable_objects:
                    continue
                target.register_for_on_children_changed_callback(self._on_target_changed)
            target.register_on_location_changed(self._on_target_changed)
            self._target = target
            self._unavailable_objects.add(target)
            break
        else:
            self._target = None

    def _on_target_changed(self, child, *_, **__):
        self._target.unregister_for_on_children_changed_callback(self._on_target_changed)
        self._target.unregister_on_location_changed(self._on_target_changed)
        self._unavailable_objects.discard(self._target)
        if child is not self._obj:
            object_routing_component = self._obj.get_component(types.OBJECT_ROUTING_COMPONENT)
            object_routing_component.restart_running_behavior()

    def get_routes_gen(self):
        if self._target is None:
            return False
            yield
        routing_slot_constraint = self.constraint.create_constraint(self._obj, self._target)
        goals = list(itertools.chain.from_iterable(h.get_goals() for h in routing_slot_constraint.get_connectivity_handles(self._obj)))
        routing_context = self._obj.get_routing_context()
        route = routing.Route(self._obj.routing_location, goals, routing_context=routing_context)
        yield route

class ObjectRouteFromRoutingFormation(_ObjectRoutingBehaviorBase):
    FACTORY_TUNABLES = {'formation_type': TunableReference(description='\n            The formation type to look for on the target. This is the routing\n            formation that we want to satisfy constraints for.\n            ', manager=services.get_instance_manager(sims4.resources.Types.SNIPPET), class_restrictions=('RoutingFormation',))}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        routing_component = self._obj.routing_component
        routing_master = routing_component.routing_master
        if routing_master is not None:
            self._target = routing_master
        else:
            self._target = None

    def get_routes_gen(self):
        if self._target is None:
            return False
            yield
        slave_data = self._target.get_formation_data_for_slave(self._obj)
        if slave_data is None:
            return False
            yield
        starting_location = self._target.intended_location
        transform = slave_data.find_good_location_for_slave(starting_location)
        if transform is None:
            return False
            yield
        goal = Goal(routing.Location(transform.translation, transform.orientation, starting_location.routing_surface))
        routing_context = self._obj.get_routing_context()
        route = routing.Route(self._obj.routing_location, (goal,), routing_context=routing_context)
        yield route

class ObjectRouteFromFGL(_ObjectRoutingBehaviorBase):
    FACTORY_TUNABLES = {'surface_type_override': OptionalTunable(description="\n            If enabled, we will use this surface type instead of the one from\n            the object's location.\n            ", tunable=TunableEnumEntry(description='\n                The surface type we want to force.\n                ', tunable_type=SurfaceType, default=SurfaceType.SURFACETYPE_WORLD, invalid_enums=(SurfaceType.SURFACETYPE_UNKNOWN,)))}

    def get_routes_gen(self):
        routing_surface = self._obj.routing_surface
        routing_surface = SurfaceIdentifier(routing_surface.primary_id, routing_surface.secondary_id, self.surface_type_override)
        starting_location = placement.create_starting_location(transform=self._obj.location.transform, routing_surface=routing_surface)
        fgl_context = placement.create_fgl_context_for_object(starting_location, self._obj)
        (position, orientation) = find_good_location(fgl_context)
        if self.surface_type_override is not None and position is None or orientation is None:
            return False
            yield
        if vector3_almost_equal(position, starting_location.position):
            return True
            yield
        goal = Goal(routing.Location(position, orientation, starting_location.routing_surface))
        routing_context = self._obj.get_routing_context()
        route = routing.Route(self._obj.routing_location, (goal,), routing_context=routing_context)
        yield route

class _TargetActionRules(HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'chance': TunablePercent(description='\n            A random chance of this action getting applied (default 100%).\n            ', default=100), 'test': TunableTestSet(description='\n            A test to decide whether or not to apply this particular set of actions to the target object.\n            ', tuning_group=GroupNames.TESTS), 'actions': TunableList(description='\n            A list of one or more ObjectRoutingBehaviorActions to run on the\n            target object after routing to it. These are applied in sequence.\n            ', tunable=TunableVariant(play_animation=ObjectRoutingBehaviorActionAnimation.TunableFactory(), destroy_objects=ObjectRoutingBehaviorActionDestroyObjects.TunableFactory(), apply_loot=ObjectRoutingBehaviorActionApplyLoot.TunableFactory(), default='play_animation')), 'abort_if_applied': Tunable(description="\n            Don't run any further actions from this list of action rules if \n            conditions are met and this action is executed.\n            ", tunable_type=bool, default=False)}

class _RouteTargetType(HasTunableSingletonFactory, AutoFactoryInit):

    def get_objects(self):
        raise NotImplementedError

class _RouteTargetTypeObject(_RouteTargetType):
    FACTORY_TUNABLES = {'tags': TunableTags(description='\n            Tags used to pre-filter the list of potential targets.\n            If any of the tags match the object will be considered.\n            ', filter_prefixes=('Func',))}

    def get_objects(self):
        if self.tags:
            return services.object_manager().get_objects_matching_tags(self.tags, match_any=True)
        else:
            return services.object_manager().get_valid_objects_gen()

class _RouteTargetTypeSim(_RouteTargetType):
    FACTORY_TUNABLES = {}

    def get_objects(self):
        return services.sim_info_manager().instanced_sims_gen()

class ObjectRouteFromTargetObject(_ObjectRoutingBehaviorBase):
    FACTORY_TUNABLES = {'radius': TunableDistanceSquared(description='\n            Only objects within this distance are considered.\n            ', default=1), 'target_type': TunableVariant(description='\n            Type of target object to choose (object, sim).\n            ', object=_RouteTargetTypeObject.TunableFactory(), sim=_RouteTargetTypeSim.TunableFactory(), default='object'), 'target_selection_test': TunableTestSet(description='\n            A test used for selecting a target.\n            ', tuning_group=GroupNames.TESTS), 'no_target_loot': TunableList(description="\n            Loot to apply if no target is selected (eg, change state back to 'wander').\n            ", tunable=LootActions.TunableReference()), 'constraints': TunableList(description='\n            Constraints relative to the relative participant.\n            ', tunable=TunableGeometricConstraintVariant(description='\n                Use the point on the found object defined by these geometric constraints.\n                ', disabled_constraints=('spawn_points', 'spawn_points_with_backup'))), 'target_action_rules': TunableList(description='\n            A set of conditions and a list of one or more TargetObjectActions to run\n             on the target object after routing to it. These are applied in sequence.\n            ', tunable=_TargetActionRules.TunableFactory())}

    @classmethod
    def _verify_tuning_callback(cls):
        if not cls.target_selection_test and not cls.tags:
            logger.error('No selection test tuned for ObjectRouteFromTargetObject {}.', cls, owner='miking')

    def _find_target(self):
        all_objects = self.target_type.get_objects()
        objects = []
        for o in all_objects:
            dist_sq = (o.position - self._obj.position).magnitude_squared()
            if dist_sq > self.radius:
                continue
            if o == self:
                continue
            if not o.is_sim and not o.may_reserve(self._obj):
                continue
            if self.target_selection_test:
                resolver = DoubleObjectResolver(self._obj, o)
                if not self.target_selection_test.run_tests(resolver):
                    continue
            else:
                objects.append([o, dist_sq])
        if not objects:
            return
        source_handles = [routing.connectivity.Handle(self._obj.position, self._obj.routing_surface)]
        dest_handles = []
        for o in objects:
            obj = o[0]
            parent = obj.parent
            route_to_obj = parent if parent is not None else obj
            constraint = Anywhere()
            for tuned_constraint in self.constraints:
                constraint = constraint.intersect(tuned_constraint.create_constraint(self._obj, route_to_obj))
            dests = constraint.get_connectivity_handles(self._obj, target=obj)
            if dests:
                dest_handles.extend(dests)
        if not dest_handles:
            return
        routing_context = self._obj.get_routing_context()
        connections = routing.estimate_path_batch(source_handles, dest_handles, routing_context=routing_context)
        if not connections:
            return
        connections.sort(key=lambda connection: connection[2])
        best_connection = connections[0]
        best_dest_handle = best_connection[1]
        best_obj = best_dest_handle.target
        return best_obj

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._target = self._find_target()

    def get_routes_gen(self):
        if self._target is None:
            self.on_no_target()
            return False
            yield
        routing_slot_constraint = Anywhere()
        for tuned_constraint in self.constraints:
            routing_slot_constraint = routing_slot_constraint.intersect(tuned_constraint.create_constraint(self._obj, self._target))
        goals = list(itertools.chain.from_iterable(h.get_goals() for h in routing_slot_constraint.get_connectivity_handles(self._obj)))
        routing_context = self._obj.get_routing_context()
        route = routing.Route(self._obj.routing_location, goals, routing_context=routing_context)
        yield route

    def do_target_action_rules_gen(self, timeline):
        if not self.target_action_rules or self._target is None:
            return
        resolver = DoubleObjectResolver(self._obj, self._target)
        for target_action_rule in self.target_action_rules:
            if random.random.random() >= target_action_rule.chance:
                continue
            if not target_action_rule.test.run_tests(resolver):
                continue
            if target_action_rule.actions is not None:
                for action in target_action_rule.actions:
                    result = yield from action.run_action_gen(timeline, self._obj, self._target)
                    if not result:
                        return
            if target_action_rule.abort_if_applied:
                return

    def on_no_target(self):
        resolver = SingleObjectResolver(self._obj)
        for loot_action in self.no_target_loot:
            loot_action.apply_to_resolver(resolver)
