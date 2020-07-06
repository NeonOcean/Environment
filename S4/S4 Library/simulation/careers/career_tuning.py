from protocolbuffers.DistributorOps_pb2 import Operation
import protocolbuffers
from audio.primitive import TunablePlayAudio
from away_actions.away_actions import AwayAction
from buffs.tunable import TunableBuffReference
from caches import cached
from careers import career_ops
from careers.career_enums import CareerCategory, CareerOutfitGenerationType, CareerPanelType, CareerShiftType, get_selector_type_from_career_category, CareerSelectorTypes
from careers.career_location import TunableCareerLocationVariant
from careers.career_scheduler import TunableCareerScheduleVariant, get_career_schedule_for_level
from careers.career_story_progression import CareerStoryProgressionParameters
from distributor.ops import GenericProtocolBufferOp
from distributor.system import Distributor
from event_testing.resolver import SingleSimResolver
from event_testing.test_events import TestEvent
from event_testing.tests import TunableTestSet
from filters.tunable import TunableSimFilter
from interactions import ParticipantType
from interactions.utils.adventure import Adventure
from interactions.utils.loot import LootActions
from interactions.utils.success_chance import SuccessChance
from interactions.utils.tested_variant import TunableTestedVariant
from objects.mixins import SuperAffordanceProviderMixin, TargetSuperAffordanceProviderMixin, MixerProviderMixin, MixerActorMixin
from objects.object_creation import ObjectCreation
from sims.outfits.outfit_generator import TunableOutfitGeneratorReference
from sims.sim_info_types import Age
from sims4.localization import TunableLocalizedStringFactory, TunableLocalizedString
from sims4.math import MAX_UINT64
from sims4.tuning.geometric import TunableCurve
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import TunableTuple, TunableEnumFlags, TunableEnumEntry, OptionalTunable, Tunable, TunableMapping, TunableThreshold, TunableList, TunableReference, TunableRange, HasTunableReference, TunableSimMinute, TunableSet, TunablePercent, HasTunableSingletonFactory, AutoFactoryInit, TunableVariant, TunableRegionDescription, HasTunableFactory, TunablePackSafeReference
from sims4.tuning.tunable_base import GroupNames, ExportModes
from sims4.utils import classproperty
from singletons import DEFAULT
from statistics.commodity import RuntimeCommodity, CommodityTimePassageFixupType
from statistics.runtime_statistic import RuntimeStatistic
from traits.trait_type import TraitType
from tunable_multiplier import TunableMultiplier, TestedSum
from ui.ui_dialog import UiDialogResponse, UiDialogOkCancel, UiDialogOk, UiDialog, PhoneRingType
from ui.ui_dialog_generic import UiDialogTextInputOk, UiDialogTextInputOkCancel
from ui.ui_dialog_notification import UiDialogNotification, TunableUiDialogNotificationSnippet
from venues.venue_constants import NPCSummoningPurpose
import careers.career_base
import event_testing.tests
import interactions.utils.interaction_elements
import scheduler
import services
import sims4.localization
import sims4.resources
import sims4.tuning.tunable
import tunable_time
import ui.screen_slam
logger = sims4.log.Logger('CareerTuning', default_owner='tingyul')

def _get_career_notification_tunable_factory(**kwargs):
    return UiDialogNotification.TunableFactory(locked_args={'text_tokens': DEFAULT, 'icon': None, 'primary_icon_response': UiDialogResponse(text=None, ui_request=UiDialogResponse.UiDialogUiRequest.SHOW_CAREER_PANEL), 'secondary_icon': None}, **kwargs)

class CareerToneTuning(AutoFactoryInit, HasTunableSingletonFactory):
    FACTORY_TUNABLES = {'default_action_list': TunableList(description='\n            List of test to default action. Should any test pass, that will\n            be set as the default action.\n            ', tunable=TunableTuple(default_action_test=OptionalTunable(description='\n                    If enabled, test will be run on the sim. \n                    Otherwise, no test will be run and default_action tuned will\n                    automatically be chosen. There should only be one item, \n                    which is also the default item in the list which has this \n                    disabled.\n                    ', tunable=TunableTestSet(description='\n                        Test to run to figure out what the default away action \n                        should be.\n                        ')), default_action=AwayAction.TunableReference(description='\n                    Default away action tone.\n                    '))), 'optional_actions': TunableSet(description='\n            Additional selectable away action tones.\n            ', tunable=AwayAction.TunableReference(pack_safe=True)), 'leave_work_early': TunableReference(description='\n            Sim Info interaction to end work early.\n            ', manager=services.get_instance_manager(sims4.resources.Types.INTERACTION), class_restrictions='CareerLeaveWorkEarlyInteraction')}

    def get_default_action(self, sim_info):
        resolver = SingleSimResolver(sim_info)
        for default_action_info in self.default_action_list:
            default_test = default_action_info.default_action_test
            if not default_test is None:
                if default_test.run_tests(resolver):
                    return default_action_info.default_action
            return default_action_info.default_action
        logger.error('Failed to find default action for career tone tuning.                       Did you forget to add a default action with no test at                       the end of the list?')

