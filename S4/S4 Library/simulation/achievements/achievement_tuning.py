from distributor.shared_messages import IconInfoData
from event_testing.milestone import Milestone
from event_testing.resolver import SingleSimResolver
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import OptionalTunable
from ui.ui_dialog import UiDialogResponse
from ui.ui_dialog_notification import UiDialogNotification
import services
import sims4.localization
import sims4.log
import sims4.tuning.tunable
import ui.screen_slam
logger = sims4.log.Logger('AchievementTuning')

class Achievement(Milestone, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.ACHIEVEMENT)):
    INSTANCE_TUNABLES = {'display_name': sims4.localization.TunableLocalizedString(description='Display name for this achievement', export_modes=sims4.tuning.tunable_base.ExportModes.All), 'descriptive_text': sims4.localization.TunableLocalizedString(description='Description for this achievement', export_modes=sims4.tuning.tunable_base.ExportModes.All), 'point_value': sims4.tuning.tunable.Tunable(int, 1, description='Point value for an achievement.', export_modes=sims4.tuning.tunable_base.ExportModes.All), 'pid': sims4.tuning.tunable.TunableRange(description='\n                                                  PID for an achievement.\n                                                  ', tunable_type=int, default=0, minimum=0, maximum=127, export_modes=sims4.tuning.tunable_base.ExportModes.ClientBinary), 'xid': sims4.tuning.tunable.Tunable(description='\n            XID for an achievement.\n            ', tunable_type=str, default='', allow_empty=True, export_modes=sims4.tuning.tunable_base.ExportModes.ClientBinary), 'reward': sims4.tuning.tunable.TunableReference(manager=services.get_instance_manager(sims4.resources.Types.REWARD), allow_none=True, description='Which rewards are given when this achievement is completed.', export_modes=sims4.tuning.tunable_base.ExportModes.All), 'category': sims4.tuning.tunable.TunableList(sims4.tuning.tunable.TunableReference(manager=services.get_instance_manager(sims4.resources.Types.ACHIEVEMENT_CATEGORY), description='One of the categories associated with this achievement.'), export_modes=sims4.tuning.tunable_base.ExportModes.All), 'is_hidden': sims4.tuning.tunable.Tunable(bool, False, description='This Achievement is hidden from the player until achieved.', export_modes=sims4.tuning.tunable_base.ExportModes.All), 'icon': sims4.tuning.tunable.TunableResourceKey(None, resource_types=sims4.resources.CompoundTypes.IMAGE, description='\n            The icon to be displayed in the panel view.\n            ', export_modes=sims4.tuning.tunable_base.ExportModes.All), 'screen_slam': OptionalTunable(description='\n            Which screen slam to show when this achievement is completed.  \n            Localization Tokens: Achievement Name = {0.String}\n            ', tunable=ui.screen_slam.TunableScreenSlamSnippet()), 'notification': OptionalTunable(description='\n            If enabled, this notification will show when the achievement is\n            completed.\n            ', tunable=UiDialogNotification.TunableFactory(locked_args={'title': None, 'text': None, 'icon': None, 'primary_icon_response': UiDialogResponse(text=None, ui_request=UiDialogResponse.UiDialogUiRequest.SHOW_ACHIEVEMENTS)}))}

    @classmethod
    def handle_event(cls, sim_info, event, resolver):
        if sim_info is not None and sim_info.account is not None:
            sim_info.account.achievement_tracker.handle_event(cls, event, resolver)

    @classmethod
    def register_callbacks(cls):
        tests = [objective.objective_test for objective in cls.objectives]
        services.get_event_manager().register_tests(cls, tests)

    @classmethod
    def show_achievement_notification(cls, sim_info):
        if cls.notification is not None:
            dialog = cls.notification(sim_info, SingleSimResolver(sim_info), title=lambda *_, **__: cls.display_name, text=lambda *_, **__: cls.descriptive_text)
            dialog.show_dialog(icon_override=IconInfoData(icon_resource=cls.icon), event_id=cls.guid64)

class AchievementCat(metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.ACHIEVEMENT_CATEGORY)):
    INSTANCE_TUNABLES = {'display_text': sims4.localization.TunableLocalizedString(description='Text used to show the Achievement Category name in the UI', export_modes=sims4.tuning.tunable_base.ExportModes.All), 'sorting_order': sims4.tuning.tunable.Tunable(description='\n            The priority sort order for this field to appear in the UI.', tunable_type=int, default=0, export_modes=sims4.tuning.tunable_base.ExportModes.All)}

class AchievementCollection(metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.ACHIEVEMENT_COLLECTION)):
    INSTANCE_TUNABLES = {'display_text': sims4.localization.TunableLocalizedString(description='Text used to describe the achievement reward set', export_modes=sims4.tuning.tunable_base.ExportModes.All)}
