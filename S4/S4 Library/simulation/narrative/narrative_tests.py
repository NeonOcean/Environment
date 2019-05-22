from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableReference, TunableVariant
from tunable_utils.tunable_white_black_list import TunableWhiteBlackList
import services

class _ActiveNarrativeTest(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'narratives': TunableWhiteBlackList(tunable=TunableReference(manager=services.get_instance_manager(Types.NARRATIVE)))}

    def test(self, tooltip):
        if self.narratives.test_collection(services.narrative_service().active_narratives):
            return TestResult.TRUE
        return TestResult(False, 'Failed to pass narrative white/black list.', tooltip=tooltip)

class _CompletedNarrativeTest(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'narratives': TunableWhiteBlackList(tunable=TunableReference(manager=services.get_instance_manager(Types.NARRATIVE)))}

    def test(self, tooltip):
        if self.narratives.test_collection(services.narrative_service().completed_narratives):
            return TestResult.TRUE
        return TestResult(False, 'Failed to pass narrative white/black list.', tooltip=tooltip)

class NarrativeTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {'test_type': TunableVariant(description='\n            The type of test to run.\n            ', active_narrative_test=_ActiveNarrativeTest.TunableFactory(), completed_narrative_test=_CompletedNarrativeTest.TunableFactory(), default='active_narrative_test')}

    def get_expected_args(self):
        return {}

    def __call__(self):
        return self.test_type.test(self.tooltip)
