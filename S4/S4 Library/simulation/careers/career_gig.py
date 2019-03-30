import random
from protocolbuffers.ResourceKey_pb2 import ResourceKey
from audio.primitive import TunablePlayAudio
from careers.prep_tasks.prep_task import PrepTask
from careers.prep_tasks.prep_task_tracker_mixin import PrepTaskTrackerMixin
from date_and_time import DateAndTime
from distributor.shared_messages import create_icon_info_msg, IconInfoData
from event_testing.resolver import SingleSimResolver
from event_testing.tests import TunableTestSet
from filters.tunable import TunableSimFilter
from interactions.utils.display_mixin import get_display_mixin
from interactions.utils.tunable_icon import TunableIcon
from relationships.relationship_bit import RelationshipBit, RelationshipBitCollectionUid
from scheduler import WeeklySchedule
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import HasTunableReference, TunableInterval, TunableList, TunableReference, TunableTuple, OptionalTunable, TunableEnumEntry, Tunable, TunableMapping
from sims4.tuning.tunable_base import ExportModes
from situations.situation_types import SituationMedal
from tunable_multiplier import TunableMultiplier
from tunable_time import TunableTimeSpan
from ui.ui_dialog_labeled_icons import UiDialogLabeledIcons
import services
import sims4
logger = sims4.log.Logger('Gig', default_owner='bosee')
_GigDisplayMixin = get_display_mixin(has_description=True, has_icon=True, use_string_tokens=True)

