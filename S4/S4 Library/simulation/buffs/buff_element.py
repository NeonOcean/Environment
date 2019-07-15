from buffs.tunable import TunablePackSafeBuffReference
from interactions.utils.interaction_elements import XevtTriggeredElement
import sims4.log
logger = sims4.log.Logger('Buffs')

class BuffFireAndForgetElement(XevtTriggeredElement):

    @staticmethod
    def _verify_tunable_callback(cls, tunable_name, source, buff, success_chance, timing):
        if buff.buff_type._temporary_commodity_info is None:
            logger.error('BuffFireAndForgetElement: {} has a buff element with a buff {} without a temporary commodity tuned.', cls, buff.buff_type)

    FACTORY_TUNABLES = {'buff': TunablePackSafeBuffReference(description='\n            A buff to be added to the Sim.\n            '), 'verify_tunable_callback': _verify_tunable_callback}

    def _do_behavior(self, *args, **kwargs):
        if self.buff.buff_type is None:
            return
        self.interaction.sim.add_buff_from_op(self.buff.buff_type, buff_reason=self.buff.buff_reason)