class Career(HasTunableReference, careers.career_base.CareerBase, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.CAREER)):
    HOMEWORK_HELP_MAPPING = TunableMapping(description='\n        Determine how often and how much help a sim receives on their homework.\n        ', key_type=TunableEnumEntry(description='\n            The age at which the homework help data applies.\n            ', tunable_type=Age, default=Age.CHILD), value_type=TunableTuple(description='\n            The homework help data the defines the eligibility, chance\n            and percent of homework completeness to apply when giving\n            homework help.\n            ', eligible_regions=TunableList(description='\n                Regions in which sims who attend school are\n                eligible to get homework help. If none are tuned,\n                all regions are valid.\n                ', tunable=TunableRegionDescription(description='\n                    Regions in which children who attend school are\n                    eligible to get homework help. If none are tuned,\n                    all regions are valid.\n                    ', pack_safe=True)), progress_percentage=TunablePercent(description='\n                The progress percentage that the homework is complete\n                after the student has been given homework help.\n                ', default=50), base_chance=TunablePercent(description='\n                The tunable chance that the sim receives homework help.\n                ', default=50), homework_help_notification=TunableUiDialogNotificationSnippet(description='\n                The notification that will show at the end of the day if a sim\n                receives homework help.\n                ')))
    NUM_CAREERS_PER_DAY = sims4.tuning.tunable.Tunable(int, 2, description='\n                                 The number of careers that are randomly selected\n                                 each day to populate career selection for the\n                                 computer and phone.\n                                 ')
    CAREER_TONE_INTERACTION = TunableReference(description='\n        The interaction that applies the tone away action.\n        ', manager=services.get_instance_manager(sims4.resources.Types.INTERACTION))
    FIND_JOB_PHONE_INTERACTION = sims4.tuning.tunable.TunableReference(description="\n        Find job phone interaction. This will be pushed on a Sim when player\n        presses the Look For Job button on the Sim's career panel.\n        ", manager=services.get_instance_manager(sims4.resources.Types.INTERACTION))
    SWITCH_JOBS_DIALOG = UiDialogOkCancel.TunableFactory(description='\n         If a Sim already has a career and is joining a new one, this dialog\n         asks the player to confirm that they want to quit the existing career.\n         \n         Params passed to Text:\n         {0.SimFirstName} and the like - Sim switching jobs\n         {1.String} - Job title of existing career\n         {2.String} - Career name of existing career\n         {3.String} - Company name of existing career\n         {4.String} - Career name of new career\n         ')
    SWITCH_MANY_JOBS_DIALOG = UiDialogOkCancel.TunableFactory(description='\n         If a Sim already has more than one career and is joining a new one, \n         this dialog asks the player to confirm that they want to quit the existing careers.\n         \n         Params passed to Text:\n         {0.SimFirstName} and the like - Sim switching jobs\n         {1.String} - Job title of existing career\n         {2.String} - Career name of existing career\n         {3.String} - Company name of existing career\n         {4.String} - Career name of new career\n         ')
    UNRETIRE_DIALOG = UiDialogOkCancel.TunableFactory(description='\n         If a Sim is retired and is joining a career, this dialog asks the\n         player to confirm that they want to unretire and lose any retirement\n         benefits.\n         \n         Params passed to Text:\n         {0.SimFirstName} and the like - Sim switching jobs\n         {1.String} - Job title of retired career\n         {2.String} - Career name of retired career\n         {3.String} - Career name of new career\n         ')
    FIRST_TIME_ASSIGNMENT_DIALOG = UiDialogOkCancel.TunableFactory(description='\n         Dialog to offer an immediate assignment to a Sim on accepting a\n         new job. \n         \n         Params passed to Text:\n         {0.SimFirstName} and the like - Sim switching jobs\n         {1.String} - Line separated list of assignment names.\n         ')
    FIRST_TIME_ASSIGNMENT_DIALOG_DELAY = sims4.tuning.tunable.TunableSimMinute(description='\n        The time in Sim Minutes between a Sim accepting\n        a job and getting the first assignment pop-up\n        ', default=3.0, minimum=0.0)
    FIRST_TIME_DEFERRED_ASSIGNMENT_ADDITIONAL_DELAY = sims4.tuning.tunable.TunableInterval(description='\n        A minimum and maximum time between which an additional delay will be\n        randomly chosen. This delay will be added to the normal first time\n        assignment delay. A different value will be chosen for each occurrence.\n        ', tunable_type=sims4.tuning.tunable.TunableSimMinute, default_lower=120, default_upper=720, minimum=0)
    CAREER_PERFORMANCE_UPDATE_INTERVAL = sims4.tuning.tunable.TunableSimMinute(description="\n        In Sim minutes, how often during a work session the Sim's work\n        performance is updated.\n        ", default=30.0, minimum=0.0)
    SCHOLARSHIP_INFO_EVENT = TunableEnumEntry(description='\n        The event to register for when waiting for a Scholarship Info Sign to be shown.\n        ', tunable_type=TestEvent, default=TestEvent.Invalid)
    WORK_SESSION_PERFORMANCE_CHANGE = TunableReference(description="\n        Used to track a sim's work performance change over a work session.\n        ", manager=services.get_instance_manager(sims4.resources.Types.STATISTIC))
    BUFFS_LEAVE_WORK = TunableSet(description='\n        The buffs that are applied when sim left work.\n        ', tunable=TunableBuffReference(pack_safe=True))
    PART_TIME_CAREER_SHIFT_ICONS = TunableMapping(description='\n        Used to populate icons on the shifts dropdown on Career Selector\n        ', key_name='shift_type', key_type=TunableEnumEntry(description='Shift Type.', tunable_type=CareerShiftType, default=CareerShiftType.ALL_DAY), value_name='icon', value_type=sims4.tuning.tunable.TunableResourceKey(None, resource_types=sims4.resources.CompoundTypes.IMAGE, description='The icon to be displayed.'), tuple_name='PartTimeShiftTuningTuple', export_modes=ExportModes.All)
    TEXT_INPUT_NEW_NAME = 'new_name'
    TEXT_INPUT_NEW_DESCRIPTION = 'new_description'
    REGISTER_CAREER_DIALOG_DATA = TunableTuple(register_career_dialog=TunableVariant(description='\n            The rename dialog to show when running this interaction.\n            ', ok_dialog=UiDialogTextInputOk.TunableFactory(text_inputs=(TEXT_INPUT_NEW_NAME, TEXT_INPUT_NEW_DESCRIPTION)), ok_cancel_dialog=UiDialogTextInputOkCancel.TunableFactory(text_inputs=(TEXT_INPUT_NEW_NAME, TEXT_INPUT_NEW_DESCRIPTION))), register_career_rename_title=OptionalTunable(TunableLocalizedStringFactory(description="\n            If set, this localized string will be used as the interaction's \n            display name if the object has been previously renamed.\n            ")))
    CUSTOM_CAREER_KNOWLEDGE_NOTIFICATION = TunableUiDialogNotificationSnippet(description="\n        The notification to use when one Sim learns about another Sim's\n        career. This is only used when the sim has a custom career. \n        Regular career's notification is found in the career track.\n        ")
    CUSTOM_CAREER_REGISTER_LOOT = LootActions.TunableReference(description='\n        Loot to give when sim registers for custom career. This is not tuned\n        directly on interaction because the sim can leave custom career through\n        code for various reasons. The join loot is applied through code to \n        standardize the flow.\n        ')
    CUSTOM_CAREER_UNREGISTER_LOOT = LootActions.TunableReference(description='\n        Loot to give when sim unregisters custom career. This is not tuned\n        directly on interaction because the sim can leave custom career through\n        code for various reasons. \n        ')
    GIG_PICKER_LOCALIZATION_FORMAT = TunableLocalizedStringFactory(description='\n        String used to format the description in the gig picker.\n        Currently has tokens for name, payout range, audition time, gig time\n        and audition prep recommendation.\n        ')
    GIG_PICKER_SKIPPED_AUDITION_LOCALIZATION_FORMAT = TunableLocalizedStringFactory(description='\n        String used to format the description in the gig picker if audition is \n        skipped. Currently has tokens for name, payout range, gig time and \n        audition prep recommendation.\n        ')
    TRAIT_BASED_CAREER_LEVEL_ENTITLEMENTS = TunableList(description='\n        A list of mappings of traits to CareerLevel references. If a sim has\n        a given trait, the associated CareerLevels will become available\n        in the career selector.\n        ', tunable=sims4.tuning.tunable.TunableTuple(trait=sims4.tuning.tunable.TunableReference(description='\n                Trait to test for on the Sim that makes the associated\n                career levels available in the career selector.\n                ', manager=services.get_instance_manager(sims4.resources.Types.TRAIT), pack_safe=True), career_entitlements=sims4.tuning.tunable.TunableList(description='\n                The list of CareerLevels.\n                ', tunable=sims4.tuning.tunable.TunableReference(description='\n                    A CareerLevel.\n                    ', manager=services.get_instance_manager(sims4.resources.Types.CAREER_LEVEL), pack_safe=True)), benefits_description=TunableLocalizedString(description='\n                A description of the benefits granted by the trait to be \n                displayed in the career selector.\n                ')))
    INSTANCE_TUNABLES = {'career_category': TunableEnumEntry(description='\n            Category for career, this will be used for aspirations and other\n            systems which should trigger for careers categories but not for\n            others.\n            ', tunable_type=CareerCategory, default=CareerCategory.Invalid, export_modes=ExportModes.All), 'career_panel_type': TunableEnumEntry(description='\n            Type of panel that UI should use for this career.\n            ', tunable_type=CareerPanelType, default=CareerPanelType.NORMAL_CAREER, export_modes=ExportModes.All, tuning_group=GroupNames.UI), 'career_story_progression': CareerStoryProgressionParameters.TunableFactory(description='\n            Define how Story Progression handles this specific career.\n            '), 'career_location': TunableCareerLocationVariant(description='\n            Define where Sims go to work.\n            ', tuning_group=GroupNames.UI), 'start_track': sims4.tuning.tunable.TunableReference(description='\n                          This is the career track that a Sim would start when joining\n                          this career for the first time. Career Tracks contain a series of\n                          levels you need to progress through to finish it. Career tracks can branch at the end\n                          of a track, to multiple different tracks which is tuned within\n                          the career track tuning.\n                          ', manager=services.get_instance_manager(sims4.resources.Types.CAREER_TRACK), export_modes=sims4.tuning.tunable_base.ExportModes.All), 'career_affordance': sims4.tuning.tunable.TunableReference(manager=services.get_instance_manager(sims4.resources.Types.INTERACTION), description='SI to push to go to work.'), 'go_home_to_work_affordance': TunableReference(description='\n            Interaction pushed onto a Sim to go home and start work from there\n            if they are not on their home lot.\n            ', manager=services.affordance_manager()), 'career_rabbit_hole': TunablePackSafeReference(description='\n            Rabbit hole to put sim in when they are at work.\n            ', manager=services.get_instance_manager(sims4.resources.Types.RABBIT_HOLE), class_restrictions=('CareerRabbitHole',)), 'tested_affordances': TunableList(description="\n            A list of test sets to run to choose the affordance to go work. If \n            an affordance is found from this list, it will be pushed onto the \n            Sim.\n            \n            If no affordance is found from this list that pass the tests, \n            normal work affordance behavior will take over, running \n            'career_affordance' if at home or 'go_home_to_work_affordance' if \n            not at home.\n            ", tunable=TunableTuple(tests=TunableTestSet(description='\n                    A set of tests that if passed will make this the affordance\n                    that is run to send the Sim to work.\n                    '), affordance=TunableReference(description='\n                    The career affordance for this test set. \n                    ', manager=services.get_instance_manager(sims4.resources.Types.INTERACTION)))), 'levels_lost_on_leave': sims4.tuning.tunable.Tunable(int, 1, description='When you leave this career for any reason you will immediately lose this many levels, for rejoining the career. i.e. if you quit your job at level 8, and then rejoined with this value set to 1, you would rejoin the career at level 7.'), 'days_to_level_loss': sims4.tuning.tunable.Tunable(int, 1, description='When you leave a career, we store off the level youwould rejoin the career at. Every days_to_level_loss days you will lose another level. i.e. I quit my job at level 8. I get reducedlevel 7 right away because of levels_lost_on_leave. Then with days_to_level_loss set to 3, in 3 days I would goto level 6, in 6 days level 5, etc...'), 'start_level_modifiers': TestedSum.TunableFactory(description='\n            A tunable list of test sets and associated values to apply to the\n            starting level of this Sim.\n            '), 'promotion_buff': OptionalTunable(description='\n            The buff to trigger when this Sim is promoted in this career.', tunable=TunableBuffReference()), 'demotion_buff': OptionalTunable(description='\n            The buff to trigger when this Sim is demoted in this career.', tunable=TunableBuffReference()), 'fired_buff': OptionalTunable(description='\n            The buff to trigger when this Sim is fired from this career.', tunable=TunableBuffReference()), 'early_promotion_modifiers': TunableMultiplier.TunableFactory(description='\n            A tunable list of test sets and associated multipliers to apply to \n            the moment of promotion. A resulting modifier multiplier of 0.10 means that promotion \n            could happen up to 10% earlier. A value less than 0 has no effect.\n            '), 'early_promotion_chance': TunableMultiplier.TunableFactory(description='\n            A tunable list of test sets and associated multipliers to apply to the percentage chance, \n            should the early promotion modifier deem that early promotion is possible,\n            that a Sim is in fact given a promotion. A resolved value of 0.10 will result in a 10%\n            chance.\n            '), 'demotion_chance_modifiers': TunableMultiplier.TunableFactory(description="\n            A tunable list of test sets and associated multipliers to apply to \n            the moment of a Sim's demotion, to provide the chance that Sim will get demoted. A resultant\n            modifier value of 0.50 means at the point of work end where performance would require demotion,\n            the Sim would have a 50% chance of being demoted. Any resultant value over 1 will result in demotion.\n            "), 'scholarship_info_loot': OptionalTunable(description='\n            If enabled, this loot will run at the beginning of the career si.\n            ', tunable=LootActions.TunablePackSafeReference(description='\n                Loot to trigger at the beginning of the career\n                ', allow_none=True)), 'career_messages': TunableTuple(join_career_notification=OptionalTunable(description='\n                If tuned, we will show a message when a sim joins this career.\n                If not tuned, no message will be shown.\n                ', tunable=_get_career_notification_tunable_factory(description='\n                    Message when a Sim joins a new career.\n                    '), enabled_by_default=True), quit_career_notification=_get_career_notification_tunable_factory(description='\n                Message when a Sim quits a career.\n                '), fire_career_notification=_get_career_notification_tunable_factory(description='\n                Message when a Sim is fired from a career.\n                '), promote_career_notification=_get_career_notification_tunable_factory(description='\n                Message when a Sim is promoted in their career.\n                '), promote_career_rewardless_notification=_get_career_notification_tunable_factory(description="\n                Message when a Sim is promoted in their career and there are no\n                promotion rewards, either because there are none tuned or Sim\n                was demoted from this level in the past and so shouldn't get\n                rewards again.\n                "), demote_career_notification=_get_career_notification_tunable_factory(description='\n                Message when a Sim is demoted in their career.\n                '), career_daily_start_notification=_get_career_notification_tunable_factory(description='\n                Message on notification when sim starts his work day\n                '), career_daily_end_notification=TunableTestedVariant(description='\n                Message on notification when sim ends his work day\n                ', tunable_type=_get_career_notification_tunable_factory(), locked_args={'no_notification': None}), career_event_confirmation_dialog=UiDialogOkCancel.TunableFactory(description='\n                 At the begining of a work day, if the career has available events and\n                 the Sim is eligible to do an event, this dialog is shown. If player\n                 accepts, the Sim is sent to the career event (e.g. hospital, police\n                 station, etc.). If player declines, the Sim goes to rabbit hole to \n                 work.\n                 \n                 Params passed to Text:\n                 {0.SimFirstName} and the like - Sim in career\n                 {1.String} - Job title\n                 {2.String} - Career name\n                 {3.String} - Company name\n                 '), career_time_off_messages=TunableMapping(description='\n                Mapping of time off reason to the messages displayed for that reason\n                ', key_type=TunableEnumEntry(career_ops.CareerTimeOffReason, career_ops.CareerTimeOffReason.NO_TIME_OFF), value_type=TunableTuple(text=TunableLocalizedStringFactory(description='\n                        Localization String for the text displayed on the panel when\n                        taking time off for the specified reason.\n                        \n                        First token: sim info\n                        Second token: PTO days remaining.\n                        ', allow_none=True), tooltip=TunableLocalizedStringFactory(description='\n                        Localization String for the tooltip displayed when\n                        taking time off for the specified reason\n                        \n                        First token: sim info\n                        Second token: PTO days remaining.\n                        ', allow_none=True), day_end_notification=OptionalTunable(description='\n                        If enabled, the notification that will be sent when the\n                        Sim ends his day of PTO.\n                        ', tunable=TunableTestedVariant(description='\n                            Message on notification when sim ends his day of PTO\n                            ', tunable_type=_get_career_notification_tunable_factory())))), career_early_warning_notification=_get_career_notification_tunable_factory(description='\n                Message warning the Sim will need to leave for work soon.\n                '), career_early_warning_time=Tunable(description='\n                How many hours before a the Sim needs to go to work to show\n                the Career Early Warning Notification. If this is <= 0, the\n                notification will not be shown.\n                ', tunable_type=float, default=1), career_early_warning_alarm=OptionalTunable(description='\n                If enabled, provides options to the player to go to work,\n                work from home, or take pto. \n                \n                {0.SimFirstName} Sim in career\n                {1.String} - Career level title\n                {2.String} - Career name\n                {3.String} - Company name\n                ', tunable=TunableTuple(dialog=UiDialog.TunableFactory(description="\n                        Dialog that's shown. Okay is confirming leaving the\n                        situation, cancel is to miss work and stay in the\n                        situation.\n                        ", locked_args={'phone_ring_type': PhoneRingType.ALARM}), go_to_work_text=sims4.localization.TunableLocalizedStringFactory(description='\n                        Button text for choosing to go to work.\n                        '), work_from_home_text=sims4.localization.TunableLocalizedStringFactory(description='\n                        If the Sim has career assignments to offer, a button with\n                        this text will show up.\n                        '), take_pto_text=sims4.localization.TunableLocalizedStringFactory(description='\n                        If the Sim has enough PTO, a button with this text will\n                        show up.\n                        '), call_in_sick_text=sims4.localization.TunableLocalizedStringFactory(description='\n                        If the Sim does not have enough PTO, a button with this\n                        text will show up.\n                        ')), enabled_by_default=True), career_missing_work=OptionalTunable(description='\n                If enabled, being late for work will trigger the missing work flow\n                ', tunable=TunableTuple(description='\n                    Tuning for triggering the missing work flow.\n                    ', dialog=UiDialogOk.TunableFactory(description='\n                        The dialog that will be triggered when the sim misses work.\n                        '), affordance=sims4.tuning.tunable.TunableReference(description='\n                        The affordance that is pushed onto the sim when the accepts\n                        the modal dialog.\n                        ', manager=services.get_instance_manager(sims4.resources.Types.INTERACTION))), enabled_by_default=True), career_performance_warning=TunableTuple(description='\n                Tuning for triggering the career performance warning flow.\n                ', dialog=UiDialogOk.TunableFactory(description='\n                    The dialog that will be triggered when when the sim falls\n                    below their performance threshold.\n                    '), threshold=TunableThreshold(description='\n                    The threshold that the performance stat value will be\n                    compared to.  If the threshold returns true then the\n                    performance warning notification will be triggered.\n                    \n                    '), affordance=sims4.tuning.tunable.TunableReference(description='\n                    The affordance that is pushed onto the sim when the accepts\n                    the modal dialog.\n                    ', manager=services.get_instance_manager(sims4.resources.Types.INTERACTION))), pto_gained_text=sims4.localization.TunableLocalizedStringFactory(description='\n                Text passed to daily end notifications when additional day of \n                PTO is earned.\n                        \n                First token: sim info\n                ', allow_none=True), overmax_rewardless_notification=_get_career_notification_tunable_factory(description='\n                The notification to display when a Sim reaches an overmax level.\n                The following tokens are provided:\n                 * 0: The Sim owner of the career\n                 * 1: The level name (e.g. Chef)\n                 * 2: The career name (e.g. Culinary)\n                 * 3: The company name (e.g. Maids United)\n                 * 4: The overmax level\n                 * 5: The new salary\n                 * 6: The salary increase\n                '), overmax_notification=_get_career_notification_tunable_factory(description='\n                The notification to display when a Sim reaches an overmax level.\n                The following tokens are provided:\n                 * 0: The Sim owner of the career\n                 * 1: The level name (e.g. Chef)\n                 * 2: The career name (e.g. Culinary)\n                 * 3: The company name (e.g. Maids United)\n                 * 4: The overmax level\n                 * 5: The new salary\n                 * 6: The salary increase\n                 * 7: The rewards, in the form of a string\n                '), situation_leave_confirmation=TunableTuple(description='\n                If a playable Sim is in a situation with a job with Confirm\n                Leave Situation For Work set, this dialog will be shown to the\n                player with the options of leaving the situation for work,\n                staying in situation and let Sim miss work, or stay in\n                situation and Sim take PTO.\n                \n                {0.SimFirstName} and the like - Sim in career\n                {1.String} - Job title\n                {2.String} - Career name\n                {3.String} - Company name\n                ', dialog=UiDialogOkCancel.TunableFactory(description="\n                    Dialog that's shown. Okay is confirming leaving the situation,\n                    cancel is to miss work and stay in the situation.\n                    "), take_pto_button_text=sims4.localization.TunableLocalizedStringFactory(description='\n                    If the Sim has enough PTO, a button with this text will show up.\n                    ')), career_event_end_warning=OptionalTunable(description='\n                If enabled, a notification will be displayed if time left is \n                more than time tuned. \n                If disabled, no notification will be displayed.\n                ', tunable=TunableTuple(description="\n                    Tuning for a notification warning the player that their Sim's\n                    active career event is about to end.\n                    ", notification=_get_career_notification_tunable_factory(description='\n                        Notification warning work day is going to end.\n    \n                         Params passed to Text:\n                         {0.SimFirstName} and the like - Sim in career\n                         {1.String} - Job title\n                         {2.String} - Career name\n                         {3.String} - Company name\n                        '), time=TunableSimMinute(description='\n                        How many Sim minutes prior to the end to show notification.\n                        ', default=60, minimum=0))), career_assignment_summary_notification=TunableTestedVariant(description='\n                Message on notification when day starts after having assignment(s).\n                ', tunable_type=_get_career_notification_tunable_factory(), locked_args={'no_notification': None}), tuning_group=GroupNames.UI), 'can_be_fired': sims4.tuning.tunable.Tunable(bool, True, description='Whether or not the Sim can be fired from this career.  For example, children cannot be fired from school.'), 'quittable_data': OptionalTunable(description='\n            Whether or not Sims can quit this career.\n            e.g.: Children/Teens cannot quit School.\n            \n            If the career is quittable, specify tuning directly related to\n            quitting, e.g. the confirmation dialog.\n            ', tunable=TunableTuple(tested_quit_dialog=OptionalTunable(description='\n                    If enabled and the tuned tests pass, instead of showing the default\n                    quit dialog the tested quit dialog will be displayed.\n                    \n                    Example: If a Sim has a scholarship (EP8) that depends on\n                    staying in the career, a tested quit dialog can be tuned to\n                    include a warning in its dialog text.\n                    ', tunable=TunableTuple(quit_dialog=UiDialogOkCancel.TunableFactory(description='\n                            This dialog asks the player to confirm that they want to\n                            quit.\n                            '), test_set=event_testing.tests.TunableTestSet(description='\n                            If the tests pass, the test-dependent-quit-dialog will\n                            show. Otherwise, the default quit-dialog will show.\n                            '))), quit_dialog=UiDialogOkCancel.TunableFactory(description='\n                    This dialog asks the player to confirm that they want to\n                    quit.\n                    ')), enabled_by_default=True, enabled_name='Can_Quit', disabled_name='Cannot_Quit'), 'career_availablity_tests': event_testing.tests.TunableTestSet(description='\n            When a Sim calls to join a Career, this test set determines if a \n            particular career can be available to that Sim at all. This test\n            set determines if a Career is visible in the Career Panel.\n            '), 'career_selectable_tests': event_testing.tests.TunableTestSet(description='\n            Test set that determines if a career that is available to a Sim\n            is valid or not. This test set determines if a Career is selectable\n            in the Career Panel.\n            '), 'show_career_in_join_career_picker': Tunable(description='\n            If checked, this career will be visible in the join career picker\n            window. If not checked, it will not be.\n            ', tunable_type=bool, default=True, tuning_group=GroupNames.UI), 'initial_pto': sims4.tuning.tunable.Tunable(description='\n            Initial amount of PTO earned when joining the career\n            ', tunable_type=float, default=0), 'disable_pto': Tunable(description='\n            If checked, will disable PTO references in the UI. This option is\n            incompatible with setting any pto tuning in the carrer or career \n            levels to non-default values.\n            ', default=False, tunable_type=bool, tuning_group=GroupNames.UI), 'initial_delay': TunableSimMinute(description='\n            The amount of time a Sim is exempt from going to work after being\n            hired. Their first work day will be at least this much into the\n            future.\n            ', default=480.0, minimum=0.0), 'is_active': sims4.tuning.tunable.Tunable(description='\n            Whether this career is considered active. Active careers appear in\n            a separate tab in the Join Career dialog.\n            ', tunable_type=bool, default=False), 'career_events': TunableList(description='\n             A list of available career events.\n             ', tunable=sims4.tuning.tunable.TunableReference(manager=services.get_instance_manager(sims4.resources.Types.CAREER_EVENT))), 'hire_agent_interaction': OptionalTunable(tunable=TunableReference(description='\n                The interaction to push a sim to hire an agent.\n                ', manager=services.affordance_manager()), tuning_group=GroupNames.GIG, export_modes=(ExportModes.ClientBinary,)), 'find_audition_interaction': OptionalTunable(tunable=TunableReference(description='\n                The interaction to push a sim to look for an audition.\n                ', manager=services.affordance_manager()), tuning_group=GroupNames.GIG, export_modes=(ExportModes.ClientBinary,)), 'cancel_audition_interaction': OptionalTunable(tunable=TunableReference(description='\n                The interaction to push on a sim who cancels an audition.\n                ', manager=services.affordance_manager()), tuning_group=GroupNames.GIG, export_modes=(ExportModes.ClientBinary,)), 'cancel_gig_interaction': OptionalTunable(tunable=TunableReference(description='\n                The interaction to push on a sim to cancel a gig.\n                ', manager=services.affordance_manager()), tuning_group=GroupNames.GIG, export_modes=(ExportModes.ClientBinary,)), 'call_costar_interaction': OptionalTunable(tunable=TunableReference(description='\n                The interaction to push a sim to call up their costars. This is added\n                for gigs.\n                ', manager=services.affordance_manager()), tuning_group=GroupNames.GIG, export_modes=(ExportModes.ClientBinary,)), 'invite_over': OptionalTunable(description='\n            Tuning that provides a tunable chance for the Sim in this career\n            inviting over someone at the end of the work/school day. For\n            example, a child Sim can invite over a classmate after school,\n            or an adult can invite over a co-worker after their shift ends.\n            \n            Invite overs will only occur if the player is on the home lot.\n            ', tunable=TunableTuple(chance=SuccessChance.TunableFactory(description='\n                    Chance of inviting over a Sim after work/school.\n                    '), confirmation_dialog=UiDialogOkCancel.TunableFactory(description='\n                    Dialog offered to player to confirm inviting over someone.\n    \n                    Localization Tokens:\n                    0: Sim in career.\n                    1: Sim being invited over.\n                    '), sim_filter=TunableSimFilter.TunableReference(description='\n                    Sim filter specifying who to invite over.\n                    '), purpose=TunableEnumEntry(description='\n                    The purpose for the invite over. This will determine the\n                    behavior of the invited over Sim, as tuned in Venue -> Npc\n                    Summoning Behavior.\n                    ', tunable_type=NPCSummoningPurpose, default=NPCSummoningPurpose.DEFAULT))), 'available_for_club_criteria': Tunable(description='\n            If enabled, this career type will be available for selection when\n            creating Club Criteria. If disabled, it will not be available.\n            ', tunable_type=bool, default=False), 'has_coworkers': Tunable(description='\n            If checked, other Sims in this career are considered coworkers. If\n            unchecked, they are not.\n            \n            e.g.\n             * Sims in High School might should not be considered coworkers.\n            ', tunable_type=bool, default=True), 'display_career_info': Tunable(description='\n            If checked, the full set of career messages are displayed for this\n            career. This includes notifications when the career is joined as\n            well as performance evaluation results.\n            \n            If unchecked, those two sets of data are not made visible to the\n            player, e.g. for school career.\n            ', tunable_type=bool, default=True), 'is_school_career': Tunable(description='\n            If checked, the career will test into special behavior and treated\n            as school for children or teens.\n            \n            If unchecked, this is a professional career.\n            \n            Used to branch behavior at the end of the day for re-setting the career\n            performance statistics for childreen/teens so they may receive\n            homework help.\n            ', tunable_type=bool, default=False), 'aspirations_to_activate': TunableList(description="\n            A list of aspirations we want to activate while the Sim is in this\n            career. This saves from having to track them when the Sim is not in\n            the career.\n            \n            Note: You don't need to tune Aspirations that the Career Level\n            references directly. But if those aspirations rely on others, then\n            they need to be tuned here.\n            ", tunable=sims4.tuning.tunable.TunableReference(description='\n                A Career Aspiration that we want to activate when the Sim is in\n                this career.\n                ', manager=services.get_instance_manager(sims4.resources.Types.ASPIRATION), class_restrictions='AspirationCareer'), unique_entries=True), 'show_ideal_mood': Tunable(description="\n            If checked, displays the current career track's ideal mood in the UI.\n            Does not change whether the ideal mood affects the career performance.\n            ", tunable_type=bool, default=False, tuning_group=GroupNames.UI, export_modes=ExportModes.All), 'is_visible_career': Tunable(description='\n            If checked, this will be considered a professional career.  If \n            unchecked, any career tests that check for a visible, \n            professional career will not take this career into account.  In \n            addition, any unchecked career will not be affected by any Career \n            Loot Ops (because it is invisible).\n            ', tunable_type=bool, default=True), 'early_work_loot': OptionalTunable(description='\n            If enabled, this loot will be applied to the Sim prior to going to\n            work.\n            ', tunable=LootActions.TunablePackSafeReference(description='\n                Loot to apply to the Sim prior to going to work.\n                ', allow_none=True))}
    _days_worked_statistic_type = None
    _active_days_worked_statistic_type = None

    @classmethod
    def _verify_tuning_callback(cls):
        if cls.disable_pto:
            if cls.initial_pto > 0:
                logger.error('Career: {} has disable PTO set but has initial PTO', cls)
            for career_level in cls.start_track.career_levels:
                if career_level.pto_per_day != 0:
                    logger.error('Career: {} has disable PTO set but has nonzero PTO gain in career level {} (zero indexed)', cls, career_level.level)
        if cls.available_for_club_criteria:
            start_track = cls.start_track
            if start_track.career_name._string_id == start_track.career_name_gender_neutral.hash:
                logger.error('Career {} has the same string tuned for its display name and its gender-neutral display name. These must be different strings for localization.', start_track, owner='BadTuning')
        for reason in career_ops.CareerTimeOffReason:
            if reason == career_ops.CareerTimeOffReason.NO_TIME_OFF:
                continue
            if reason not in cls.career_messages.career_time_off_messages:
                logger.error('Career: {} is missing career.career time off messages for reason: {}', cls, reason)

    @classmethod
    def _tuning_loaded_callback(cls):
        cls._create_runtime_commodities()
        cls._propagate_track_and_level_data()

    @classmethod
    def _create_runtime_commodities(cls):
        temp_commodity = RuntimeCommodity.generate(cls.__name__)
        temp_commodity.decay_rate = 0
        temp_commodity.convergence_value = 0
        temp_commodity.remove_on_convergence = False
        temp_commodity.visible = False
        temp_commodity.max_value_tuning = 99
        temp_commodity.min_value_tuning = 0
        temp_commodity.initial_value = cls.initial_pto
        temp_commodity.add_if_not_in_tracker = True
        temp_commodity._time_passage_fixup_type = CommodityTimePassageFixupType.FIXUP_USING_TIME_ELAPSED
        cls._pto_commodity = temp_commodity
        if cls._days_worked_statistic_type is None:
            cls._days_worked_statistic_type = RuntimeStatistic.generate(cls.__name__ + '_DaysWorked')
            cls._active_days_worked_statistic_type = RuntimeStatistic.generate(cls.__name__ + '_ActiveDaysWorked')
            cls.max_value_tuning = MAX_UINT64

    @classmethod
    def _propagate_track_and_level_data(cls):
        tracks = []
        tracks.append((cls.start_track, 1))
        while tracks:
            (track, starting_user_level) = tracks.pop()
            for (index, career_level) in enumerate(track.career_levels):
                if career_level.track is not None:
                    logger.assert_log('Invalid tuning. {} is in multiple career tracks: {}, {}', career_level.__name__, career_level.track.__name__, cls.__name__)
                career_level.career = cls
                career_level.track = track
                career_level.level = index
                career_level.user_level = index + starting_user_level
            branch_user_level = len(track.career_levels) + starting_user_level
            for branch in track.branches:
                if branch.parent_track is not None:
                    logger.error('Invalid tuning. {} has multiple parent tracks: {}, {}', branch.__name__, branch.parent_track.__name__, track.__name__)
                branch.parent_track = track
                tracks.append((branch, branch_user_level))

    @classmethod
    @cached
    def get_max_user_level(cls):
        max_user_level = 0
        stack = [(cls.start_track, 0)]
        while stack:
            (track, level) = stack.pop()
            level += len(track.career_levels)
            if track.branches:
                for branch in track.branches:
                    stack.append((branch, level))
                else:
                    max_user_level = max(max_user_level, level)
            else:
                max_user_level = max(max_user_level, level)
        return max_user_level

    @classproperty
    def allow_multiple_careers(cls):
        return False

    @classproperty
    def pto_commodity(cls):
        return cls._pto_commodity

    @classproperty
    def can_quit(cls):
        return cls.quittable_data is not None

    @staticmethod
    def _append_career_info_pb(msg, sim_info, career, current_track, new_level, benefit_description=None, is_selectable=True):
        if current_track is not None:
            career_track = current_track
        elif career.start_track is not None:
            career_track = career.start_track
        else:
            logger.error('Career {} is unjoinable because it is missing Start Track tuning.', career)
            return
        if new_level < 0 or new_level >= len(career_track.career_levels):
            logger.error('Career {} has an invalid index for career level: new_level={}.', career, new_level)
            return
        career_level = career_track.career_levels[new_level]
        career_info_msg = msg.career_choices.add()
        career_info_msg.uid = career.guid64
        career_info_msg.career_track = career_track.guid64
        career_info_msg.career_level = new_level
        career_info_msg.is_active = career.is_active
        if benefit_description is not None:
            career_info_msg.benefit_description = benefit_description
        career_info_msg.is_selectable = is_selectable
        career_info_msg.hourly_pay = career.get_hourly_pay(sim_info=sim_info, career_track=career_track, career_level=career_level.level, overmax_level=0)
        work_schedule = get_career_schedule_for_level(career_level)
        if work_schedule is not None:
            work_schedule.populate_scheduler_msg(career_info_msg.work_schedule)

    @staticmethod
    def get_join_career_pb(sim_info, num_careers_to_show=0, default_career_selection_data=None):
        msg = protocolbuffers.Sims_pb2.CareerSelectionUI()
        msg.sim_id = sim_info.sim_id
        msg.is_branch_select = False
        msg.reason = career_ops.CareerOps.JOIN_CAREER
        current_shift = CareerShiftType.ALL_DAY
        for sim_career_id in sim_info.career_tracker.careers:
            sim_career = sim_info.career_tracker.get_career_by_uid(sim_career_id)
            if sim_career.schedule_shift_type != CareerShiftType.ALL_DAY:
                current_shift = sim_career.schedule_shift_type
                break
        msg.current_shift = current_shift
        if default_career_selection_data is not None:
            msg.default_career_select_uid = default_career_selection_data.default_career_select
            msg.career_selector_type = default_career_selection_data.career_selector_type
        all_possible_careers = services.get_career_service().get_shuffled_career_list()
        career_tracks_added = []
        career_tracks_to_skip = []
        for entitlement in Career.TRAIT_BASED_CAREER_LEVEL_ENTITLEMENTS:
            if sim_info.trait_tracker.has_trait(entitlement.trait):
                for career_level in entitlement.career_entitlements:
                    test_result = career_level.career.is_career_available(sim_info=sim_info, from_join=True)
                    if test_result and sim_info.career_tracker.get_career_by_uid(career_level.career.guid64) is None and career_level.track not in career_tracks_added:
                        is_selectable_test_result = career_level.career.is_career_selectable(sim_info=sim_info)
                        Career._append_career_info_pb(msg, sim_info, career_level.career, career_level.track, career_level.level, benefit_description=entitlement.benefits_description, is_selectable=is_selectable_test_result.result)
                        career_tracks_added.append(career_level.track)
                    parent_track = career_level.track.parent_track
                    if parent_track is not None:
                        all_child_branches_available = True
                        for child in parent_track.branches:
                            if child not in career_tracks_added:
                                all_child_branches_available = False
                                break
                        if all_child_branches_available:
                            career_tracks_to_skip.append(parent_track)
        for career_tuning in all_possible_careers:
            if 0 < num_careers_to_show <= len(career_tracks_added):
                break
            if not career_tuning.show_career_in_join_career_picker:
                continue
            test_result = career_tuning.is_career_available(sim_info=sim_info, from_join=True)
            if test_result:
                if sim_info.career_tracker.get_career_by_uid(career_tuning.guid64) is None:
                    (new_level, _, current_track) = career_tuning.get_career_entry_level(career_history=sim_info.career_tracker.career_history, resolver=SingleSimResolver(sim_info))
                    if current_track in career_tracks_to_skip:
                        continue
                    is_selectable_test_result = career_tuning.is_career_selectable(sim_info=sim_info)
                    if current_track not in career_tracks_added:
                        Career._append_career_info_pb(msg, sim_info, career_tuning, current_track, new_level, is_selectable=is_selectable_test_result.result)
        return msg

    @staticmethod
    def get_quit_career_pb(sim_info):
        msg = protocolbuffers.Sims_pb2.CareerSelectionUI()
        msg.sim_id = sim_info.sim_id
        msg.is_branch_select = False
        msg.reason = career_ops.CareerOps.QUIT_CAREER
        for career_instance in sim_info.careers.values():
            if not career_instance.show_career_in_join_career_picker:
                continue
            career_info_msg = msg.career_choices.add()
            career_info_msg.uid = career_instance.guid64
            career_info_msg.career_track = career_instance.current_track_tuning.guid64
            career_info_msg.career_level = career_instance.level
            career_info_msg.company = career_instance.get_company_name()
            career_info_msg.conflicted_schedule = False
            career_level = career_instance.current_track_tuning.career_levels[career_instance.level]
            work_schedule = get_career_schedule_for_level(career_level)
            if work_schedule is not None:
                work_schedule.populate_scheduler_msg(career_info_msg.work_schedule, career_instance.schedule_shift_type)
        return msg

    @staticmethod
    def get_select_career_track_pb(sim_info, career, career_branches):
        msg = protocolbuffers.Sims_pb2.CareerSelectionUI()
        msg.sim_id = sim_info.sim_id
        msg.is_branch_select = True
        for career_track in career_branches:
            career_info_msg = msg.career_choices.add()
            career_info_msg.uid = career.guid64
            career_info_msg.career_track = career_track.guid64
            career_info_msg.career_level = 0
            career_info_msg.company = career.get_company_name()
            work_schedule = get_career_schedule_for_level(career_track.career_levels[0])
            career_level = career_track.career_levels[0]
            work_schedule = get_career_schedule_for_level(career_level)
            if work_schedule is not None:
                work_schedule.populate_scheduler_msg(career_info_msg.work_schedule)
        return msg