class Gig(HasTunableReference, _GigDisplayMixin, PrepTaskTrackerMixin, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.CAREER_GIG)):
    INSTANCE_TUNABLES = {'gig_time': WeeklySchedule.TunableFactory(description='\n            A tunable schedule that will determine when you have to be at work.\n            ', export_modes=ExportModes.All), 'gig_prep_time': TunableTimeSpan(description='\n            The amount of time between the audition and the gig. If no audition\n            is required, then this is the amount of time between the time the\n            gig was picked and this audition.\n            ', default_hours=5), 'gig_prep_tasks': TunableList(description='\n            A list of prep tasks the Sim can do to improve their performance\n            during the gig. \n            ', tunable=PrepTask.TunableFactory()), 'audio_on_prep_task_completion': OptionalTunable(description='\n            A sting to play at the time a prep task completes.\n            ', tunable=TunablePlayAudio(locked_args={'immediate': True, 'joint_name_hash': None, 'play_on_active_sim_only': True})), 'gig_pay_range': TunableInterval(description='\n            Minimum and maximum amount of money the sim can earn in this gig.\n            ', tunable_type=int, default_lower=0, default_upper=100, minimum=0), 'payout_stat_data': TunableMapping(description='\n            Stats, and its associated information, that are gained (or lost) \n            when sim finishes this gig.\n            ', key_type=TunableReference(description='\n                Stat for this payout.\n                ', manager=services.get_instance_manager(sims4.resources.Types.STATISTIC)), value_type=TunableTuple(description='\n                Data about this payout stat. \n                ', base_amount=Tunable(description='\n                    Base amount (pre-modifiers) applied to the sim at the end\n                    of the gig.\n                    ', tunable_type=float, default=0.0), medal_to_payout=TunableMapping(description='\n                    Mapping of medal -> stat multiplier.\n                    ', key_type=TunableEnumEntry(description='\n                        Medal achieved in this gig.\n                        ', tunable_type=SituationMedal, default=SituationMedal.TIN), value_type=TunableMultiplier.TunableFactory(description='\n                        Mulitiplier on statistic payout if scorable situation\n                        ends with the associate medal.\n                        ')), ui_threshold=TunableList(description='\n                    Thresholds and icons we use for this stat to display in \n                    the end of day dialog. Tune in reverse of highest threshold \n                    to lowest threshold.\n                    ', tunable=TunableTuple(description='\n                        Threshold and icon for this stat and this gig.\n                        ', threshold_icon=TunableIcon(description='\n                            Icon if the stat is of this threshold.\n                            '), threshold_description=TunableLocalizedStringFactory(description='\n                            Description to use with icon\n                            '), threshold=Tunable(description='\n                            Threshold that the stat must >= to.\n                            ', tunable_type=float, default=0.0))))), 'career_events': TunableList(description='\n             A list of available career events for this gig.\n             ', tunable=TunableReference(manager=services.get_instance_manager(sims4.resources.Types.CAREER_EVENT))), 'gig_cast_rel_bit_collection_id': TunableEnumEntry(description='\n            If a rel bit is applied to the cast member, it must be of this collection id.\n            We use this to clear the rel bit when the gig is over.\n            ', tunable_type=RelationshipBitCollectionUid, default=RelationshipBitCollectionUid.Invalid, invalid_enums=(RelationshipBitCollectionUid.All,)), 'gig_cast': TunableList(description='\n            This is the list of sims that need to spawn for this gig. \n            ', tunable=TunableTuple(description='\n                Data for cast members. It contains a test which tests against \n                the owner of this gig and spawn the necessary sims. A bit\n                may be applied through the loot action to determine the type \n                of cast members (costars, directors, etc...) \n                ', filter_test=TunableTestSet(description='\n                    Test used on owner sim.\n                    '), sim_filter=TunableSimFilter.TunableReference(description='\n                    If filter test is passed, this sim is created and stored.\n                    '), cast_member_rel_bit=OptionalTunable(description='\n                    If tuned, this rel bit will be applied on the spawned cast \n                    member.\n                    ', tunable=RelationshipBit.TunableReference(description='\n                        Rel bit to apply.\n                        ')))), 'end_of_gig_dialog': OptionalTunable(description='\n            A results dialog to show. This dialog allows a list\n            of icons with labels. Stats are added at the end of this icons.\n            ', tunable=UiDialogLabeledIcons.TunableFactory())}

    @classmethod
    def _verify_tuning_callback(cls):
        for cast in cls.gig_cast:
            if cast.cast_member_rel_bit is not None and cls.gig_cast_rel_bit_collection_id not in cast.cast_member_rel_bit.collection_ids:
                logger.error('Cast member relationship bit needs to be of type {} in {}', cls.gig_cast_rel_bit_collection_id, cls)

    def __init__(self, owner, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._owner = owner
        self._cast_list_ids = []
        self._upcoming_gig_time = None

    def get_random_gig_event(self):
        return random.choice(self.career_events)

    def get_gig_time(self):
        return self._upcoming_gig_time

    def clean_up_gig(self):
        if not services.current_zone().is_zone_shutting_down:
            for cast_id in self._cast_list_ids:
                self._owner.relationship_tracker.remove_relationship_bit_by_collection_id(cast_id, self.gig_cast_rel_bit_collection_id)
        self._cast_list_ids = []
        self.prep_task_cleanup()

    def save_gig(self, gig_proto_buff):
        gig_proto_buff.gig_type = self.guid64
        gig_proto_buff.gig_time = self._upcoming_gig_time
        gig_proto_buff.cast_list.extend(self._cast_list_ids)

    def load_gig(self, gig_proto_buff):
        self._upcoming_gig_time = DateAndTime(gig_proto_buff.gig_time)
        self._cast_list_ids.extend(gig_proto_buff.cast_list)
        self.prep_time_start(self._owner, self.gig_prep_tasks, self.guid64, self.audio_on_prep_task_completion)

    def set_up_gig(self, upcoming_gig_time):
        self._upcoming_gig_time = upcoming_gig_time
        self._roll_cast()
        self.prep_time_start(self._owner, self.gig_prep_tasks, self.guid64, self.audio_on_prep_task_completion)

    def _roll_cast(self):
        resolver = SingleSimResolver(self._owner)
        blacklist_sim_ids = {sim_info.sim_id for sim_info in services.active_household()}
        blacklist_sim_ids.update(set(sim_info.sim_id for sim_info in services.sim_info_manager().instanced_sims_gen()))

        def get_sim_filter_gsi_name():
            return 'Cast member for gig.'

        for potential_cast_member in self.gig_cast:
            if not potential_cast_member.filter_test.run_tests(resolver=resolver):
                pass
            else:
                generated_result = services.sim_filter_service().submit_matching_filter(sim_filter=potential_cast_member.sim_filter, allow_yielding=False, blacklist_sim_ids=blacklist_sim_ids, gsi_source_fn=get_sim_filter_gsi_name)
                for result in generated_result:
                    cast_sim_info = result.sim_info
                    self._owner.relationship_tracker.add_relationship_bit(cast_sim_info.id, potential_cast_member.cast_member_rel_bit)
                    self._cast_list_ids.append(cast_sim_info.id)
                    blacklist_sim_ids.add(cast_sim_info.id)

    def collect_rabbit_hole_rewards(self):
        self._apply_payout_stat(SituationMedal.BRONZE)

    def get_rabbit_hole_pay(self):
        return self.gig_pay_range.lower_bound

    def build_end_gig_dialog(self, payout):
        owner_sim = self._owner
        resolver = SingleSimResolver(owner_sim)
        medal = payout.medal
        payout_display_data = []
        self._apply_payout_stat(medal, payout_display_data)
        additional_icons = []
        for additional_payout in payout_display_data:
            additional_icons.append(create_icon_info_msg(IconInfoData(additional_payout.threshold_icon), name=additional_payout.threshold_description()))
        end_of_day_dialog = self.end_of_gig_dialog(owner_sim, resolver=resolver)
        return (end_of_day_dialog, additional_icons)

    @classmethod
    def build_gig_msg(cls, msg, sim, gig_time=None, audition_time=None):
        msg.gig_type = cls.guid64
        msg.gig_name = cls.display_name(sim)
        msg.min_pay = cls.gig_pay_range.lower_bound
        msg.max_pay = cls.gig_pay_range.upper_bound
        msg.gig_icon = ResourceKey()
        msg.gig_icon.instance = cls.display_icon.instance
        msg.gig_icon.group = cls.display_icon.group
        msg.gig_icon.type = cls.display_icon.type
        msg.gig_description = cls.display_description(sim)
        if gig_time is not None:
            msg.gig_time = gig_time
        if audition_time is not None:
            msg.audition_time = audition_time

    def send_prep_task_update(self):
        self._prep_task_tracker.send_prep_task_update()

    def _apply_payout_stat(self, medal, payout_display_data=None):
        owner_sim = self._owner
        resolver = SingleSimResolver(owner_sim)
        payout_stats = self.payout_stat_data
        for stat in payout_stats.keys():
            stat_tracker = owner_sim.get_tracker(stat)
            if not owner_sim.get_tracker(stat).has_statistic(stat):
                pass
            else:
                stat_data = payout_stats[stat]
                stat_multiplier = 1.0
                if medal in stat_data.medal_to_payout:
                    multiplier = stat_data.medal_to_payout[medal]
                    stat_multiplier = multiplier.get_multiplier(resolver)
                stat_total = stat_data.base_amount*stat_multiplier
                stat_tracker.add_value(stat, stat_total)
                if payout_display_data is not None:
                    for threshold_data in stat_data.ui_threshold:
                        if stat_total >= threshold_data.threshold:
                            payout_display_data.append(threshold_data)
                            break
