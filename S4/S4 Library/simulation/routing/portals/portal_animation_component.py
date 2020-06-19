from animation.animation_constants import ActorType
from distributor.fields import ComponentField, Field
from distributor.ops import SetActorType, SetActorStateMachine
from objects.components import Component
from objects.components.types import PORTAL_ANIMATION_COMPONENT
from sims4.tuning.tunable import AutoFactoryInit, HasTunableFactory, TunableInteractionAsmResourceKey

class PortalAnimationComponent(Component, HasTunableFactory, AutoFactoryInit, component_name=PORTAL_ANIMATION_COMPONENT):
    FACTORY_TUNABLES = {'_portal_asm': TunableInteractionAsmResourceKey(description='\n            The animation to use for this portal.\n            ')}

    @ComponentField(op=SetActorType, priority=Field.Priority.HIGH)
    def actor_type(self):
        return ActorType.Door

    @ComponentField(op=SetActorStateMachine)
    def portal_asm(self):
        return self._portal_asm
