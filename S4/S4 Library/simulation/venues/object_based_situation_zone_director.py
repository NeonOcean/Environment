from _weakrefset import WeakSet
from objects.components.types import SITUATION_SCHEDULER_COMPONENT
from scheduler import SituationWeeklySchedule
from sims4.tuning.tunable import TunableMapping, TunableTuple, TunableRange, Tunable
from tag import TunableTag
import services
import sims4.log
logger = sims4.log.Logger('ZoneDirector', default_owner='mkartika')

class ObjectBasedSituationZoneDirectorMixin:
    INSTANCE_TUNABLES = {'object_based_situations_schedule': TunableMapping(description='\n            Mapping of object tag to situations schedule. \n            When the object in the tag is exist on the zone lot, the situations\n            will be spawned based on the schedule.\n            ', key_type=TunableTag(description='\n                An object tag. If the object exist on the zone lot, situations\n                will be scheduled.\n                ', filter_prefixes=('func',)), value_type=TunableTuple(description='\n                Data associated with situations schedule.\n                ', affected_object_cap=TunableRange(description='\n                    Specify the maximum number of objects on the zone lot that \n                    can schedule the situations.\n                    ', tunable_type=int, minimum=1, default=1), situation_schedule=SituationWeeklySchedule.TunableFactory(description='\n                    The schedule to trigger the different situations.\n                    ', schedule_entry_data={'pack_safe': True}), schedule_immediate=Tunable(description='\n                    This controls the behavior of scheduler if the current time\n                    happens to fall within a schedule entry. If this is True, \n                    a start_callback will trigger immediately for that entry.\n                    If False, the next start_callback will occur on the next entry.\n                    ', tunable_type=bool, default=False), consider_off_lot_objects=Tunable(description='\n                    If True, consider all objects in lot and the open street for\n                    this object situation. If False, only consider objects on\n                    the active lot.\n                    ', tunable_type=bool, default=True)))}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.affected_objects_map = {}

    def create_situations_during_zone_spin_up(self):
        super().create_situations_during_zone_spin_up()
        self._cleanup_affected_objects()
        self._load_affected_objects()
        self._setup_affected_objects()

    def on_exit_buildbuy(self):
        super().on_exit_buildbuy()
        self._setup_affected_objects()

    def _cleanup_affected_objects(self):
        object_tags = self.object_based_situations_schedule.keys()
        object_manager = services.object_manager()
        for obj in object_manager.get_valid_objects_gen():
            if obj.has_component(SITUATION_SCHEDULER_COMPONENT):
                if not obj.has_any_tag(object_tags):
                    obj.remove_component(SITUATION_SCHEDULER_COMPONENT)

    def _load_affected_objects(self):
        object_manager = services.object_manager()
        for (object_tag, data) in self.object_based_situations_schedule.items():
            object_cap = data.affected_object_cap
            tagged_objects = list(object_manager.get_objects_with_tag_gen(object_tag))
            if not tagged_objects:
                continue
            affected_objects = []
            for obj in tagged_objects:
                if not obj.has_component(SITUATION_SCHEDULER_COMPONENT):
                    continue
                if len(affected_objects) == object_cap:
                    obj.remove_component(SITUATION_SCHEDULER_COMPONENT)
                else:
                    affected_objects.append(obj)
                    obj.set_situation_scheduler(data.situation_schedule(start_callback=self._start_situations, schedule_immediate=data.schedule_immediate, extra_data=obj))
            if affected_objects:
                self.affected_objects_map[object_tag] = WeakSet(affected_objects)

    def _setup_affected_objects(self):
        object_manager = services.object_manager()
        for (object_tag, data) in self.object_based_situations_schedule.items():
            object_cap = data.affected_object_cap
            if object_tag in self.affected_objects_map and len(self.affected_objects_map[object_tag]) >= object_cap:
                continue
            tagged_objects = []
            if data.consider_off_lot_objects:
                tagged_objects = list(object_manager.get_objects_with_tag_gen(object_tag))
            else:
                tagged_objects = [obj for obj in object_manager.get_objects_with_tag_gen(object_tag) if obj.is_on_active_lot()]
            if not tagged_objects:
                continue
            if object_tag not in self.affected_objects_map:
                self.affected_objects_map[object_tag] = WeakSet()
            affected_objects = self.affected_objects_map[object_tag]
            if len(affected_objects) == len(tagged_objects):
                continue
            for obj in tagged_objects:
                if obj in affected_objects:
                    continue
                obj.add_dynamic_component(SITUATION_SCHEDULER_COMPONENT, scheduler=data.situation_schedule(start_callback=self._start_situations, schedule_immediate=data.schedule_immediate, extra_data=obj))
                affected_objects.add(obj)
                if len(affected_objects) >= object_cap:
                    break

    def _start_situations(self, scheduler, alarm_data, obj):
        obj.create_situation(alarm_data.entry.situation)
