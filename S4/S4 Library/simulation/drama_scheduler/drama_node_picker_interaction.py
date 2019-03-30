from drama_scheduler.drama_node import DramaNodeScoringBucket
from drama_scheduler.drama_node_types import DramaNodeType
from event_testing.resolver import SingleSimResolver
from interactions.base.picker_interaction import PickerSuperInteraction
from interactions.utils.loot import LootActions
from sims4.tuning.tunable import OptionalTunable, TunableEnumEntry, TunableList
from sims4.utils import flexmethod
import services
import sims4.log
logger = sims4.log.Logger('DramaNodePickerInteraction', default_owner='bosee')

class DramaNodePickerInteraction(PickerSuperInteraction):
    INSTANCE_TUNABLES = {'bucket': OptionalTunable(description='\n            If enabled, we only return nodes of this bucket.\n            Drama nodes with no buckets are rejected.\n            ', tunable=TunableEnumEntry(description='\n                Bucket to test against.\n                ', tunable_type=DramaNodeScoringBucket, default=DramaNodeScoringBucket.DEFAULT)), 'loot_when_empty': OptionalTunable(description="\n            If enabled, we run this loot when picker is empty and don't display\n            the empty picker.\n            If disabled, picker will appear empty.\n            ", tunable=TunableList(description='\n                Loot applied if the picker is going to be empty.\n                ', tunable=LootActions.TunableReference(pack_safe=True)))}

    def _run_interaction_gen(self, timeline):
        self._show_picker_dialog(self.target, target_sim=self.target)
        return True

    def _show_picker_dialog(self, owner, **kwargs):
        if self.use_pie_menu():
            return
        dialog = self._create_dialog(owner, **kwargs)
        if self.loot_when_empty is not None and len(dialog.picker_rows) == 0:
            resolver = SingleSimResolver(owner.sim_info)
            for loot in self.loot_when_empty:
                loot.apply_to_resolver(resolver)
        else:
            dialog.show_dialog()

    @flexmethod
    def picker_rows_gen(cls, inst, target, context, **kwargs):
        for drama_node in services.drama_scheduler_service().all_nodes_gen():
            if drama_node.drama_node_type == DramaNodeType.PICKER:
                if not cls.bucket or not drama_node.scoring or drama_node.scoring.bucket != cls.bucket:
                    pass
                else:
                    result = drama_node.create_picker_row(owner=target)
                    if result is not None:
                        yield result

    def on_choice_selected(self, choice_tag, **kwargs):
        if choice_tag is None:
            return
        choice_tag.on_picker_choice(owner=self.sim.sim_info)
