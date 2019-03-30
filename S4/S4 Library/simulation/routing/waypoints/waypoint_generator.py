from postures.base_postures import MobilePosture
from postures.posture_graph import get_mobile_posture_constraint
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, OptionalTunable, TunableRange, Tunable

class WaypointContext:

    def __init__(self, obj):
        self._obj = obj

    @property
    def pick(self):
        pass

    @property
    def sim(self):
        return self._obj

class _WaypointGeneratorBase(HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'mobile_posture_override': OptionalTunable(description='\n            If enabled, the mobile posture specified would require the sim to\n            be in this posture to begin the route. This allows us to make the\n            Sim Swim or Ice Skate instead of walk/run.\n            ', tunable=MobilePosture.TunableReference(description='\n                The mobile posture we want to use.\n                ')), '_loops': TunableRange(description='\n            The number of loops we want to perform per route.\n            ', tunable_type=int, default=1, minimum=1), 'use_provided_routing_surface': Tunable(description="\n            If enabled, we will use the target's provided routing surface if it\n            has one.\n            ", tunable_type=bool, default=False)}

    def __init__(self, context, target, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._context = context
        self._target = target if target is not None else context.sim
        provided_routing_surface = self._target.provided_routing_surface
        if provided_routing_surface is not None and self.use_provided_routing_surface:
            self._routing_surface = provided_routing_surface
        else:
            self._routing_surface = self._target.routing_location.routing_surface

    @property
    def loops(self):
        return self._loops

    def get_posture_constraint(self):
        return get_mobile_posture_constraint(posture=self.mobile_posture_override, target=self._target)
