from aspirations.aspiration_types import AspriationType
from event_testing import objective_tuning
from event_testing.milestone import Milestone
from event_testing.resolver import SingleSimResolver, GlobalResolver
from interactions.utils.display_mixin import get_display_mixin
from interactions.utils.loot import LootActions
from traits.traits import Trait
from sims import genealogy_tracker
from sims4.tuning.instances import HashedTunedInstanceMetaclass, lock_instance_tunables
from sims4.tuning.tunable import TunableEnumEntry, TunableSet, OptionalTunable, TunableReference
from sims4.tuning.tunable_base import GroupNames, SourceQueries
from sims4.utils import classproperty, constproperty
from singletons import DEFAULT
from ui.ui_dialog import UiDialogResponse
from ui.ui_dialog_notification import UiDialogNotification
import enum
import server.online_tests
import services
import sims4.localization
import sims4.log
import sims4.tuning.tunable
import ui.screen_slam
logger = sims4.log.Logger('AspirationTuning')

class AspirationBasic(Milestone, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.ASPIRATION)):
    INSTANCE_SUBCLASSES_ONLY = True
    INSTANCE_TUNABLES = {'complete_only_in_sequence': sims4.tuning.tunable.Tunable(description='\n            Aspirations that will only start progress if all previous track aspirations are complete.', tunable_type=bool, default=False), 'screen_slam': OptionalTunable(description='\n            Which screen slam to show when this aspiration is complete.\n            Localization Tokens: Sim - {0.SimFirstName}, Milestone Name - \n            {1.String}, Aspiration Track Name - {2.String}\n            ', tunable=ui.screen_slam.TunableScreenSlamSnippet())}

    @classmethod
    def handle_event(cls, sim_info, event, resolver):
        if sim_info is not None and sim_info.aspiration_tracker is not None:
            sim_info.aspiration_tracker.handle_event(cls, event, resolver)

    @constproperty
    def aspiration_type():
        return AspriationType.BASIC

    @classmethod
    def register_callbacks(cls):
        tests = [objective.objective_test for objective in cls.objectives]
        services.get_event_manager().register_tests(cls, tests)

    @classmethod
    def setup_aspiration(cls, event_data_tracker):
        for objective in cls.objectives:
            objective.setup_objective(event_data_tracker, cls)

    @classmethod
    def cleanup_aspiration(cls, event_data_tracker):
        for objective in cls.objectives:
            objective.cleanup_objective(event_data_tracker, cls)

    @classmethod
    def unregister_callbacks(cls):
        tests = [objective.objective_test for objective in cls.objectives]
        services.get_event_manager().unregister_tests(cls, tests)

    @classmethod
    def apply_on_complete_loot_actions(cls, sim_info):
        pass

    @constproperty
    def update_on_load():
        return True

class Aspiration(AspirationBasic):
    INSTANCE_TUNABLES = {'display_name': sims4.localization.TunableLocalizedString(description='\n            Display name for this aspiration\n            ', allow_none=True, export_modes=sims4.tuning.tunable_base.ExportModes.All), 'descriptive_text': sims4.localization.TunableLocalizedString(description='\n            Description for this aspiration\n            ', allow_none=True, export_modes=sims4.tuning.tunable_base.ExportModes.All), 'is_child_aspiration': sims4.tuning.tunable.Tunable(description='\n            Child aspirations are only possible to complete as a child.\n            ', tunable_type=bool, default=False, export_modes=sims4.tuning.tunable_base.ExportModes.All), 'reward': sims4.tuning.tunable.TunableReference(description='\n            Which rewards are given when this aspiration is completed.\n            ', manager=services.get_instance_manager(sims4.resources.Types.REWARD), allow_none=True), 'on_complete_loot_actions': sims4.tuning.tunable.TunableList(description='\n           List of loots operations that will be awarded when \n           this aspiration complete.\n           ', tunable=LootActions.TunableReference())}

    @constproperty
    def aspiration_type():
        return AspriationType.FULL_ASPIRATION

    @classmethod
    def _verify_tuning_callback(cls):
        for objective in cls.objectives:
            pass
        logger.debug('Loading asset: {0}', cls)

    @classmethod
    def apply_on_complete_loot_actions(cls, sim_info):
        resolver = SingleSimResolver(sim_info)
        for loot_action in cls.on_complete_loot_actions:
            loot_action.apply_to_resolver(resolver)

