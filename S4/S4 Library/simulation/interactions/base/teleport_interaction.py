from event_testing.results import TestResult
from interactions.base.super_interaction import SuperInteraction
from interactions.utils.routing import get_fgl_context_for_jig_definition
from objects.terrain import TerrainSuperInteraction
from sims4.tuning.tunable import OptionalTunable, TunableReference, Tunable
from sims4.tuning.tunable_base import GroupNames
import placement
import routing
import services
import sims4.log
import sims4.math
logger = sims4.log.Logger('Teleport')

class TeleportHereInteraction(TerrainSuperInteraction):
    INSTANCE_TUNABLES = {'target_jig': OptionalTunable(description='\n            If enabled, a jig can be tuned to place at the target location of\n            the teleport. If placement fails, the interaction will fail.\n            ', tunable=TunableReference(description='\n                The jig to test the target location against.\n                ', manager=services.definition_manager(), class_restrictions='Jig'), tuning_group=GroupNames.CORE), '_teleporting': Tunable(description='\n            If checked, sim will be instantly be teleported without playing\n             any type of animation.\n             ', tunable_type=bool, default=True)}
    _ignores_spawn_point_footprints = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dest_goals = None

    @classmethod
    def _test(cls, target, context, **kwargs):
        (position, surface) = cls._get_position_and_surface(target, context)
        if position is None or surface is None:
            return TestResult(False, 'Cannot go here without a pick or target.')
        location = routing.Location(position, sims4.math.Quaternion.IDENTITY(), surface)
        if not routing.test_connectivity_permissions_for_handle(routing.connectivity.Handle(location), context.sim.routing_context):
            return TestResult(False, 'Cannot TeleportHere! Unroutable area.')
        return TestResult.TRUE

    def _run_interaction_gen(self, timeline):
        if not self._teleporting:
            return True
            yield
        starting_loc = placement.create_starting_location(transform=self.target.transform, routing_surface=self.target.routing_surface)
        if self.target_jig is not None:
            fgl_context = placement.create_fgl_context_for_object(starting_loc, self.target_jig)
        else:
            fgl_context = placement.create_fgl_context_for_sim(starting_loc, self.sim)
        (position, orientation) = placement.find_good_location(fgl_context)
        if position is None:
            return False
            yield
        end_transform = sims4.math.Transform(position, orientation)
        self.sim.routing_component.on_slot = None
        ending_location = sims4.math.Location(end_transform, self.target.routing_surface)
        self.sim.location = ending_location
        self.sim.refresh_los_constraint()
        return True
        yield

class TeleportInteraction(SuperInteraction):
    _teleporting = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dest_goals = []

    def _run_interaction_gen(self, timeline):
        for goal in self.dest_goals:
            goal_transform = sims4.math.Transform(goal.location.transform.translation, self.sim.location.transform.orientation)
            goal_surface = goal.routing_surface_id
            goal_location = sims4.math.Location(goal_transform, goal_surface)
            self.sim.set_location(goal_location)
            break
        result = yield from super()._run_interaction_gen(timeline)
        return result
        yield
