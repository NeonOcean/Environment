import collections
from protocolbuffers import UI_pb2
from protocolbuffers import SimObjectAttributes_pb2 as protocols
from protocolbuffers.DistributorOps_pb2 import Operation
from crafting.crafting_interactions import StartCraftingMixin
from distributor.ops import GenericProtocolBufferOp
from distributor.rollback import ProtocolBufferRollback
from distributor.shared_messages import IconInfoData, create_icon_info_msg
from distributor.system import Distributor
from objects import ALL_HIDDEN_REASONS
from sims.sim_info_lod import SimInfoLODLevel
from sims.sim_info_tracker import SimInfoTracker
from sims4.localization import LocalizationHelperTuning
from sims4.utils import classproperty
from ui.notebook_tuning import NotebookTuning
import services
import sims4.resources

class NotebookTrackerSimInfo(SimInfoTracker):

    def __init__(self, sim_info):
        self._owner = sim_info
        self._notebook_entries = collections.defaultdict(list)
        self._notebook_entry_catsubcat_cache = collections.defaultdict(set)

    def clear_notebook_tracker(self):
        self._notebook_entries.clear()
        self._notebook_entry_catsubcat_cache.clear()

    def unlock_entry(self, notebook_entry, from_load=False):
        notebook_entries = self._notebook_entries.get(notebook_entry.subcategory_id)
        if notebook_entries and notebook_entry.has_identical_entries(notebook_entries):
            return
        notebook_entry.new_entry = True
        self._notebook_entries[notebook_entry.subcategory_id].append(notebook_entry)
        category_id = NotebookTuning.get_category_id(notebook_entry.subcategory_id)
        self._notebook_entry_catsubcat_cache[category_id].add(notebook_entry.subcategory_id)
        if not from_load:
            NotebookTuning.show_entry_unlocked_notification(notebook_entry.category_id, notebook_entry.subcategory_id, self._owner)

    def remove_entries_by_subcategory(self, subcategory_id):
        category_id = NotebookTuning.get_category_id(subcategory_id)
        self._notebook_entries.pop(subcategory_id, None)
        category_cache = self._notebook_entry_catsubcat_cache.get(category_id)
        if category_cache and subcategory_id in category_cache:
            category_cache.remove(subcategory_id)
            if not category_cache:
                self._notebook_entry_catsubcat_cache.pop(category_id, None)

    def remove_entry_by_reference(self, subcategory_id, entry):
        notebook_entries = self._notebook_entries.get(subcategory_id)
        if not notebook_entries:
            return
        entries_to_remove = set(entry_inst for entry_inst in notebook_entries if isinstance(entry_inst, entry))
        for to_remove in entries_to_remove:
            notebook_entries.remove(to_remove)
        if not notebook_entries:
            self.remove_entries_by_subcategory(subcategory_id)

    def generate_notebook_information(self):
        msg = UI_pb2.NotebookView()
        if self._notebook_entries:
            ingredient_cache = StartCraftingMixin.get_default_candidate_ingredients(self._owner.get_sim_instance())
        for category_id in self._notebook_entry_catsubcat_cache.keys():
            with ProtocolBufferRollback(msg.categories) as notebook_category_message:
                category_tuning = NotebookTuning.NOTEBOOK_CATEGORY_MAPPING[category_id]
                notebook_category_message.category_name = category_tuning.category_name
                notebook_category_message.category_icon = create_icon_info_msg(IconInfoData(icon_resource=category_tuning.category_icon))
                valid_subcategories = self._notebook_entry_catsubcat_cache[category_id]
                for subcategory_id in valid_subcategories:
                    with ProtocolBufferRollback(notebook_category_message.subcategories) as notebook_subcategory_message:
                        subcategory_tuning = category_tuning.subcategories[subcategory_id]
                        notebook_subcategory_message.subcategory_name = subcategory_tuning.subcategory_name
                        notebook_subcategory_message.subcategory_icon = create_icon_info_msg(IconInfoData(icon_resource=subcategory_tuning.subcategory_icon))
                        notebook_subcategory_message.subcategory_tooltip = subcategory_tuning.subcategory_tooltip
                        notebook_subcategory_message.entry_type = subcategory_tuning.format_type
                        if subcategory_tuning.show_max_entries is not None:
                            notebook_subcategory_message.max_num_entries = subcategory_tuning.show_max_entries
                        subcategory_entries = self._notebook_entries[subcategory_id]
                        for entry in subcategory_entries:
                            if entry is None:
                                continue
                            if entry.is_definition_based():
                                definition_data = entry.get_definition_notebook_data(ingredient_cache=ingredient_cache)
                                if definition_data is not None:
                                    self._fill_notebook_entry_data(notebook_subcategory_message, definition_data, True, entry.new_entry)
                            else:
                                self._fill_notebook_entry_data(notebook_subcategory_message, entry, False, entry.new_entry)
                            entry.new_entry = False
        op = GenericProtocolBufferOp(Operation.NOTEBOOK_VIEW, msg)
        Distributor.instance().add_op_with_no_owner(op)

    def _fill_notebook_entry_data(self, notebook_subcategory_message, entry, definition_based, new_entry):
        active_sim = self._owner.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
        with ProtocolBufferRollback(notebook_subcategory_message.entries) as notebook_entry_message:
            notebook_entry_message.entry_message = entry.entry_text
            if entry.entry_icon_info_data is not None:
                notebook_entry_message.entry_icon = create_icon_info_msg(entry.entry_icon_info_data)
            if entry.entry_tooltip is not None:
                notebook_entry_message.entry_tooltip = entry.entry_tooltip
            notebook_entry_message.new_entry = new_entry
            if entry.entry_sublist is not None:
                for sublist_data in entry.entry_sublist:
                    with ProtocolBufferRollback(notebook_entry_message.entry_list) as notebook_entry_list_message:
                        if sublist_data.is_ingredient:
                            item_message = sublist_data.object_display_name
                        else:
                            item_message = LocalizationHelperTuning.get_object_name(sublist_data.object_definition)
                        notebook_entry_list_message.item_message = item_message
                        if active_sim is not None and sublist_data.num_objects_required > 0:
                            if sublist_data.is_ingredient:
                                notebook_entry_list_message.item_count = sublist_data.item_count
                            else:
                                notebook_entry_list_message.item_count = active_sim.inventory_component.get_count(sublist_data.object_definition)
                        else:
                            notebook_entry_list_message.item_count = 0
                        notebook_entry_list_message.item_total = sublist_data.num_objects_required

    def save_notebook(self):
        notebook_tracker_data = protocols.PersistableNotebookTracker()
        for cateogry_list in self._notebook_entries.values():
            for entry in cateogry_list:
                with ProtocolBufferRollback(notebook_tracker_data.notebook_entries) as entry_data:
                    entry_data.tuning_reference_id = entry.guid64
                    entry_data.new_entry = entry.new_entry
                    if entry.is_definition_based():
                        entry_data.object_entry_ids.extend(entry.entry_object_definition_ids)
                        if entry.recipe_object_definition_id is not None:
                            entry_data.object_recipe_id = entry.recipe_object_definition_id
        return notebook_tracker_data

    def load_notebook(self, notebook_proto_msg):
        manager = services.get_instance_manager(sims4.resources.Types.NOTEBOOK_ENTRY)
        for notebook_data in notebook_proto_msg.notebook_entries:
            tuning_reference_id = notebook_data.tuning_reference_id
            tuning_instance = manager.get(tuning_reference_id)
            if tuning_instance is None:
                continue
            object_entry_ids = list(notebook_data.object_entry_ids)
            object_recipe_id = notebook_data.object_recipe_id
            self._owner.notebook_tracker.unlock_entry(tuning_instance(object_recipe_id, object_entry_ids, notebook_data.new_entry), from_load=True)

    @classproperty
    def _tracker_lod_threshold(cls):
        return SimInfoLODLevel.FULL

    def on_lod_update(self, old_lod, new_lod):
        if new_lod < self._tracker_lod_threshold:
            self.clear_notebook_tracker()
        elif old_lod < self._tracker_lod_threshold:
            sim_msg = services.get_persistence_service().get_sim_proto_buff(self._owner.id)
            if sim_msg is not None:
                self.load_notebook(sim_msg.attributes.notebook_tracker)