class TunableCareerTrack(metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.CAREER_TRACK)):
    INSTANCE_TUNABLES = {'career_name': sims4.localization.TunableLocalizedStringFactory(description='\n            The name of this Career Track\n            ', export_modes=sims4.tuning.tunable_base.ExportModes.All, tuning_group=GroupNames.UI), 'career_name_gender_neutral': sims4.localization.TunableLocalizedString(description="\n            The gender neutral name for this Career. This string is not provided\n            any tokens, and thus can't rely on context to properly form\n            masculine and feminine forms.\n            ", export_modes=sims4.tuning.tunable_base.ExportModes.All, tuning_group=GroupNames.UI), 'career_description': sims4.localization.TunableLocalizedString(description='A description for this Career Track', allow_none=True, export_modes=sims4.tuning.tunable_base.ExportModes.All, tuning_group=GroupNames.UI), 'icon': sims4.tuning.tunable.TunableResourceKey(None, resource_types=sims4.resources.CompoundTypes.IMAGE, description='Icon to be displayed for this Career Track', export_modes=sims4.tuning.tunable_base.ExportModes.All, tuning_group=GroupNames.UI), 'icon_high_res': sims4.tuning.tunable.TunableResourceKey(None, resource_types=sims4.resources.CompoundTypes.IMAGE, description='Icon to be displayed for screen slams from this career track', export_modes=sims4.tuning.tunable_base.ExportModes.All, tuning_group=GroupNames.UI), 'image': sims4.tuning.tunable.TunableResourceKey(None, resource_types=sims4.resources.CompoundTypes.IMAGE, description='Pre-rendered image to show in the branching select UI.', export_modes=sims4.tuning.tunable_base.ExportModes.All, tuning_group=GroupNames.UI), 'display_overmax_instead_of_career_levels': Tunable(description='\n            If checked, we will display overmax levels to the user instead of user career levels in the UI.\n            ', tunable_type=bool, default=False, tuning_group=GroupNames.UI), 'career_levels': sims4.tuning.tunable.TunableList(description='\n                            All of the career levels you need to be promoted through to\n                            get through this career track. When you get promoted past the\n                            end of a career track, and branches is tuned, you will get a selection\n                            UI where you get to pick the next part of your career.\n                            ', tunable=sims4.tuning.tunable.TunableReference(description='\n                                A single career track', manager=services.get_instance_manager(sims4.resources.Types.CAREER_LEVEL), reload_dependent=True), export_modes=sims4.tuning.tunable_base.ExportModes.All), 'branches': sims4.tuning.tunable.TunableList(sims4.tuning.tunable.TunableReference(description='A single career level', manager=services.get_instance_manager(sims4.resources.Types.CAREER_TRACK)), description="\n                              When you get promoted past the end of a career track, branches\n                              determine which career tracks you can progress to next. i.e.\n                              You're in the medical career and the starter track has 5 levels in\n                              it. When you get promoted to level 6, you get to choose either the\n                              surgeon track, or the organ seller track \n                            ", export_modes=sims4.tuning.tunable_base.ExportModes.All), 'overmax': OptionalTunable(description='\n            If enabled, then this track is eligible for overmaxing, making Sims\n            able to increase their level and salary despite reaching the top\n            tier.\n            ', tunable=TunableTuple(description='\n                Overmax data for this career.\n                ', salary_increase=TunableRange(description='\n                    The pay raise awarded per overmax level.\n                    ', tunable_type=int, default=1, minimum=1), reward=TunableReference(description='\n                    If specified, any rewards that may be awarded when\n                    overmaxing.\n                    ', manager=services.get_instance_manager(sims4.resources.Types.REWARD)), reward_by_level=OptionalTunable(description='\n                    If tuned, a special reward that will substituted for the\n                    normal reward on certain overmax levels. The keys should be\n                    tuned such that if we want a reward for the first overmax,\n                    its key should be 1.\n                    ', tunable=TunableMapping(key_type=TunableRange(tunable_type=int, default=0, minimum=0), value_type=TunableReference(manager=services.get_instance_manager(sims4.resources.Types.REWARD)))), performance_threshold_increase=TunableRange(description='\n                    The amount to increase the performance requirement per\n                    overmax level. Eventually, this will be max performance.\n                    ', tunable_type=float, default=0))), 'knowledge_notification': OptionalTunable(description="\n            If enabled, this career track will provide a TNS when a Sim learns\n            about another Sim's career.\n            ", tunable=TunableUiDialogNotificationSnippet(description="\n                The notification to use when one Sim learns about another Sim's\n                career. Three additional tokens are provided: the level name (e.g.\n                Chef), the career name (e.g. Culinary), and the company name (e.g.\n                The Solar Flare).\n                "), enabled_by_default=True), 'goodbye_notification': TunableUiDialogNotificationSnippet(description='\n            The notification to use when the Sim is leaving a visit situation to\n            go to work. Three additional tokens are provided: the level name\n            (e.g. Chef), the career name (e.g. Culinary), and the company name\n            (e.g. The Solar Flare).\n            '), 'busy_time_situation_picker_tooltip': sims4.localization.TunableLocalizedString(description='\n            The tooltip that will display on the situation sim picker for\n            user selectable sims that will be busy during the situation.\n            ', export_modes=sims4.tuning.tunable_base.ExportModes.All), 'assignments': TunableList(description='\n            List of possible tested assignemnts that can offered on a work \n            day inside this career track.\n            ', tunable=TunableTuple(description='\n                Tuple of test and aspirations that will be run when selecting\n                a daily assignment.\n                ', tests=event_testing.tests.TunableTestSet(description='\n                   Tests to be run when daily tasks are being offered inside\n                   a career track.\n                   '), career_assignment=sims4.tuning.tunable.TunableReference(description='\n                    Aspiration that needs to be completed for satisfying the\n                    daily assignment.\n                    ', manager=services.get_instance_manager(sims4.resources.Types.ASPIRATION), class_restrictions='AspirationAssignment', pack_safe=True), weight=TunableRange(description='\n                    The weight of this assignment when the random roll chooses\n                    the daily tasks.\n                    ', tunable_type=float, default=1.0, minimum=0), is_first_assignment=sims4.tuning.tunable.Tunable(description='\n                    Setting this to true will trigger this assignment when a sim\n                    first joins a career.\n                    \n                    If all assignments are unchecked, the first assignment\n                    will be selected randomly.\n                    ', tunable_type=bool, default=False))), 'assignment_chance': TunablePercent(description='\n            Chance of an assignment being offered during a regular work day.\n            ', default=50), 'active_assignment_amount': sims4.tuning.tunable.Tunable(description='\n            Amount of active assignments to offer each time a Sim goes to work\n            \n            WARNING: Always make this less than the number of possible weighted\n            assignments.\n            ', tunable_type=float, default=2), 'outfit_generation_type': TunableEnumEntry(description='\n            Possible ways the career will generate the outfits for its sims.\n            By default CAREER tuning will use the level tuning to generate \n            the ouftit.\n            Zone director will use the restaurant zone director tuning to  \n            validate and generate the outfits for each level.\n            ', tunable_type=CareerOutfitGenerationType, default=CareerOutfitGenerationType.CAREER_TUNING)}
    parent_track = None

    @classmethod
    def _verify_tuning_callback(cls):
        if cls.active_assignment_amount > len(cls.assignments) and len(cls.assignments) > 0:
            logger.error('Warning - the Active Assignment Amount is greater than the number of possible assignments {}', cls, owner='Shirley')

    @classmethod
    def get_career_description(cls, sim):
        return cls.career_description

    @classmethod
    def get_career_name(cls, sim):
        return cls.career_name(sim)

