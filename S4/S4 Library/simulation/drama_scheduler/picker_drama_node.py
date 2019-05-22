import elements
from careers.career_gig import Gig
from careers.career_tuning import Career
from drama_scheduler.drama_node import BaseDramaNode, CooldownOption
from drama_scheduler.drama_node_types import DramaNodeType
from event_testing.resolver import SingleSimResolver
from event_testing.tests import TunableTestSet, TunableTestSetWithTooltip
from interactions import ParticipantType
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable import TunableReference, OptionalTunable, TunableVariant, HasTunableSingletonFactory, AutoFactoryInit, Tunable
from sims4.utils import classproperty
import id_generator
import services
import sims4.log
logger = sims4.log.Logger('PickerDramaNode', default_owner='bosee')

class _PickerDramaNodeBehavior(HasTunableSingletonFactory, AutoFactoryInit):

    def create_picker_row(self, owner=None, **kwargs):
        raise NotImplementedError

    def on_picked(self, owner=None):
        raise NotImplementedError

class _ScheduleDramaNodePickerBehavior(_PickerDramaNodeBehavior):
    FACTORY_TUNABLES = {'drama_node': BaseDramaNode.TunableReference(description='\n            Drama node to schedule.\n            ')}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_node = None

    def create_picker_row(self, owner, **kwargs):
        uid = id_generator.generate_object_id()
        self._saved_node = self.drama_node(uid)
        picker_row = self._saved_node.create_picker_row(owner=owner)
        return picker_row

    def on_picked(self, owner=None):
        services.drama_scheduler_service().schedule_node(self.drama_node, SingleSimResolver(owner), specific_time=self._saved_node.get_picker_schedule_time(), drama_inst=self._saved_node)

class _ScheduleCareerGigPickerBehavior(_PickerDramaNodeBehavior):
    FACTORY_TUNABLES = {'career_gig': Gig.TunableReference(description='\n            Career gig to schedule.\n            '), 'allow_add_career': Tunable(description="\n            If tuned, picking this drama node will add the required career\n            if the sim doesn't already have it. If not tuned, trying to add a\n            gig for a career the sim doesn't have will throw an error.\n            ", tunable_type=bool, default=False)}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._scheduled_time = None

    def create_picker_row(self, owner, **kwargs):
        self._owner = owner
        now = services.time_service().sim_now
        time_till_gig = self.career_gig.get_time_until_next_possible_gig(now)
        if time_till_gig is None:
            return
        self._scheduled_time = now + time_till_gig
        picker_row = self.career_gig.create_picker_row(scheduled_time=self._scheduled_time, owner=owner)
        return picker_row

    def on_picked(self, owner=None):
        sim_info = SingleSimResolver(owner).get_participant(ParticipantType.Actor)
        career = sim_info.career_tracker.get_career_by_uid(self.career_gig.career.guid64)
        if career is None:
            if self.allow_add_career:
                sim_info.career_tracker.add_career(self.career_gig.career(sim_info))
            else:
                logger.error('Tried to add gig {} to missing career {} on sim {}', self.career_gig, self.career_gig.career, sim_info)
                return
        sim_info.career_tracker.set_gig(self.career_gig, self._scheduled_time)

class PickerDramaNode(BaseDramaNode, AutoFactoryInit):
    INSTANCE_TUNABLES = {'behavior': TunableVariant(schedule_drama_node=_ScheduleDramaNodePickerBehavior.TunableFactory(description='\n                Drama node to schedule should the player pick this to run.\n                '), schedule_career_gig=_ScheduleCareerGigPickerBehavior.TunableFactory(description='\n                A gig to schedule should the player pick this to run.\n                ')), 'visibility_tests': TunableTestSetWithTooltip(description='\n            Tests that will be run on the picker owner of this PickerDramaNode\n            to determine if this node should appear in a picker.\n            '), 'replace_if_removed': Tunable(description='\n            If True, whenever we remove this node because it was selected in a picker, we will replace it with a new\n            valid node from the same bucket.\n            ', tunable_type=bool, default=False), 'remove_if_picked': Tunable(description="\n            If true, selecting this picker drama node will remove the picker\n            drama node from the drama scheduler and it won't appear in future\n            pickers.\n            ", tunable_type=bool, default=False)}

    @classproperty
    def persist_when_active(cls):
        return False

    @classproperty
    def drama_node_type(cls):
        return DramaNodeType.PICKER

    @classproperty
    def simless(cls):
        return True

    def _run(self):
        return True

    def on_picker_choice(self, owner=None):
        if self.remove_if_picked:
            if self.replace_if_removed:
                selected_time = self.selected_time

                def schedule_new_node(timeline):
                    try:
                        nodes_in_bucket = []
                        for drama_node in services.get_instance_manager(sims4.resources.Types.DRAMA_NODE).get_ordered_types():
                            if drama_node.scoring:
                                if drama_node.scoring.bucket == self.scoring.bucket:
                                    nodes_in_bucket.append(drama_node)
                        yield from services.drama_scheduler_service().score_and_schedule_nodes_gen(nodes_in_bucket, 1, specific_time=selected_time, zone_id=services.current_zone_id(), timeline=timeline)
                    except GeneratorExit:
                        raise
                    except Exception as exception:
                        logger.exception('Exception while replacing a drama node', exc=exception, level=sims4.log.LEVEL_ERROR)
                    finally:
                        self._element = None

                sim_timeline = services.time_service().sim_timeline
                self._element = sim_timeline.schedule(elements.GeneratorElement(schedule_new_node))
            services.drama_scheduler_service().cancel_scheduled_node(self._uid)
        self.behavior.on_picked(owner)

    def create_picker_row(self, owner=None, run_visibility_tests=True, disable_row_if_visibily_tests_fail=False, **kwargs):
        disable_row = False
        tooltip_override = None
        if run_visibility_tests and owner is not None:
            resolver = SingleSimResolver(owner)
            result = self.visibility_tests.run_tests(resolver)
            if not result:
                if disable_row_if_visibily_tests_fail:
                    tooltip_override = result.tooltip
                    disable_row = True
                else:
                    return
        picker_row = self.behavior.create_picker_row(owner=owner)
        if picker_row is not None:
            picker_row.tag = self
            if disable_row:
                picker_row.is_enable = False
                if tooltip_override:
                    picker_row.row_tooltip = tooltip_override
        return picker_row

    REMOVE_INSTANCE_TUNABLES = ('receiver_sim', 'sender_sim_info', 'picked_sim_info')

lock_instance_tunables(PickerDramaNode, allow_during_work_hours=True, cooldown_option=CooldownOption.ON_SCHEDULE)