class AspirationSimInfoPanel(AspirationBasic):
    INSTANCE_TUNABLES = {'display_name': sims4.localization.TunableLocalizedString(description='\n            Display name for this aspiration.\n            ', allow_none=True, export_modes=sims4.tuning.tunable_base.ExportModes.All), 'descriptive_text': sims4.localization.TunableLocalizedString(description='\n            Description for this aspiration.\n            ', allow_none=True, export_modes=sims4.tuning.tunable_base.ExportModes.All), 'category': sims4.tuning.tunable.TunableReference(description='\n            The category this aspiration track goes into when displayed in the\n            UI.\n            ', manager=services.get_instance_manager(sims4.resources.Types.ASPIRATION_CATEGORY), export_modes=sims4.tuning.tunable_base.ExportModes.All)}

    @constproperty
    def aspiration_type():
        return AspriationType.SIM_INFO_PANEL

    @classmethod
    def _verify_tuning_callback(cls):
        for objective in cls.objectives:
            pass

lock_instance_tunables(AspirationSimInfoPanel, complete_only_in_sequence=False)

class AspirationNotification(AspirationBasic):
    INSTANCE_TUNABLES = {'objectives': sims4.tuning.tunable.TunableList(description='\n            A Set of objectives for completing an aspiration.', tunable=sims4.tuning.tunable.TunableReference(description='\n                One objective for an aspiration', manager=services.get_instance_manager(sims4.resources.Types.OBJECTIVE))), 'notification': UiDialogNotification.TunableFactory(description='\n            This text will display in a notification pop up when completed.\n            ')}

    @constproperty
    def aspiration_type():
        return AspriationType.NOTIFICATION

lock_instance_tunables(AspirationNotification, complete_only_in_sequence=False)
AspirationCareerDisplayMixin = get_display_mixin(use_string_tokens=True, has_description=True, has_icon=True, has_tooltip=True)

class AspirationCareer(AspirationCareerDisplayMixin, AspirationBasic):

    def reward(self, *args, **kwargs):
        pass

    @constproperty
    def aspiration_type():
        return AspriationType.CAREER

    @classmethod
    def _verify_tuning_callback(cls):
        for objective in cls.objectives:
            pass

lock_instance_tunables(AspirationCareer, complete_only_in_sequence=True)

class AspirationAssignment(AspirationBasic):

    def reward(self, *args, **kwargs):
        pass

    @classmethod
    def satisfy_assignment(cls, sim_info):
        current_career = sim_info.career_tracker.get_on_assignment_career()
        if current_career is None:
            return
        if cls not in current_career.active_assignments:
            return
        current_career.handle_assignment_loot()

    @classmethod
    def send_assignment_update(cls, sim_info):
        current_career = sim_info.career_tracker.get_on_assignment_career()
        if current_career is None:
            return
        if cls not in current_career.active_assignments:
            return
        current_career.resend_at_work_info()
        current_career.send_assignment_update()

    @constproperty
    def aspiration_type():
        return AspriationType.ASSIGNMENT

    @classmethod
    def _verify_tuning_callback(cls):
        for objective in cls.objectives:
            pass

lock_instance_tunables(AspirationAssignment, complete_only_in_sequence=True)

class AspirationFamilialTrigger(AspirationBasic):
    INSTANCE_TUNABLES = {'objectives': sims4.tuning.tunable.TunableList(description='\n            A Set of objectives for completing an aspiration.', tunable=sims4.tuning.tunable.TunableReference(description='\n                One objective for an aspiration', manager=services.get_instance_manager(sims4.resources.Types.OBJECTIVE))), 'target_family_relationships': TunableSet(description='\n            These relations will get an event message upon Aspiration completion that they can test for.', tunable=TunableEnumEntry(genealogy_tracker.FamilyRelationshipIndex, genealogy_tracker.FamilyRelationshipIndex.FATHER))}

    @constproperty
    def aspiration_type():
        return AspriationType.FAMILIAL

    @classmethod
    def _verify_tuning_callback(cls):
        for objective in cls.objectives:
            pass

