from interactions.base.picker_interaction import PickerSuperInteraction
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.tunable import TunableEnumEntry, OptionalTunable
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import flexmethod
from traits.trait_type import TraitType
from ui.ui_dialog_picker import ObjectPickerRow
import services
import sims4

class TraitTypePickerSuperInteraction(PickerSuperInteraction):
    INSTANCE_TUNABLES = {'trait_type': TunableEnumEntry(description='\n            The type of traits to display in this picker.\n            ', tunable_type=TraitType, default=TraitType.PERSONALITY, tuning_group=GroupNames.PICKERTUNING), 'disabled_row_tooltip': OptionalTunable(description='\n            If enabled, the tooltip to display if the row is disabled.\n            ', tunable=TunableLocalizedStringFactory(), tuning_group=GroupNames.PICKERTUNING)}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._equipped_traits = set()

    def _run_interaction_gen(self, timeline):
        self._show_picker_dialog(self.sim, target_sim=self.sim)
        return True
        yield

    @classmethod
    def _trait_selection_gen(cls, target):
        trait_manager = services.get_instance_manager(sims4.resources.Types.TRAIT)
        for trait in trait_manager.types.values():
            if trait.trait_type == cls.trait_type:
                yield trait

    @flexmethod
    def picker_rows_gen(cls, inst, target, context, **kwargs):
        trait_tracker = target.sim_info.trait_tracker
        for trait in cls._trait_selection_gen(target):
            is_selected = trait_tracker.has_trait(trait)
            if not not is_selected and inst is not None:
                inst._equipped_traits.add(trait)
            is_enabled = True
            is_enabled = trait_tracker.can_add_trait(trait)
            row_tooltip = None
            row_tooltip = cls.disabled_row_tooltip
            row = ObjectPickerRow(name=trait.display_name(target), row_description=trait.trait_description(target), icon=trait.icon, tag=trait, is_selected=is_selected, is_enable=is_enabled, row_tooltip=row_tooltip)
            yield row

    def _update_traits(self, selected_traits):
        traits_to_remove = self._equipped_traits - selected_traits
        for trait in traits_to_remove:
            self.target.sim_info.remove_trait(trait)
        traits_to_add = selected_traits - self._equipped_traits
        for trait in traits_to_add:
            self.target.sim_info.add_trait(trait)

    def on_choice_selected(self, choice_tag, **kwargs):
        selected_traits = set((choice_tag,))
        self._update_traits(selected_traits)

    def on_multi_choice_selected(self, choice_tags, **kwargs):
        selected_traits = set(choice_tags)
        self._update_traits(selected_traits)
