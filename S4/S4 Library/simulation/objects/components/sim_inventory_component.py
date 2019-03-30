from protocolbuffers import FileSerialization_pb2
import weakref
from animation.posture_manifest_constants import STAND_OR_SIT_CONSTRAINT
from objects.components import componentmethod, types
from objects.components.inventory import InventoryComponent
from objects.components.inventory_enums import InventoryType
from objects.components.inventory_item import InventoryItemComponent
from objects.mixins import ProvidedAffordanceData, AffordanceCacheMixin
from objects.object_enums import ItemLocation
import services
import sims4.log
logger = sims4.log.Logger('Inventory', default_owner='tingyul')

class SimInventoryComponent(InventoryComponent, AffordanceCacheMixin, component_name=types.INVENTORY_COMPONENT):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._shelved_objects = None
        self._object_providing_affordances = None

    @property
    def inventory_type(self):
        return InventoryType.SIM

    @property
    def default_item_location(self):
        return ItemLocation.SIM_INVENTORY

    @componentmethod
    def get_inventory_access_constraint(self, sim, is_put, carry_target, use_owner_as_target_for_resolver=False):
        return STAND_OR_SIT_CONSTRAINT

    @componentmethod
    def get_inventory_access_animation(self, *args, **kwargs):
        pass

    def can_add(self, obj, hidden=False):
        if self.owner.sim_info.is_pet:
            return False
        return super().can_add(obj, hidden=hidden)

    @property
    def allow_ui(self):
        return self.owner.household is services.active_household()

    def should_save_parented_item_to_inventory(self, obj):
        return self.can_add(obj) and self.owner.household.id == obj.get_household_owner_id()

    def get_shelved_object_count(self):
        if self._shelved_objects:
            return len(self._shelved_objects.objects)
        return 0

    def _on_save_items(self, object_list):
        if self._shelved_objects is None:
            return
        if not self.owner.is_player_sim:
            return
        if self.owner.household.id == services.active_household_id():
            return
        logger.info('Merging Inventory {} (size: {}) with saved inventory {}.', self, len(self), self.get_shelved_object_count())
        for shelved_obj in self._shelved_objects.objects:
            object_list.objects.append(shelved_obj)

    def _on_load_items(self):
        logger.info('Loaded {}. #Created: {}. #Shelved: {}.', self, len(self), self.get_shelved_object_count())

    def _load_item(self, definition_id, obj_data):
        if self._should_create_object(definition_id):
            self._create_inventory_object(definition_id, obj_data)
        else:
            if self._shelved_objects is None:
                self._shelved_objects = FileSerialization_pb2.ObjectList()
            self._shelved_objects.objects.append(obj_data)

    def _update_provided_affordances(self, obj):
        provided_affordances = []
        for provided_affordance in obj.inventoryitem_component.target_super_affordances:
            provided_affordance_data = ProvidedAffordanceData(provided_affordance.affordance, provided_affordance.object_filter, provided_affordance.allow_self)
            provided_affordances.append(provided_affordance_data)
        self.add_to_affordance_caches(obj.inventoryitem_component.super_affordances, provided_affordances)

    @componentmethod
    def get_super_affordance_availability_gen(self):
        yield from self.get_cached_super_affordances_gen()

    @componentmethod
    def get_target_super_affordance_availability_gen(self, context, target):
        yield from self.get_cached_target_super_affordances_gen(context, target)

    @componentmethod
    def get_target_provided_affordances_data_gen(self):
        yield from self.get_cached_target_provided_affordances_data_gen()

    def get_provided_super_affordances(self):
        affordances = set()
        target_affordances = list()
        if self._object_providing_affordances is not None:
            for obj in self._object_providing_affordances:
                affordances.update(obj.inventoryitem_component.super_affordances)
                for provided_affordance in obj.inventoryitem_component.target_super_affordances:
                    provided_affordance_data = ProvidedAffordanceData(provided_affordance.affordance, provided_affordance.object_filter, provided_affordance.allow_self)
                    target_affordances.append(provided_affordance_data)
        return (affordances, target_affordances)

    def get_sim_info_from_provider(self):
        return self.owner.sim_info

    def add_affordance_provider_object(self, obj):
        if self._object_providing_affordances is None:
            self._object_providing_affordances = weakref.WeakSet()
        self._object_providing_affordances.add(obj)
        self._update_provided_affordances(obj)

    def remove_affordance_provider_object(self, obj):
        if self._object_providing_affordances is not None:
            self._object_providing_affordances.remove(obj)
            if not self._object_providing_affordances:
                self._object_providing_affordances = None
            self.update_affordance_caches()

    def _should_create_object(self, definition_id):
        if self.owner.household.id == services.active_household_id():
            return True
        elif InventoryItemComponent.should_item_be_removed_from_inventory(definition_id):
            return False
        return True