class TunableTimePeriod(sims4.tuning.tunable.TunableTuple):

    def __init__(self, **kwargs):
        super().__init__(start_time=tunable_time.TunableTimeOfWeek(description='Time when the period starts.'), period_duration=sims4.tuning.tunable.Tunable(float, 1.0, description='Duration of this time period in hours.'), **kwargs)

class TunableOutfit(TunableTuple):

    def __init__(self, **kwargs):
        super().__init__(outfit_generator=OptionalTunable(TunableOutfitGeneratorReference()), generate_on_level_change=Tunable(description='\n                If checked, then an outfit is regenerated for this Sim on\n                promotion/demotion. If unchecked, the existing outfit is\n                maintained.\n                ', tunable_type=bool, default=True), **kwargs)

class StatisticPerformanceModifier(TunableTuple):

    def __init__(self, **kwargs):
        super().__init__(statistic=TunableReference(description='\n                Statistic that contributes to this performance modifier.\n                ', manager=services.get_instance_manager(sims4.resources.Types.STATISTIC)), performance_curve=TunableCurve(description='\n                Curve that maps the commodity to performance change. X is the\n                commodity value, Y is the bonus performance.\n                '), reset_at_end_of_work=Tunable(description='\n                If set, the statistic will be reset back to its default value\n                when a Sim leaves work.\n                ', tunable_type=bool, default=True), tooltip_text=OptionalTunable(description="\n                If enabled, this performance modifier's description will appear\n                in its tooltip.\n                ", tunable=TunableTuple(general_description=TunableLocalizedStringFactory(description='\n                        A description of the performance modifier. {0.String}\n                        is the thresholded description.\n                        '), thresholded_descriptions=TunableList(description='\n                        A list of thresholds and the text describing it. The\n                        thresholded description will be largest threshold\n                        value in this list that the commodity is >= to.\n                        ', tunable=TunableTuple(threshold=Tunable(description='\n                                Threshold that the commodity must >= to.\n                                ', tunable_type=float, default=0.0), text=TunableLocalizedString(description='\n                                Description for meeting this threshold.\n                                '))))), **kwargs)

