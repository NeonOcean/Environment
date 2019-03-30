from protocolbuffers.DistributorOps_pb2 import SetWhimBucks
from date_and_time import create_time_span
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableRange, TunableRate, TunableSimMinute
from sims4.tuning.tunable_base import RateDescriptions
import alarms

class SatisfactionPointMultiplierModifier(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'score_multiplier': TunableRange(description="\n            A multiplier to apply to a Whim's score.\n            ", tunable_type=float, minimum=0, default=1)}

    def apply_modifier(self, sim_info, modifier_owner):
        whims_tracker = sim_info.whim_tracker
        whims_tracker.add_score_multiplier(self.score_multiplier)

    def remove_modifier(self, sim_info, modifier_owner):
        whims_tracker = sim_info.whim_tracker
        whims_tracker.remove_score_multiplier(self.score_multiplier)

class SatisfactionPointPeriodicGainModifier(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'score_rate': TunableRate(description='\n            The rate at which Sims gain Satisfaction Points.\n            ', rate_description=RateDescriptions.PER_SIM_MINUTE, tunable_type=int, default=1), 'score_interval': TunableSimMinute(description='\n            How often satisfaction points are awarded. Since awarding points has\n            a UI treatment, this affects visible feedback to the player.\n            ', default=8)}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._alarm_handles = {}

    def apply_modifier(self, sim_info, modifier_owner):
        score = int(self.score_interval*self.score_rate)

        def _on_award_satisfaction_points(_):
            sim_info.add_whim_bucks(score, SetWhimBucks.WHIM)

        alarm_handle_key = (sim_info, modifier_owner)
        alarm_handle = alarms.add_alarm(self, create_time_span(minutes=self.score_interval), _on_award_satisfaction_points, repeating=True)
        self._alarm_handles[alarm_handle_key] = alarm_handle

    def remove_modifier(self, sim_info, modifier_owner):
        alarm_handle_key = (sim_info, modifier_owner)
        alarm_handle = self._alarm_handles.pop(alarm_handle_key)
        alarms.cancel_alarm(alarm_handle)