lock_instance_tunables(AspirationFamilialTrigger, complete_only_in_sequence=False)

class AspirationCategory(metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.ASPIRATION_CATEGORY)):
    INSTANCE_TUNABLES = {'display_text': sims4.localization.TunableLocalizedString(description='Text used to show the Aspiration Category name in the UI', export_modes=sims4.tuning.tunable_base.ExportModes.All), 'ui_sort_order': sims4.tuning.tunable.Tunable(description='\n            Order in which this category is sorted against other categories in the UI.\n            If two categories share the same sort order, undefined behavior will insue.\n            ', tunable_type=int, default=0, export_modes=sims4.tuning.tunable_base.ExportModes.All), 'icon': sims4.tuning.tunable.TunableResourceKey(None, resource_types=sims4.resources.CompoundTypes.IMAGE, description='\n            The icon to be displayed in the panel view.\n            ', allow_none=True, export_modes=sims4.tuning.tunable_base.ExportModes.All, tuning_group=GroupNames.UI), 'is_sim_info_panel': sims4.tuning.tunable.Tunable(description='\n            Checking this box will mark this category for the Sim Info Panel, not the Aspirations panel.', tunable_type=bool, default=False, export_modes=sims4.tuning.tunable_base.ExportModes.All), 'used_by_packs': sims4.tuning.tunable.TunableEnumSet(description='\n            Optional set of packs which utilize this category.  Used for excluding\n            categories from the UI if their tuning resides in base game.\n            (It is preferred to place category tuning in the appropriate pack, if possible.)\n            ', enum_type=sims4.common.Pack, enum_default=sims4.common.Pack.BASE_GAME, export_modes=sims4.tuning.tunable_base.ExportModes.ClientBinary)}

class AspirationTrackLevels(enum.Int):
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    LEVEL_5 = 5
    LEVEL_6 = 6

TRACK_LEVEL_MAX = 6

class TunableHiddenTrackTestVariant(sims4.tuning.tunable.TunableVariant):

    def __init__(self, description='A tunable test supporting hidden aspiration testing', **kwargs):
        super().__init__(is_live_event_active=server.online_tests.IsLiveEventActive.TunableFactory(), description=description, **kwargs)