class TunableWorkPerformanceMetrics(sims4.tuning.tunable.TunableTuple):

    def __init__(self, **kwargs):
        super().__init__(base_performance=sims4.tuning.tunable.Tunable(float, 1.0, description='Base work performance before any modifications are applied for going to a full day of work.'), missed_work_penalty=sims4.tuning.tunable.Tunable(float, 1.0, description="Penalty that is applied to your work day performance if you don't attend a full day of work."), full_work_day_percent=sims4.tuning.tunable.TunableRange(float, 80, 1, 100, description='This is the percent of the work day you must have been running the work interaction, to get full credit for your performance on that day. Ex: If this is tuned to 80, and you have a 5 hour work day, You must be inside the work interaction for at least 4 hours to get 100% of your performance. If you only went to work for 2 hours, you would get: (base_performance + positive performance mods * 0.5) + negative performance mods'), commodity_metrics=sims4.tuning.tunable.TunableList(sims4.tuning.tunable.TunableTuple(commodity=sims4.tuning.tunable.TunableReference(description='Commodity this test should apply to on the sim.', manager=services.get_instance_manager(sims4.resources.Types.STATISTIC)), threshold=sims4.tuning.tunable.TunableThreshold(description='The amount of commodity needed to get this performance mod.'), performance_mod=sims4.tuning.tunable.Tunable(float, 1.0, description='Work Performance you get for passing the commodity threshold.'), description='DEPRECATED. USE STATISTIC METRICS INSTEAD. If the tunable commodity is within the tuned threshold, this performance mod will be applied to an individual day of work.')), mood_metrics=sims4.tuning.tunable.TunableList(sims4.tuning.tunable.TunableTuple(mood=sims4.tuning.tunable.TunableReference(description='Mood the Sim needs to get this performance change.', manager=services.get_instance_manager(sims4.resources.Types.MOOD)), performance_mod=sims4.tuning.tunable.Tunable(float, 1.0, description='Work Performance you get for having this mood.'), description='If the Sim is in this mood state, they will get this performance mod applied for a day of work')), statistic_metrics=TunableList(description='\n                             Performance modifiers based on a statistic.\n                             ', tunable=StatisticPerformanceModifier()), performance_tooltip=OptionalTunable(description='\n                             Text to show on the performance tooltip below the\n                             ideal mood bar. Any Statistic Metric tooltip text\n                             will appear below this text on a new line.\n                             ', tunable=TunableLocalizedString()), performance_per_completed_goal=Tunable(description='\n                             The performance amount to give per completed\n                             career goal each work period.\n                             ', tunable_type=float, default=0.0), tested_metrics=TunableList(description='\n                             Performance modifiers that are applied based on\n                             the test.\n                             ', tunable=TunableTuple(tests=event_testing.tests.TunableTestSet(description='\n                                    Tests that must pass to get the performance modifier.\n                                    '), performance_mod=sims4.tuning.tunable.Tunable(description='\n                                    Performance modifier the Sim receives for passing the test. Can be negative.\n                                    ', tunable_type=float, default=0.0))), daily_assignment_performance=Tunable(description='\n                             The total performance amount to give for completing all\n                             assignments.\n                             ', tunable_type=float, default=1.0), **kwargs)

