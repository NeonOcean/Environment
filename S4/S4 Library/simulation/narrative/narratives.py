from audio.primitive import TunablePlayAudio, play_tunable_audio
from event_testing.resolver import GlobalResolver
from event_testing.tests import TunableTestSet
from narrative.narrative_enums import NarrativeGroup, NarrativeEvent, NarrativeSituationShiftType
from narrative.narrative_environment_support import NarrativeEnvironmentOverride
from sims4.localization import TunableLocalizedString
from sims4.resources import Types
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import HasTunableReference, TunableEnumSet, TunableMapping, TunableEnumEntry, TunableReference, TunableTuple, OptionalTunable, TunableList
from situations.situation_curve import SituationCurve
from ui.ui_dialog import UiDialogOk
from zone_tests import ZoneTest
import event_testing
import services
import sims4.resources

class SituationReplacementTestList(event_testing.tests.TestListLoadingMixin):
    DEFAULT_LIST = event_testing.tests.TestList()

    def __init__(self, description=None):
        if description is None:
            description = 'A list of tests.  All tests must succeed to pass the TestSet.'
        super().__init__(description=description, tunable=ZoneTest.TunableFactory(locked_args={'tooltip': None}))

class Narrative(HasTunableReference, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(Types.NARRATIVE)):
    INSTANCE_TUNABLES = {'narrative_groups': TunableEnumSet(description='\n            A set of narrative groups this narrative is a member of.\n            ', enum_type=NarrativeGroup, enum_default=NarrativeGroup.INVALID, invalid_enums=(NarrativeGroup.INVALID,)), 'narrative_links': TunableMapping(description='\n            A mapping of narrative event to the narrative that will trigger \n            when that narrative event triggers.\n            ', key_type=TunableEnumEntry(description='\n                Event of interest.\n                ', tunable_type=NarrativeEvent, default=NarrativeEvent.INVALID, invalid_enums=(NarrativeEvent.INVALID,)), value_type=TunableReference(description='\n                The narrative the respective event transitions to while\n                this specific narrative is active. \n                ', manager=services.get_instance_manager(Types.NARRATIVE))), 'additional_situation_shifts': TunableMapping(description='\n            A mapping of situation shift type to the shift curve it provides.\n            ', key_type=TunableEnumEntry(description='\n                Shift type.\n                ', tunable_type=NarrativeSituationShiftType, default=NarrativeSituationShiftType.INVALID, invalid_enums=(NarrativeSituationShiftType.INVALID,)), value_type=SituationCurve.TunableFactory(description='\n                The situation schedule this adds to the situation scheduler\n                if this shift type is opted into as an additional source.\n                ', get_create_params={'user_facing': False})), 'situation_replacements': TunableMapping(description='\n            A mapping of situation to a tuple of situation and tests to apply.\n            ', key_type=TunableReference(description='\n                A situation that is available for situation replacement.\n                ', manager=services.get_instance_manager(Types.SITUATION)), value_type=TunableTuple(replacement=TunableReference(description='\n                    A situation that is available for situation replacement.\n                    ', manager=services.get_instance_manager(Types.SITUATION)), replacement_tests=SituationReplacementTestList())), 'environment_override': OptionalTunable(description='\n            If tuned, this narrative can have some effect on world controls\n            such as skyboxes, ambient sounds, and vfx.\n            ', tunable=NarrativeEnvironmentOverride.TunableFactory()), 'introduction': OptionalTunable(description='\n            If enabled, an introduction dialog will be shown on the next zone\n            load (which could be a save/load, travel, switch to another\n            household, etc.) if the test passes.\n            ', tunable=TunableTuple(dialog=UiDialogOk.TunableFactory(description='\n                    The dialog to show that introduces the narrative.\n                    '), tests=TunableTestSet(description='\n                    The test set that must pass for the introduction to be\n                    given. Only the global resolver is available.\n                    Sample use: Must be in a specific region.\n                    '))), 'audio_sting': OptionalTunable(description='\n            If enabled, play the specified audio sting when this narrative starts.\n            ', tunable=TunablePlayAudio()), 'sim_info_loots': OptionalTunable(description='\n            Loots that will be given to all sim_infos when this narrative starts.\n            ', tunable=TunableTuple(loots=TunableList(tunable=TunableReference(manager=services.get_instance_manager(sims4.resources.Types.ACTION), class_restrictions=('LootActions',), pack_safe=True)), save_lock_tooltip=TunableLocalizedString(description='\n                    The tooltip/message to show on the save lock tooltip while\n                    the loots are processing.\n                    ')))}

    def __init__(self):
        self._introduction_shown = False
        self._should_suppress_travel_sting = False

    def save(self, msg):
        msg.narrative_id = self.guid64
        msg.introduction_shown = self._introduction_shown

    def load(self, msg):
        self._introduction_shown = msg.introduction_shown

    def on_zone_load(self):
        self._should_suppress_travel_sting = False
        if self.introduction is not None:
            if not self._introduction_shown:
                resolver = GlobalResolver()
                if self.introduction.tests.run_tests(resolver):
                    dialog = self.introduction.dialog(None, resolver=resolver)
                    dialog.show_dialog()
                    self._introduction_shown = True
                    self._should_suppress_travel_sting = self.introduction.dialog.audio_sting is not None

    @property
    def should_suppress_travel_sting(self):
        return self._should_suppress_travel_sting

    def start(self):
        if self.audio_sting is not None:
            play_tunable_audio(self.audio_sting)
        if self.sim_info_loots is not None:
            services.narrative_service().add_sliced_sim_info_loots(self.sim_info_loots.loots, self.sim_info_loots.save_lock_tooltip)
