import collections
import time
from protocolbuffers import FileSerialization_pb2
from build_buy import _buildbuy
from objects.gallery_tuning import ContentSource
from objects.object_enums import ItemLocation
from relationships import global_relationship_tuning
from sims.fixup.sim_info_fixup_action import SimInfoFixupActionTiming
from sims4.utils import classproperty
from singletons import DEFAULT
import build_buy
import id_generator
import indexed_manager
import objects.object_manager
import persistence_error_types
import server.account
import services
import sims.household
import sims4.log
logger = sims4.log.Logger('HouseholdManager')

class HouseholdFixupHelper:

    def __init__(self):
        self._households_sharing_sims = set()

    def add_shared_sim_household(self, household):
        self._households_sharing_sims.add(household)

    def fix_shared_sim_households(self):
        for household in self._households_sharing_sims:
            if not household.destroy_household_if_empty():
                household.handle_adultless_household(skip_hidden=True, skip_premade=True)

class HouseholdManager(objects.object_manager.DistributableObjectManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._loaded = False
        self._save_slot_data = None
        self._pending_household_funds = collections.defaultdict(list)
        self._pending_transfers = {}

    @classproperty
    def save_error_code(cls):
        return persistence_error_types.ErrorCodes.SERVICE_SAVE_FAILED_HOUSEHOLD_MANAGER

    def create_household(self, account, starting_funds=DEFAULT):
        new_household = sims.household.Household(account, starting_funds)
        self.add(new_household)
        return new_household

    def load_households(self):
        if self._loaded:
            return
        if indexed_manager.capture_load_times:
            time_stamp = time.time()
        fixup_helper = HouseholdFixupHelper()
        business_service = services.business_service()
        for household_proto in services.get_persistence_service().all_household_protos():
            household_id = household_proto.household_id
            household = self.get(household_id)
            if household is None:
                household = self._load_household_from_household_proto(household_proto, fixup_helper=fixup_helper)
                business_service.load_legacy_data(household, household_proto)
        fixup_helper.fix_shared_sim_households()
        for household_id in self._pending_household_funds.keys():
            logger.error('Household {} has pending funds leftover from BB after all households were loaded.', household_id, owner='camilogarcia')
        self._pending_household_funds = None
        for sim_info in services.sim_info_manager().get_all():
            sim_info.on_all_sim_infos_loaded()
            sim_info.set_default_data()
        if indexed_manager.capture_load_times:
            elapsed_time = time.time() - time_stamp
            indexed_manager.object_load_times['household'] = elapsed_time
        self._loaded = True

    def load_household(self, household_id):
        return self._load_household(household_id)

    def _load_household(self, household_id):
        household = self.get(household_id)
        if household is not None:
            for sim_info in household.sim_info_gen():
                zone_id = services.current_zone_id()
                if sim_info.zone_id != zone_id:
                    householdProto = services.get_persistence_service().get_household_proto_buff(household_id)
                    if householdProto is None:
                        logger.error('unable to find household with household id {}'.household_id)
                        return
                    found_sim = False
                    if householdProto.sims.ids:
                        for sim_id in householdProto.sims.ids:
                            if sim_id == sim_info.sim_id:
                                found_sim = True
                                break
                    if found_sim:
                        sim_proto = services.get_persistence_service().get_sim_proto_buff(sim_id)
                        sim_info.load_sim_info(sim_proto)
            return household
        logger.info('Starting to load household id = {0}', household_id)
        household_proto = services.get_persistence_service().get_household_proto_buff(household_id)
        if household_proto is None:
            sims4.log.error('Persistence', 'Household proto could not be found id = {0}', household_id)
            return
        household = self._load_household_from_household_proto(household_proto)
        return household

    def _load_household_from_household_proto(self, household_proto, fixup_helper=None):
        account = services.account_service().get_account_by_id(household_proto.account_id, try_load_account=True)
        if account is None:
            sims4.log.error('Persistence', "Household account doesn't exist in account ids. Creating temp account", owner='yshan')
            account = server.account.Account(household_proto.account_id, 'TempPersonaName')
        household = sims.household.Household(account)
        resend_sim_infos = household.load_data(household_proto, fixup_helper)
        logger.info('Household loaded. name:{:20} id:{:10} #sim_infos:{:2}', household.name, household.id, len(household))
        self.add(household)
        if resend_sim_infos:
            household.resend_sim_infos()
        household.initialize_sim_infos()
        if household is services.client_manager().get_first_client().household:
            for sim_info in household.sim_info_gen():
                for other_info in household.sim_info_gen():
                    if sim_info is not other_info:
                        relationship_service = services.relationship_service()
                        if relationship_service.has_bit(sim_info.id, other_info.id, global_relationship_tuning.RelationshipGlobalTuning.NEIGHBOR_RELATIONSHIP_BIT):
                            relationship_service.remove_relationship_bit(sim_info.id, other_info.id, global_relationship_tuning.RelationshipGlobalTuning.NEIGHBOR_RELATIONSHIP_BIT)
            household.bills_manager.sanitize_household_inventory()
        if self._pending_household_funds is not None:
            pending_funds_reasons = self._pending_household_funds.get(household.id)
            if pending_funds_reasons is not None:
                del self._pending_household_funds[household.id]
                for (fund, reason) in pending_funds_reasons:
                    household.funds.add(fund, reason, None)
        return household

    def switch_sim_household(self, sim_info, target_sim_info=None):
        active_household = services.active_household()
        starting_household = sim_info.household
        destination_household = active_household if target_sim_info is None else target_sim_info.household
        self.switch_sim_from_household_to_target_household(sim_info, starting_household, destination_household)

    def switch_sim_from_household_to_target_household(self, sim_info, starting_household, destination_household, destroy_if_empty_household=True):
        active_household = services.active_household()
        if services.hidden_sim_service().is_hidden(sim_info.id):
            services.hidden_sim_service().unhide(sim_info.id)
        if starting_household is destination_household:
            logger.error('Trying to run AddToHousehold basic extra on a sim who is already in the destination household.')
            return False
        if not destination_household.can_add_sim_info(sim_info):
            logger.error('Trying to run AddToHousehold basic extra when there is no room in the destination household.')
            return False
        starting_household.remove_sim_info(sim_info, destroy_if_empty_household=destroy_if_empty_household, assign_to_none=False)
        destination_household.add_sim_info_to_household(sim_info)
        client = services.client_manager().get_first_client()
        if destination_household is active_household:
            client.add_selectable_sim_info(sim_info)
            sim_info.apply_fixup_actions(SimInfoFixupActionTiming.ON_ADDED_TO_ACTIVE_HOUSEHOLD)
        else:
            client.remove_selectable_sim_info(sim_info)
        if sim_info.career_tracker is not None:
            sim_info.career_tracker.remove_invalid_careers()
        sim = sim_info.get_sim_instance()
        if sim is not None:
            sim.update_intended_position_on_active_lot(update_ui=True)
            situation_manager = services.get_zone_situation_manager()
            for situation in situation_manager.get_situations_sim_is_in(sim):
                if destination_household is active_household and situation.is_user_facing:
                    continue
                situation_manager.remove_sim_from_situation(sim, situation.id)
            services.daycare_service().on_sim_spawn(sim_info)
        return True

    def is_household_stored_in_any_neighborhood_proto(self, household_id):
        for neighborhood_proto in services.get_persistence_service().get_neighborhoods_proto_buf_gen():
            if any(household_id == household_account_proto.household_id for household_account_proto in neighborhood_proto.npc_households):
                return True
        return False

    def get_by_sim_id(self, sim_id):
        for house in self._objects.values():
            if house.sim_in_household(sim_id):
                return house

    def save(self, **kwargs):
        households = self.get_all()
        for household in households:
            household.save_data()

    def on_all_households_and_sim_infos_loaded(self, client):
        for household in self.get_all():
            household.on_all_households_and_sim_infos_loaded()

    def on_client_disconnect(self, client):
        for household in self.get_all():
            household.on_client_disconnect()

    def on_zone_load(self):
        for household in self.get_all():
            household.on_zone_load()

    def on_zone_unload(self):
        for household in self.get_all():
            household.on_zone_unload()

    @staticmethod
    def get_active_sim_home_zone_id():
        client = services.client_manager().get_first_client()
        if client is not None:
            active_sim = client.active_sim
            if active_sim is not None:
                household = active_sim.household
                if household is not None:
                    return household.home_zone_id

    def try_add_pending_household_funds(self, household_id, funds, reason):
        if self._pending_household_funds is None:
            return False
        self._pending_household_funds[household_id].append((funds, reason))
        return True

    def add_pending_transfer(self, household_id, transfer_proto):
        self._pending_transfers[household_id] = transfer_proto

    def get_pending_transfer(self, household_id):
        pending_transfer_data = self._pending_transfers.get(household_id, None)
        return pending_transfer_data

    def remove_pending_transfer(self, household_id):
        if household_id in self._pending_transfers:
            del self._pending_transfers[household_id]

    def transfer_household_inventory(self, source_household, target_household):
        active_household = services.active_household()
        target_household.copy_rewards_inventory_from_household(source_household)
        if source_household is active_household:
            self.transfer_active_household_inventory(source_household, target_household)
        elif target_household is active_household:
            self.transfer_inactive_household_inventory(source_household, target_household)
        else:
            logger.error("Trying to transfer household inventory from one inactive household to another, we currently don't support that. Feel free to add if we come up with a use case. S={}, T={}", source_household, target_household)

    def transfer_active_household_inventory(self, source_household, target_household):
        inventory_available = build_buy.is_household_inventory_available(target_household.id)
        source_household_msg = services.get_persistence_service().get_household_proto_buff(source_household.id)
        target_household_msg = services.get_persistence_service().get_household_proto_buff(target_household.id)
        object_manager = services.object_manager()
        object_ids = build_buy.get_object_ids_in_household_inventory(source_household.id)
        for object_id in object_ids:
            object_data_raw = _buildbuy.get_object_data_in_household_inventory(object_id, source_household.id)
            if object_data_raw is None:
                continue
            obj = self._create_object_from_raw_inv_data(object_id, object_data_raw)
            self._transfer_object(target_household, obj, inventory_available, target_household_msg)
        for object_data in source_household_msg.inventory.objects:
            if object_data.object_id in object_ids:
                continue
            obj = object_manager.get(object_data.object_id)
            if obj is None:
                obj = self._create_object_from_object_data(object_data.object_id, object_data)
            if obj is not None:
                self._transfer_object(target_household, obj, inventory_available, target_household_msg)

    def _transfer_object(self, target_household, obj, inventory_available, target_household_msg):
        obj.set_household_owner_id(target_household.id)
        if inventory_available:
            build_buy.move_object_to_household_inventory(obj)
        else:
            if target_household_msg is not None:
                object_data = obj.save_object(target_household_msg.inventory.objects)
                if object_data is not None:
                    object_data.object_id = id_generator.generate_object_id()
            obj.destroy(cause='Merge/Transfer to New Household Inventory')

    def transfer_inactive_household_inventory(self, source_household, target_household):
        if build_buy.is_household_inventory_available(source_household.id):
            object_ids = build_buy.get_object_ids_in_household_inventory(source_household.id)
            for object_id in object_ids:
                object_data_raw = _buildbuy.get_object_data_in_household_inventory(object_id, source_household.id)
                obj = self._create_object_from_raw_inv_data(object_id, object_data_raw)
                build_buy.remove_object_from_household_inventory(object_id, source_household)
                obj.set_household_owner_id(target_household.id)
                build_buy.move_object_to_household_inventory(obj)
            else:
                del household_msg.inventory.objects[:]
        else:
            household_msg = services.get_persistence_service().get_household_proto_buff(source_household.id)
            if household_msg is not None:
                for object_msg in household_msg.inventory.objects:
                    obj = self._create_object_from_object_data(object_msg.object_id, object_msg)
                    obj.set_household_owner_id(target_household.id)
                    build_buy.move_object_to_household_inventory(obj)
                del household_msg.inventory.objects[:]

    def _create_object_from_raw_inv_data(self, object_id, raw_inv_data):
        object_data = FileSerialization_pb2.ObjectData()
        object_data.ParseFromString(raw_inv_data)
        return self._create_object_from_object_data(object_id, object_data)

    def _create_object_from_object_data(self, object_id, object_data):
        obj = objects.system.create_object(object_data.guid, obj_id=object_id, obj_state=object_data.state_index)
        return obj