class CareerLevel(SuperAffordanceProviderMixin, TargetSuperAffordanceProviderMixin, MixerProviderMixin, MixerActorMixin, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.CAREER_LEVEL)):
    INSTANCE_TUNABLES = {'title': sims4.localization.TunableLocalizedStringFactory(description='Your career title for this career level', export_modes=sims4.tuning.tunable_base.ExportModes.All, tuning_group=GroupNames.UI), 'title_description': sims4.localization.TunableLocalizedStringFactory(description='A description for this individual career level', allow_none=True, export_modes=sims4.tuning.tunable_base.ExportModes.All, tuning_group=GroupNames.UI), 'promotion_audio_sting': OptionalTunable(description='\n            The audio sting to play when the Sim is promoted to this Career Level.\n            ', tunable=TunablePlayAudio(), tuning_group=GroupNames.AUDIO), 'screen_slam': OptionalTunable(description='\n            Which screen slam to show when this career level is reached.\n            Localization Tokens: Sim - {0.SimFirstName}, Level Name - \n            {1.String}, Level Number - {2.Number}, Track Name - {3.String}\n            ', tunable=ui.screen_slam.TunableScreenSlamSnippet()), 'work_schedule': scheduler.WeeklySchedule.TunableFactory(description='\n            A tunable schedule that will determine when you have to be at work.\n            ', export_modes=sims4.tuning.tunable_base.ExportModes.All, tuning_group=GroupNames.DEPRECATED), 'schedule': TunableCareerScheduleVariant(description='\n            Define the work hours for this particular career level.\n            '), 'additional_unavailable_times': sims4.tuning.tunable.TunableList(TunableTimePeriod(description='An individual period of time in which the sim is unavailible at this Career Level.'), description='A list time periods in which the Sim is considered busy for the sake of Sim Filters in addition to the normal working hours.'), 'wakeup_time': tunable_time.TunableTimeOfDay(description="\n            The time when the sim needs to wake up for work.  This is used by autonomy\n            to determine when it's appropriate to nap vs sleep.  It also guides a series\n            of buffs to make the sim more inclined to sleep as their bedtime approaches.", default_hour=8, needs_tuning=True), 'work_outfit': TunableOutfit(description='Tuning for this career level outfit.'), 'work_outfit_overrides': sims4.tuning.tunable.TunableList(description='\n            A list of (test, outfit) pairs. If any test passes, the corresponding\n            work outfit override will be chosen. When a work outfit override is\n            chosen, no later tests will be evaluated, so higher priority tests\n            should come first. \n            ', tunable=TunableTuple(test=TunableTestSet(description='\n                    The test.\n                    '), work_outfit=TunableOutfit(description='\n                    The outfit to use to override work_outfit\n                    '))), 'aspiration': sims4.tuning.tunable.TunableReference(manager=services.get_instance_manager(sims4.resources.Types.ASPIRATION), allow_none=True, description='The Aspiration you need to complete to be eligible for promotion.', export_modes=sims4.tuning.tunable_base.ExportModes.All), 'pay_type': TunableVariant(description='\n            The different way the sim can be paid. \n            If it is gig based then just a string is displayed. \n            ', simoleons_per_hour=Tunable(description='\n                number of simoleons you get per hour this level.\n                ', tunable_type=int, default=10), potential_simoleons_weekly=TunableLocalizedStringFactory(description="\n                String to display if sim doesn't earn a set amount of simoleons\n                per hour. \n                "), export_modes=ExportModes.All), 'simoleons_for_assignments_per_day': sims4.tuning.tunable.Tunable(description=' \n            Number of simoleons acquired if completing all assignments in a day.\n            (scaled and handled out per assignment.)\n            ', tunable_type=int, default=10), 'pto_per_day': sims4.tuning.tunable.Tunable(description=' \n            Number of days of PTO per full day worked.  Will be scaled according\n            to how much time is actually worked.\n            ', tunable_type=float, default=0.1, export_modes=sims4.tuning.tunable_base.ExportModes.All), 'pto_accrual_trait_multiplier': TunableList(description='\n            A multiplier on the rate of pto accrual\n            ', tunable=sims4.tuning.tunable.TunableTuple(trait=sims4.tuning.tunable.TunableReference(description='\n                    Trait to test for on the Sim that applies the pto multiplier.\n                    ', manager=services.get_instance_manager(sims4.resources.Types.TRAIT), pack_safe=True), multiplier=sims4.tuning.tunable.Tunable(description='\n                    The multiplier to apply to the rate of pto accrual\n                    ', tunable_type=float, default=1))), 'simolean_trait_bonus': sims4.tuning.tunable.TunableList(description='\n            A bonus additional income amount applied at the end of the work day to total take home pay\n            based on the presence of the tuned trait.', tunable=sims4.tuning.tunable.TunableTuple(trait=sims4.tuning.tunable.TunableReference(description='\n                    Trait to test for on the Sim that allows the bonus to get added.', manager=services.get_instance_manager(sims4.resources.Types.TRAIT), pack_safe=True), bonus=sims4.tuning.tunable.Tunable(description='\n                Percentage of daily take to add as bonus income.', tunable_type=int, default=20, tuning_group=GroupNames.SCORING))), 'performance_stat': sims4.tuning.tunable.TunableReference(services.get_instance_manager(sims4.resources.Types.STATISTIC), description='Commodity used to track career performance for this level.', export_modes=sims4.tuning.tunable_base.ExportModes.All, tuning_group=GroupNames.SCORING), 'demotion_performance_level': sims4.tuning.tunable.Tunable(float, -80.0, description='Level of performance commodity to cause demotion.', tuning_group=GroupNames.SCORING), 'fired_performance_level': sims4.tuning.tunable.Tunable(float, -95.0, description='Level of performance commodity to cause being fired.', tuning_group=GroupNames.SCORING), 'promote_performance_level': sims4.tuning.tunable.Tunable(float, 100.0, description='Level of performance commodity to cause being promoted.', tuning_group=GroupNames.SCORING), 'performance_metrics': TunableWorkPerformanceMetrics(tuning_group=GroupNames.SCORING), 'promotion_reward': sims4.tuning.tunable.TunableReference(manager=services.get_instance_manager(sims4.resources.Types.REWARD), allow_none=True, description='\n            Which rewards are given when this career level\n            is reached.\n            '), 'tones': OptionalTunable(description='\n            If enabled, specify tones that the Sim can have in its skewer while\n            at work.\n            ', tunable=CareerToneTuning.TunableFactory(description='\n                Tuning for tones.\n                ')), 'ideal_mood': sims4.tuning.tunable.TunableReference(description='\n            The ideal mood to display to the user to be in to gain performance at this career level\n            ', manager=services.get_instance_manager(sims4.resources.Types.MOOD), allow_none=True, export_modes=sims4.tuning.tunable_base.ExportModes.ClientBinary, tuning_group=GroupNames.UI), 'loot_on_join': TunableList(description='\n            A list of loot actions to give the sim when they join the career\n            at this level.\n            ', tunable=LootActions.TunableReference(description='\n                Loot to give when Sim joins the career at this career level.\n                ', pack_safe=True)), 'loot_on_quit': LootActions.TunableReference(description='\n            Loot to give when Sim quits the career on this career level.\n            ', allow_none=True), 'object_create_on_join': TunableList(description='\n            Objects to create on join.  If marked as require claim they will only exist\n            for as long as the sim in in the career at this level.\n            ', tunable=ObjectCreation.TunableFactory()), 'stay_late_extension': TunableSimMinute(description='\n            How long to extend the active work shift when the Sim stays late.\n            ', default=120), 'end_of_day_loot': TunableSet(description='\n            List of loot applied to the sim at the end of the day.\n            Currently used only to max out daily task at the end of the day\n            if responsible trait is available but it can be extended to include\n            more end of day loot in the future.\n            ', tunable=LootActions.TunableReference(description='\n                Loot to give at the end of the day. \n                ', pack_safe=True)), 'fame_moment': OptionalTunable(description='\n            When enabled allows a fame adventure moment to be displayed to the\n            user, once per career track.\n            ', tunable=TunableTuple(description='\n                The data associated with a fame moment.\n                \n                moment is the adventure moment that is displayed when the\n                    moment occurs\n                \n                chance_to_occur is the liklihood that a moment happens during\n                    a shift.\n                ', moment=Adventure.TunableFactory(description='\n                    A reference to the adventure moment that can happen once and only\n                    once while the Sim has this career track.\n                    '), chance_to_occur=SuccessChance.TunableFactory(description='\n                    The chance the moment will happen during a given shift.\n                    '))), 'agents_available': TunableList(description='\n            List of agents available for this career level. A higher level \n            should include more agents not fewer.\n            ', tunable=TunableReference(description='\n                A reference to the agent available for this career level.\n                ', manager=services.get_instance_manager(sims4.resources.Types.TRAIT), pack_safe=True), export_modes=ExportModes.All), 'ageup_branch_career': OptionalTunable(description='\n            This adult career will be assigned to the teen that ages up while\n            on the parent career.\n            ', tunable=TunableReference(manager=services.get_instance_manager(sims4.resources.Types.CAREER)))}
    career = None
    track = None
    level = None
    user_level = None

    @classmethod
    def _verify_tuning_callback(cls):
        for trait in cls.agents_available:
            if trait.trait_type != TraitType.AGENT:
                logger.error('Only trait type agent allowed in this list.')

    @classmethod
    def get_aspiration(cls):
        return cls.aspiration

    @classmethod
    def get_title(cls, sim):
        return cls.title(sim)

    @classproperty
    def simoleons_per_hour(cls):
        if isinstance(cls.pay_type, int):
            return cls.pay_type
        return 0

    @classmethod
    def get_work_outfit(cls, sim_info):
        if cls.work_outfit_overrides:
            if sim_info is not None:
                resolver = SingleSimResolver(sim_info)
                for override in cls.work_outfit_overrides:
                    if override.test.run_tests(resolver):
                        return override.work_outfit
        return cls.work_outfit

