from interactions.utils.loot_basic_op import BaseLootOperation
from narrative.narrative_enums import NarrativeEvent
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableVariant, TunableReference, TunableEnumEntry
import services

class _TriggerEventOp(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'event': TunableEnumEntry(description='\n            Event of interest.\n            ', tunable_type=NarrativeEvent, default=NarrativeEvent.INVALID, invalid_enums=(NarrativeEvent.INVALID,))}

    def perform(self, *_, **__):
        services.narrative_service().handle_narrative_event(self.event)

class _StartNarrativeOp(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'narrative': TunableReference(manager=services.get_instance_manager(Types.NARRATIVE))}

    def perform(self, *_, **__):
        services.narrative_service().start_narrative(self.narrative)

class _EndNarrativeOp(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'narrative': TunableReference(manager=services.get_instance_manager(Types.NARRATIVE))}

    def perform(self, *_, **__):
        services.narrative_service().end_narrative(self.narrative)

class _ResetNarrativeCompletionOp(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'narrative': TunableReference(manager=services.get_instance_manager(Types.NARRATIVE))}

    def perform(self, *_, **__):
        services.narrative_service().reset_completion(self.narrative)

class NarrativeLootOp(BaseLootOperation):
    FACTORY_TUNABLES = {'op_type': TunableVariant(trigger_event=_TriggerEventOp.TunableFactory(), start_narrative=_StartNarrativeOp.TunableFactory(), end_narrative=_EndNarrativeOp.TunableFactory(), reset_completion=_ResetNarrativeCompletionOp.TunableFactory(), default='trigger_event')}

    def __init__(self, op_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.op_type = op_type

    def _apply_to_subject_and_target(self, subject, target, resolver):
        self.op_type.perform()
