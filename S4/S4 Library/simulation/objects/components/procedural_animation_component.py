from animation.animation_constants import ActorType
from animation.animation_controls import ProceduralControlWheel
from distributor.fields import Field, ComponentField
from distributor.ops import SetActorType, GenericProtocolBufferOp
from distributor.rollback import ProtocolBufferRollback
from distributor.system import Distributor
from objects.components import types, Component
from protocolbuffers import Animation_pb2, DistributorOps_pb2
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, TunableList, TunableVariant
import services

class ProceduralAnimationComponent(Component, HasTunableFactory, AutoFactoryInit, component_name=types.PROCEDURAL_ANIMATION_COMPONENT):
    FACTORY_TUNABLES = {'controls': TunableList(description='\n            List of animated controls that the client needs to animate and manage.\n            ', tunable=TunableVariant(description='\n                The control type.\n                ', wheel=ProceduralControlWheel.TunableFactory()))}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._controls = {}
        for (control_id, control) in enumerate(self.controls, 1):
            self._controls[control_id] = control()

    @ComponentField(op=SetActorType, priority=Field.Priority.HIGH)
    def actor_type(self):
        return ActorType.ProceduralObject

    def send_animation_data_msg(self):
        animation_data_msg = Animation_pb2.ProceduralAnimationData()
        for (control_id, control) in self._controls.items():
            with ProtocolBufferRollback(animation_data_msg.controls) as control_msg:
                control_msg.control_id = control_id
                control.build_control_msg(control_msg)
        distributor = Distributor.instance()
        op = GenericProtocolBufferOp(DistributorOps_pb2.Operation.SET_PROCEDURAL_ANIMATION_DATA, animation_data_msg)
        distributor.add_op(self.owner, op)

    def _setup(self):
        self.send_animation_data_msg()

    def on_add(self, *_, **__):
        zone = services.current_zone()
        if not zone.is_zone_loading:
            self._setup()

    def on_finalize_load(self):
        self._setup()