class DefaultCareerSelectionData:

    def __init__(self, default_career_select=0, career_selector_type=0):
        self.default_career_select = default_career_select
        self.career_selector_type = career_selector_type

class CareerSelectionDefault(HasTunableSingletonFactory, AutoFactoryInit):

    def get_default_career_information(self):
        raise NotImplementedError

class CareerReferenceSelectionDefault(CareerSelectionDefault):
    FACTORY_TUNABLES = {'toggle_career': TunableTuple(default_career=TunablePackSafeReference(description='\n                The default selected career.\n                ', manager=services.get_instance_manager(sims4.resources.Types.CAREER)), toggle_to_career_selector_type=Tunable(description="\n                If set to True, the career panel will open to the career selector\n                type panel of the tuned default career's selector type. If False,\n                the career will be selected in the default All Careers panel.\n                ", tunable_type=bool, default=False))}

    def get_default_career_information(self):
        default_career = self.toggle_career.default_career
        default_career_select_uid = self.toggle_career.default_career.guid64 if default_career is not None else 0
        career_selector_type = CareerSelectorTypes.ALL
        if default_career is not None:
            if self.toggle_career.toggle_to_career_selector_type:
                career_selector_type = get_selector_type_from_career_category(default_career)
        return DefaultCareerSelectionData(default_career_select=default_career_select_uid, career_selector_type=career_selector_type)

