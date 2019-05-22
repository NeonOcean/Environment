from interactions.interaction_finisher import FinishingType
from objects import HiddenReasonFlag, ALL_HIDDEN_REASONS
from sims.daycare import DaycareLiability
import placement
import sims4
logger = sims4.log.Logger('RabbitHoles')
RABBIT_HOLE_LIABILTIY = 'RabbitHoleLiability'

class RabbitHoleLiability(DaycareLiability):
    LIABILITY_TOKEN = RABBIT_HOLE_LIABILTIY

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._interaction = None
        self._has_hidden = False

    def should_transfer(self, continuation):
        return False

    def on_add(self, interaction):
        super().on_add(interaction)
        self._interaction = interaction

    def on_run(self):
        for sim_info in self._sim_infos:
            sim = sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
            if sim is None:
                return
            sim.fade_out()
            sim.hide(HiddenReasonFlag.RABBIT_HOLE)
            sim.client.selectable_sims.notify_dirty()
            valid_sims = (self._interaction.sim, self._interaction.target)
            for interaction in tuple(sim.interaction_refs):
                if interaction not in sim.interaction_refs:
                    continue
                if interaction.sim in valid_sims:
                    continue
                interaction.cancel(FinishingType.OBJECT_CHANGED, cancel_reason_msg='Target Sim went into rabbit hole')
            sim.remove_location_from_quadtree(placement.ItemType.SIM_POSITION)
            sim.remove_location_from_quadtree(placement.ItemType.SIM_INTENDED_POSITION)
            self._has_hidden = True
        super().on_run()

    def release(self):
        if not self._has_hidden:
            return
        for sim_info in self._sim_infos:
            sim = sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
            if sim is None:
                return
            sim.show(HiddenReasonFlag.RABBIT_HOLE)
            sim.client.selectable_sims.notify_dirty()
            sim.add_location_to_quadtree(placement.ItemType.SIM_POSITION)
            sim.fade_in()
            self._has_hidden = False
        super().release()
