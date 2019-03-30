from drama_scheduler.drama_node import BaseDramaNode, CooldownOption
from drama_scheduler.drama_node_types import DramaNodeType
from event_testing.resolver import SingleSimResolver
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable import TunableReference, OptionalTunable
from sims4.utils import classproperty
import id_generator
import services
import sims4.log
logger = sims4.log.Logger('PickerDramaNode', default_owner='bosee')

class PickerDramaNode(BaseDramaNode):
    INSTANCE_TUNABLES = {'node_to_run': BaseDramaNode.TunableReference(description='\n            Drama node to schedule should the player pick this to run.\n            '), 'visibility_tests': OptionalTunable(description='\n            If set, run this test on owner if owner is available.\n            If owner is not available, not tests will be run.\n            ', tunable=TunableReference(description='\n                A set of tests to run on the owner to let us know if we should\n                show this node to the owner.\n                ', manager=services.get_instance_manager(sims4.resources.Types.SNIPPET), class_restrictions=('TestSetInstance',)))}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_node = None

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
        services.drama_scheduler_service().schedule_node(self.node_to_run, SingleSimResolver(owner), specific_time=self._saved_node.get_picker_schedule_time(), drama_inst=self._saved_node)

    def create_picker_row(self, owner=None, **kwargs):
        uid = id_generator.generate_object_id()
        self._saved_node = self.node_to_run(uid)
        if owner is not None and self.visibility_tests is not None:
            resolver = SingleSimResolver(owner)
            if not self.visibility_tests(resolver):
                return
        picker_row = self._saved_node.create_picker_row(owner=owner)
        picker_row.tag = self
        return picker_row

    REMOVE_INSTANCE_TUNABLES = ('receiver_sim', 'sender_sim_info', 'picked_sim_info')

lock_instance_tunables(PickerDramaNode, allow_during_work_hours=True, cooldown_option=CooldownOption.ON_SCHEDULE)