from objects.components.needs_state_value import NeedsStateValue
from sims4.tuning.tunable import AutoFactoryInit, HasTunableFactory, TunableRange, OptionalTunable, TunableReference, TunableList
import services
import sims4.resources

class PlayEffectState(HasTunableFactory, AutoFactoryInit, NeedsStateValue):
    FACTORY_TUNABLES = {'state_index': TunableRange(description='\n            The index of the state to apply to the VFX activated by the state\n            that is also activating this state change. This is defined in the\n            Swarm file.\n            ', tunable_type=int, minimum=0, default=0), 'state_owning_vfx': OptionalTunable(description='\n            Specify which client states the VFX that we care about are owned by.\n            ', tunable=TunableList(description='\n                Specify specific state(s) that own VFX.\n                ', tunable=TunableReference(description='\n                    The client state(s) owning the VFX we want to modify.\n                    ', manager=services.get_instance_manager(sims4.resources.Types.OBJECT_STATE), class_restrictions='ObjectState', pack_safe=True)), enabled_name='Use_Specific_State', disabled_name='Use_Current_State')}

    def __init__(self, target, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._target = target

    def start(self):
        states_owning_vfx = (self.state_value.state,) if self.state_owning_vfx is None else self.state_owning_vfx
        for state_owning_vfx in states_owning_vfx:
            vfx_distributable = self.distributable_manager.get_distributable('vfx_state', state_owning_vfx)
            if vfx_distributable is not None:
                vfx_distributable.set_state_index(self.state_index)

    def stop(self, **kwargs):
        pass
