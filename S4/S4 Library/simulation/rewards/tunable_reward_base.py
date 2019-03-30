from interactions.utils.has_display_text_mixin import HasDisplayTextMixin
from rewards.reward_enums import RewardDestination
from sims4.tuning.tunable import HasTunableFactory

class TunableRewardBase(HasTunableFactory, HasDisplayTextMixin):

    def open_reward(self, sim_info, reward_destination=RewardDestination.HOUSEHOLD):
        raise NotImplementedError

    def valid_reward(self, sim_info):
        return True