class CareerSelectorCategoryDefault(CareerSelectionDefault):
    FACTORY_TUNABLES = {'default_selector_type': TunableEnumEntry(description='\n            The default panel at which to open the career selection\n            window.\n            ', tunable_type=CareerSelectorTypes, default=CareerSelectorTypes.ALL)}

    def get_default_career_information(self):
        return DefaultCareerSelectionData(career_selector_type=self.default_selector_type)

class CareerSelectElement(interactions.utils.interaction_elements.XevtTriggeredElement):
    FACTORY_TUNABLES = {'description': 'Perform an operation on a Sim Career', 'career_op': sims4.tuning.tunable.TunableEnumEntry(career_ops.CareerOps, career_ops.CareerOps.JOIN_CAREER, description='\n                                Operation this basic extra will perform on the\n                                career.  Currently supports Joining, Quitting\n                                and Playing Hooky/Calling In Sick.\n                                '), 'subject': TunableEnumFlags(description='\n            The Sim to run this career op on.\n            Currently, the only supported options are Actor and PickedSim\n            ', enum_type=ParticipantType, default=ParticipantType.Actor), 'default_career_window_selection': OptionalTunable(description='\n            If enabled, then the default selection in the Career Selection Window\n            will be set to the tuned value.\n            ', tunable=TunableVariant(career_reference=CareerReferenceSelectionDefault.TunableFactory(description='\n                    Default selection and selector type is based on a single \n                    career reference.\n                    '), career_selector_type=CareerSelectorCategoryDefault.TunableFactory(description='\n                    Default selector type panel is the tuned value.\n                    '), default='career_reference'))}

    def _get_default_selection_data(self):
        if self.default_career_window_selection is not None:
            return self.default_career_window_selection.get_default_career_information()

    def _do_behavior(self):
        if services.current_zone().ui_dialog_service.auto_respond:
            return
        participants = self.interaction.get_participants(self.subject)
        if participants is None or len(participants) == 0:
            logger.error('Could not find participant type, {}, for the Career Select op on interaction, {}', self.subject, self.interaction, owner='Trevor')
            return
        if len(participants) > 1:
            logger.warn('More than one participant found of type, {}, for the Career Select op on interaction, {}', self.subject, self.interaction, owner='Dan P')
        sim_or_sim_info = next(iter(participants))
        sim_info = getattr(sim_or_sim_info, 'sim_info', sim_or_sim_info)
        if self.career_op == career_ops.CareerOps.JOIN_CAREER:
            num = Career.NUM_CAREERS_PER_DAY
            if self.interaction.debug or self.interaction.cheat:
                num = 0
            if sim_info.is_selectable and sim_info.valid_for_distribution:
                default_career_selection_data = self._get_default_selection_data()
                msg = Career.get_join_career_pb(sim_info, num_careers_to_show=num, default_career_selection_data=default_career_selection_data)
                Distributor.instance().add_op(sim_info, GenericProtocolBufferOp(Operation.SELECT_CAREER_UI, msg))
        elif self.career_op == career_ops.CareerOps.QUIT_CAREER:
            if len(sim_info.career_tracker.get_quittable_careers()) == 1:

                def on_quit_dialog_response(dialog):
                    if dialog.accepted:
                        sim_info.career_tracker.remove_career(career.guid64)

                for career in sim_info.career_tracker.get_quittable_careers().values():
                    career_name = career._current_track.get_career_name(sim_info)
                    job_title = career.current_level_tuning.get_title(sim_info)
                    dialog = None
                    resolver = SingleSimResolver(sim_info)
                    if career.quittable_data.tested_quit_dialog is not None and career.quittable_data.tested_quit_dialog.test_set.run_tests(resolver):
                        dialog = career.quittable_data.tested_quit_dialog.quit_dialog(sim_info, resolver)
                    else:
                        dialog = career.quittable_data.quit_dialog(sim_info, resolver)
                    dialog.show_dialog(on_response=on_quit_dialog_response, additional_tokens=(career_name, job_title, career.get_company_name()))
            elif sim_info.is_selectable:
                if sim_info.valid_for_distribution:
                    msg = Career.get_quit_career_pb(sim_info)
                    Distributor.instance().add_op(sim_info, GenericProtocolBufferOp(Operation.SELECT_CAREER_UI, msg))
        elif self.career_op == career_ops.CareerOps.CALLED_IN_SICK:
            for career in sim_info.careers.values():
                career.request_day_off(career_ops.CareerTimeOffReason.FAKE_SICK)
