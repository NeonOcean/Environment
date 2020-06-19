from drama_scheduler.drama_node_types import DramaNodeType
from event_testing.results import TestResult
from event_testing.test_events import TestEvent, cached_test
from interactions import ParticipantTypeSingleSim
from sims4.tuning.tunable import Tunable, OptionalTunable, TunableTuple, TunableReference, HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry, TunableList
import event_testing.test_base
import services
import sims4
logger = sims4.log.Logger('DramaNodeTests', default_owner='jjacobson')

class FestivalRunningTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'drama_node': OptionalTunable(description='\n            If enabled then we will check a specific type of festival drama\n            node otherwise we will look at all of the festival drama nodes.\n            ', tunable=TunableReference(description='\n                Reference to the festival drama node that we want to be running.\n                ', manager=services.get_instance_manager(sims4.resources.Types.DRAMA_NODE), class_restrictions=('FestivalDramaNode',)), enabled_by_default=True), 'check_if_on_festival_street': OptionalTunable(description="\n            If enabled, test against if the player is on the festival's street.\n            ", tunable=Tunable(description="\n                If checked, this test will pass only if the player is on the\n                festival's street. If unchecked, the test will pass only if the\n                player is not on the festival street.\n                ", tunable_type=bool, default=True)), 'valid_time_blocks': TunableTuple(description='\n            Festival drama nodes have a tunable pre-festival duration that\n            delay festival start to some point after the drama node has\n            started. For example, if the festival drama node has a pre-festival\n            duration of 2 hours and the drama node runs at 8am, the festival\n            will not start until 10am.\n\n            By default, this test passes if the festival drama node is running,\n            regardless if the festival is in its pre-festival duration. This\n            tuning changes that behavior.\n            ', pre_festival=Tunable(description='\n                If the festival is currently in its pre-festival duration,\n                test can pass if this is checked and fails if unchecked.\n                ', tunable_type=bool, default=True), running=Tunable(description='\n                If the festival is running (it is past its pre-festival\n                duration), test can pass if this is checked and fails if\n                unchecked.\n                ', tunable_type=bool, default=True)), 'negate': Tunable(description='\n            If enabled this test will pass if no festivals of the tuned\n            requirements are running.\n            ', tunable_type=bool, default=False)}
    test_events = (TestEvent.FestivalStarted,)

    def get_expected_args(self):
        return {}

    @cached_test
    def __call__(self):
        drama_scheduler = services.drama_scheduler_service()
        for node in drama_scheduler.active_nodes_gen():
            if self.drama_node is None:
                if node.drama_node_type != DramaNodeType.FESTIVAL:
                    continue
            elif type(node) is not self.drama_node:
                continue
            if self.check_if_on_festival_street is not None and self.check_if_on_festival_street != node.is_on_festival_street():
                continue
            if node.is_during_pre_festival():
                if not self.valid_time_blocks.pre_festival:
                    continue
            elif not self.valid_time_blocks.running:
                continue
            if self.negate:
                return TestResult(False, 'Drama nodes match the required conditions.')
            return TestResult.TRUE
        if self.negate:
            return TestResult.TRUE
        return TestResult(False, 'No drama nodes match the required conditions.')

class NextFestivalTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'drama_node': OptionalTunable(description='\n            If enabled then we will check a specific type of festival drama\n            node otherwise we will look at all of the festival drama nodes.\n            ', tunable=TunableReference(description='\n                Reference to the festival drama node that we want to be the\n                next one.\n                ', manager=services.get_instance_manager(sims4.resources.Types.DRAMA_NODE), class_restrictions=('FestivalDramaNode',)), enabled_by_default=True), 'negate': Tunable(description='\n            If enabled this test will pass if the next festival is not one of\n            the tuned nodes.\n            ', tunable_type=bool, default=False)}

    def get_expected_args(self):
        return {}

    @cached_test
    def __call__(self):
        drama_scheduler = services.drama_scheduler_service()
        best_time = None
        best_nodes = [type(node) for node in drama_scheduler.active_nodes_gen() if node.drama_node_type == DramaNodeType.FESTIVAL]
        if not best_nodes:
            for node in drama_scheduler.scheduled_nodes_gen():
                if node.drama_node_type != DramaNodeType.FESTIVAL:
                    continue
                new_time = node._selected_time - services.time_service().sim_now
                if best_time is None or new_time < best_time:
                    best_nodes = [type(node)]
                    best_time = new_time
                elif new_time == best_time:
                    best_nodes.append(type(node))
        if not best_nodes:
            if self.negate:
                return TestResult.TRUE
            return TestResult(False, 'No scheduled Festivals.')
        if self.drama_node is None or self.drama_node in best_nodes:
            if self.negate:
                return TestResult(False, 'Next scheduled Festival matches requested.')
            return TestResult.TRUE
        if self.negate:
            return TestResult.TRUE
        return TestResult(False, "Next scheduled Festival doesn't match requested.")

class TimeUntilFestivalTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'drama_node': OptionalTunable(description='\n            If enabled then we will check a specific type of festival drama\n            node otherwise we will look at any of the festival drama nodes.\n            ', tunable=TunableReference(description='\n                Reference to the festival drama node that we want to test.\n                ', manager=services.get_instance_manager(sims4.resources.Types.DRAMA_NODE), class_restrictions=('FestivalDramaNode',)), enabled_by_default=True), 'max_time': Tunable(description='\n            Maximum time in hours between when the test occurs to the start of\n            the festival in order for the test to return true.\n            ', tunable_type=float, default=18.0), 'negate': Tunable(description='\n            If enabled this test will pass if the requested festival will not\n            start within the specified time.\n            ', tunable_type=bool, default=False)}

    def get_expected_args(self):
        return {}

    @cached_test
    def __call__(self):
        drama_scheduler = services.drama_scheduler_service()
        best_time = None
        for node in drama_scheduler.scheduled_nodes_gen():
            if node.drama_node_type != DramaNodeType.FESTIVAL:
                continue
            if not self.drama_node is None:
                if self.drama_node is type(node):
                    new_time = node.get_time_remaining()
                    if not best_time is None:
                        if new_time < best_time:
                            best_time = new_time
                    best_time = new_time
            new_time = node.get_time_remaining()
            if not best_time is None:
                if new_time < best_time:
                    best_time = new_time
            best_time = new_time
        if best_time is None:
            if not self.negate:
                return TestResult(False, 'No scheduled Festivals of type {}.', self.drama_node, tooltip=self.tooltip)
        elif best_time.in_hours() < self.max_time:
            if self.negate:
                return TestResult(False, 'Next scheduled Festival is within specified time', tooltip=self.tooltip)
        elif not self.negate:
            return TestResult(False, "Next scheduled Festival isn't within specified time", tooltip=self.tooltip)
        return TestResult.TRUE

class DramaNodeTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'drama_nodes': TunableList(description='\n            The types of drama nodes that we want to check.\n            ', tunable=TunableReference(description='\n                A Drama node type we want to check.\n                ', manager=services.get_instance_manager(sims4.resources.Types.DRAMA_NODE), pack_safe=True)), 'check_scheduled_nodes': Tunable(description='\n            Check against nodes that are scheduled, but not actively running.\n            ', tunable_type=bool, default=True), 'check_active_nodes': Tunable(description='\n            Check against nodes that are actively running.\n            ', tunable_type=bool, default=True), 'exists': Tunable(description='\n            If checked then this drama node will pass if a node meeting the requirements exists.\n            Otherwise it will pass if there is not a node meeting the requirements.\n            ', tunable_type=bool, default=True), 'receiver_sim': OptionalTunable(description='\n            If enabled we will check that the receiver Sim is the tuned Sim.\n            ', tunable=TunableEnumEntry(description='\n                The Sim that we will make sure is the receiver Sim.\n                ', tunable_type=ParticipantTypeSingleSim, default=ParticipantTypeSingleSim.TargetSim))}

    def get_expected_args(self):
        if self.receiver_sim is None:
            return {}
        else:
            return {'receiver_sim': self.receiver_sim}

    @cached_test
    def __call__(self, receiver_sim=None):
        if not self.drama_nodes:
            if self.exists:
                return TestResult(False, 'No drama node exists meeting the requirements.', tooltip=self.tooltip)
            return TestResult.TRUE
        drama_scheduler = services.drama_scheduler_service()
        if self.check_scheduled_nodes and self.check_active_nodes:
            drama_node_gen = drama_scheduler.all_nodes_gen
        elif self.check_scheduled_nodes:
            drama_node_gen = drama_scheduler.scheduled_nodes_gen
        elif self.check_active_nodes:
            drama_node_gen = drama_scheduler.active_nodes_gen
        else:
            if self.exists:
                return TestResult(False, 'No drama node exists meeting the requirements.', tooltip=self.tooltip)
            return TestResult.TRUE
        if receiver_sim is not None:
            receiver_sim = next(iter(receiver_sim))
        for drama_node in drama_node_gen():
            if type(drama_node) not in self.drama_nodes:
                continue
            if receiver_sim is not None and drama_node.get_receiver_sim_info() is not receiver_sim:
                continue
            if self.exists:
                return TestResult.TRUE
            return TestResult(False, 'Drama node meeting the requirements exists when we are asking for non-existence.', tooltip=self.tooltip)
        if self.exists:
            return TestResult(False, 'No drama node exists meeting the requirements.', tooltip=self.tooltip)
        return TestResult.TRUE
