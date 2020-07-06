from objects.components import Component, types, ComponentPriority
from objects.components.state import TunableStateTypeReference, TunableStateValueReference
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, TunableList, TunableReference, Tunable
import services
import sims4.resources
from snippets import define_snippet

class StereoComponent(Component, HasTunableFactory, AutoFactoryInit, component_name=types.STEREO_COMPONENT):
    FACTORY_TUNABLES = {'channel_state': TunableStateTypeReference(description='\n            The state used to populate the radio stations'), 'off_state': TunableStateValueReference(description='\n            The channel that represents the off state.'), 'listen_affordances': TunableList(description='\n            An ordered list of affordances that define "listening" to this\n            stereo. The first succeeding affordance is used.\n            ', tunable=TunableReference(manager=services.get_instance_manager(sims4.resources.Types.INTERACTION), pack_safe=True)), 'play_on_active_sim_only': Tunable(description='\n            If enabled, and audio target is Sim, the audio will only be \n            played on selected Sim. Otherwise it will be played regardless \n            Sim is selected or not.\n            \n            If audio target is Object, always set this to False. Otherwise\n            the audio will never be played.\n            \n            ex. This will be useful for Earbuds where we want to hear the\n            music only when the Sim is selected.\n            \n            This is passed down to the audio state when it is triggered, and thus\n            will overwrite any tuning on the state value.\n            ', tunable_type=bool, default=False), 'immediate': Tunable(description='\n            If checked, this audio will be triggered immediately, nothing\n            will block.\n            \n            ex. Earbuds audio will be played immediately while \n            the Sim is routing or animating.\n            \n            This is passed down to the audio state when it is triggered, and thus\n            will overwrite any tuning on the state value.\n            ', tunable_type=bool, default=False)}

    def is_stereo_turned_on(self):
        current_channel = self.owner.get_state(self.channel_state)
        return current_channel != self.off_state

    def get_available_picker_channel_states(self, context):
        for client_state in self.owner.get_client_states(self.channel_state):
            if client_state.show_in_picker:
                if client_state.test_channel(self.owner, context):
                    yield client_state

    def component_potential_interactions_gen(self, context, **kwargs):
        current_channel = self.owner.get_state(self.channel_state)
        if current_channel != self.off_state:
            for listen_affordance in self.listen_affordances:
                yield from listen_affordance.potential_interactions(self.owner, context, required_station=current_channel, off_state=self.off_state, **kwargs)

(_, TunableStereoComponentSnippet) = define_snippet('stereo_component', StereoComponent.TunableFactory())