class AspirationTrack(metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.ASPIRATION_TRACK)):
    INSTANCE_TUNABLES = {'display_text': sims4.localization.TunableLocalizedString(description='\n            Text used to show the Aspiration Track name in the UI', export_modes=sims4.tuning.tunable_base.ExportModes.All), 'description_text': sims4.localization.TunableLocalizedString(description='\n            Text used to show the Aspiration Track description in the UI', export_modes=sims4.tuning.tunable_base.ExportModes.All), 'icon': sims4.tuning.tunable.TunableResourceKey(None, resource_types=sims4.resources.CompoundTypes.IMAGE, description='\n            The icon to be displayed in the panel view.\n            ', export_modes=sims4.tuning.tunable_base.ExportModes.All, tuning_group=GroupNames.UI), 'icon_high_res': sims4.tuning.tunable.TunableResourceKey(None, resource_types=sims4.resources.CompoundTypes.IMAGE, description='\n            The icon to be displayed in aspiration track selection.\n            ', allow_none=True, export_modes=sims4.tuning.tunable_base.ExportModes.All, tuning_group=GroupNames.UI), 'category': sims4.tuning.tunable.TunableReference(description='\n            The category this aspiration track goes into when displayed in the UI.', manager=services.get_instance_manager(sims4.resources.Types.ASPIRATION_CATEGORY), export_modes=sims4.tuning.tunable_base.ExportModes.All), 'primary_trait': sims4.tuning.tunable.TunableReference(description='\n            This is the primary Aspiration reward trait that is applied upon selection from CAS.', manager=services.get_instance_manager(sims4.resources.Types.TRAIT), export_modes=sims4.tuning.tunable_base.ExportModes.All, allow_none=True), 'aspirations': sims4.tuning.tunable.TunableMapping(description='\n            A Set of objectives for completing an aspiration.', key_type=TunableEnumEntry(AspirationTrackLevels, AspirationTrackLevels.LEVEL_1), value_type=sims4.tuning.tunable.TunableReference(description='\n                One aspiration in the track, associated for a level', manager=services.get_instance_manager(sims4.resources.Types.ASPIRATION), class_restrictions='Aspiration', reload_dependent=True), tuple_name='AspirationsMappingTuple', minlength=1, export_modes=sims4.tuning.tunable_base.ExportModes.All), 'reward': sims4.tuning.tunable.TunableReference(description='\n            Which rewards are given when this aspiration track is completed.', manager=services.get_instance_manager(sims4.resources.Types.REWARD), export_modes=sims4.tuning.tunable_base.ExportModes.All), 'notification': UiDialogNotification.TunableFactory(description='\n            This text will display in a notification pop up when completed.\n            ', locked_args={'text_tokens': DEFAULT, 'icon': None, 'primary_icon_response': UiDialogResponse(text=None, ui_request=UiDialogResponse.UiDialogUiRequest.SHOW_ASPIRATION_SELECTOR), 'secondary_icon': None}), 'mood_asm_param': sims4.tuning.tunable.Tunable(description="\n            The asm parameter for Sim's mood for use with CAS ASM state machine, driven by selection\n            of this AspirationTrack, i.e. when a player selects the a romantic aspiration track, the Flirty\n            ASM is given to the state machine to play. The name tuned here must match the animation\n            state name parameter expected in Swing.", tunable_type=str, default=None, source_query=SourceQueries.SwingEnumNamePattern.format('mood'), export_modes=sims4.tuning.tunable_base.ExportModes.All), 'is_hidden_unlockable': sims4.tuning.tunable.Tunable(description='\n            If True, this track will be initially hidden until unlocked\n            during gameplay.\n            Note: It will never be able to be selected in CAS, even\n            if it has been unlocked.', tunable_type=bool, default=False, export_modes=sims4.tuning.tunable_base.ExportModes.All), 'override_traits': sims4.tuning.tunable.TunableSet(description='\n            Traits that are applied to the sim when they select this aspiration. Overrides any\n            traits that are on the sim when the aspiration is selected. This is used for FTUE\n            aspirations.\n            ', tunable=Trait.TunableReference(pack_safe=True), export_modes=sims4.tuning.tunable_base.ExportModes.All), 'whim_set': OptionalTunable(description='\n            If enabled then this aspiration track will give a whim set when\n            it is active.\n            ', tunable=TunableReference(description='\n                A whim set that is active when this aspiration track is active.\n                ', manager=services.get_instance_manager(sims4.resources.Types.ASPIRATION), class_restrictions=('ObjectivelessWhimSet',))), 'is_hidden_unlocked_tests': sims4.tuning.tunable.TunableList(description='\n            All tests must pass for this track to remain\n            unlocked on load.  This does NOT unlock it.\n            \n            Uses GlobalResolver\n            ', tunable=TunableHiddenTrackTestVariant())}
    _sorted_aspirations = None

    @classmethod
    def get_aspirations(cls):
        return cls._sorted_aspirations

    @classmethod
    def get_next_aspriation(cls, current_aspiration):
        next_aspiration_level = None
        current_aspiration_guid = current_aspiration.guid64
        for (level, track_aspiration) in cls.aspirations.items():
            if track_aspiration.guid64 == current_aspiration_guid:
                next_aspiration_level = int(level) + 1
                break
        if next_aspiration_level in cls.aspirations:
            return cls.aspirations[next_aspiration_level]

    @classmethod
    def is_available(cls):
        if not cls.is_hidden_unlockable:
            return True
        resolver = GlobalResolver()
        for test in cls.is_hidden_unlocked_tests:
            if not resolver(test):
                return False
        return True

    @classproperty
    def is_child_aspiration_track(cls):
        return cls._sorted_aspirations[0][1].is_child_aspiration

    @classmethod
    def _tuning_loaded_callback(cls):
        cls._sorted_aspirations = tuple(sorted(cls.aspirations.items()))

    @classmethod
    def _verify_tuning_callback(cls):
        aspiration_list = cls.aspirations.values()
        aspiration_set = set(aspiration_list)
        if len(aspiration_set) != len(aspiration_list):
            logger.error('{} Aspiration Track has repeating aspiration values in the aspiration map.', cls, owner='ddriscoll')
