from careers.career_enums import GigResult
from careers.career_gig import Gig
from event_testing.resolver import SingleSimResolver
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable import TunableReference, OptionalTunable
from tunable_time import TunableTimeSpan
from ui.ui_dialog_picker import ObjectPickerRow
import services
import sims4
logger = sims4.log.Logger('HomeAssignmentGig', default_owner='rrodgers')

class HomeAssignmentGig(Gig):
    INSTANCE_TUNABLES = {'gig_picker_localization_format': TunableLocalizedStringFactory(description='\n            String used to format the description in the gig picker. Currently\n            has tokens for name, payout, gig time, tip title, and tip text.\n            '), 'gig_assignment_aspiration': TunableReference(description='\n            An aspiration to use as the assignment for this gig. The objectives\n            of this aspiration\n            ', manager=services.get_instance_manager(sims4.resources.Types.ASPIRATION), class_restrictions='AspirationGig'), 'great_success_remaining_time': OptionalTunable(description='\n            If the aspiration for this gig is completed with more than this\n            amount of time left, the gig will be considered a great success.\n            ', tunable=TunableTimeSpan())}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._gig_pay = None

    @classmethod
    def get_aspiration(cls):
        return cls.gig_assignment_aspiration

    def set_up_gig(self):
        super().set_up_gig()
        aspiration_tracker = self._owner.aspiration_tracker
        aspiration_tracker.reset_milestone(self.gig_assignment_aspiration)
        self.gig_assignment_aspiration.register_callbacks()
        aspiration_tracker.process_test_events_for_aspiration(self.gig_assignment_aspiration)

    def load_gig(self, gig_proto_buff):
        super().load_gig(gig_proto_buff)
        self.gig_assignment_aspiration.register_callbacks()

    def get_pay(self, overmax_level=None, **_):
        completed_objectives = 0
        aspiration_tracker = self._owner.aspiration_tracker
        if aspiration_tracker is not None:
            for objective in self.gig_assignment_aspiration.objectives:
                if aspiration_tracker.objective_completed(objective):
                    completed_objectives += 1
        else:
            completed_objectives = len(self.gig_assignment_aspiration.objectives)
        remaining_time = self._upcoming_gig_time - services.time_service().sim_now
        if completed_objectives < len(self.gig_assignment_aspiration.objectives):
            if completed_objectives == 0:
                self._gig_result = GigResult.CRITICAL_FAILURE
            else:
                self._gig_result = GigResult.FAILURE
        elif self.great_success_remaining_time and remaining_time > self.great_success_remaining_time():
            self._gig_result = GigResult.GREAT_SUCCESS
        else:
            self._gig_result = GigResult.SUCCESS
        pay = self.gig_pay.lower_bound
        if self.additional_pay_per_overmax_level:
            pay = pay + overmax_level*self.additional_pay_per_overmax_level
        if self.result_based_gig_pay_multipliers:
            if self._gig_result in self.result_based_gig_pay_multipliers:
                multiplier = self.result_based_gig_pay_multipliers[self._gig_result].get_multiplier(SingleSimResolver(self._owner))
                pay = pay*multiplier
        self._gig_pay = pay
        return pay

    def get_overmax_evaluation_result(self, reward_text, overmax_level, *args, **kwargs):
        return super().get_overmax_evaluation_result(reward_text, overmax_level, *args, **kwargs)

    def send_prep_task_update(self):
        pass

    @classmethod
    def build_gig_msg(cls, msg, sim, gig_time=None):
        super().build_gig_msg(msg, sim, gig_time=gig_time)
        msg.aspiration_id = cls.gig_assignment_aspiration.guid64

    def treat_work_time_as_due_date(self):
        return True

    @classmethod
    def create_picker_row(cls, scheduled_time=None, owner=None, **kwargs):
        if not cls.tip:
            logger.error('No tip tuned for Home Assignment Gig {}. Home assignment Gigs must have a tip.', cls)
            return
        (pay_lower, pay_upper) = cls._get_base_pay_for_gig_owner(owner)
        description = cls.gig_picker_localization_format(pay_lower, pay_upper, scheduled_time, cls.tip.tip_title(), cls.tip.tip_text())
        row_tooltip = None if cls.display_description is None else lambda *_: cls.display_description(owner)
        row = ObjectPickerRow(name=cls.display_name(owner), icon=cls.display_icon, row_description=description, row_tooltip=row_tooltip)
        return row

lock_instance_tunables(HomeAssignmentGig, gig_prep_tasks=None, audio_on_prep_task_completion=None, career_events=None, gig_cast_rel_bit_collection_id=None, gig_cast=None, end_of_gig_dialog=None, payout_stat_data=None)