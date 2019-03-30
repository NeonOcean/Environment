from collections import namedtuple
from protocolbuffers import SimObjectAttributes_pb2 as protocols
from distributor.rollback import ProtocolBufferRollback
from sims.sim_info_lod import SimInfoLODLevel
from sims.sim_info_tracker import SimInfoTracker
from sims4.tuning.tunable import TunableVariant, TunablePackSafeReference
from sims4.utils import classproperty
import services
import sims4
Unlock = namedtuple('Unlock', ('tuning_class', 'name'))
logger = sims4.log.Logger('UnlockTracker')

class TunableUnlockVariant(TunableVariant):

    def __init__(self, **kwargs):
        super().__init__(unlock_recipe=TunablePackSafeReference(manager=services.get_instance_manager(sims4.resources.Types.RECIPE)), **kwargs)

class UnlockTracker(SimInfoTracker):

    def __init__(self, sim_info):
        self._sim_info = sim_info
        self._unlocks = []

    def add_unlock(self, tuning_class, name):
        if tuning_class is not None:
            self._unlocks.append(Unlock(tuning_class, name))

    def get_unlocks(self, tuning_class):
        if tuning_class is None:
            return []
        return [unlock for unlock in self._unlocks if issubclass(unlock.tuning_class, tuning_class)]

    def is_unlocked(self, tuning_class):
        return any(unlock.tuning_class is tuning_class for unlock in self._unlocks)

    def save_unlock(self):
        unlock_tracker_data = protocols.PersistableUnlockTracker()
        for unlock in self._unlocks:
            with ProtocolBufferRollback(unlock_tracker_data.unlock_data_list) as unlock_data:
                unlock_data.unlock_instance_id = unlock.tuning_class.guid64
                unlock_data.unlock_instance_type = unlock.tuning_class.tuning_manager.TYPE
                if unlock.name is not None:
                    unlock_data.custom_name = unlock.name
        return unlock_tracker_data

    def load_unlock(self, unlock_proto_msg):
        for unlock_data in unlock_proto_msg.unlock_data_list:
            instance_id = unlock_data.unlock_instance_id
            instance_type = sims4.resources.Types(unlock_data.unlock_instance_type)
            manager = services.get_instance_manager(instance_type)
            if manager is None:
                logger.error('Loading: Sim {} fail to get instance manager for unlock item {}, {}', self.owner, instance_id, instance_type, owner='cjiang')
            else:
                tuning_class = manager.get(instance_id)
                if tuning_class is None:
                    logger.info('Trying to load unavailable {} resource: {}', instance_type, instance_id)
                else:
                    self._unlocks.append(Unlock(tuning_class, unlock_data.custom_name))

    @classproperty
    def _tracker_lod_threshold(cls):
        return SimInfoLODLevel.FULL

    def on_lod_update(self, old_lod, new_lod):
        if new_lod < self._tracker_lod_threshold:
            self._unlocks.clear()
        elif old_lod < self._tracker_lod_threshold:
            sim_msg = services.get_persistence_service().get_sim_proto_buff(self._sim_info.id)
            if sim_msg is not None:
                self.load_unlock(sim_msg.attributes.unlock_tracker)
