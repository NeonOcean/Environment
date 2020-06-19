from sims4.tuning.tunable import AutoFactoryInit, HasTunableFactory, Tunable, OptionalTunable
from sims4.tuning.tunable_hash import TunableStringHash32
from vehicles.vehicle_constants import VehicleControlType

class VehicleControlBase(HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {}

    def build_control_msg(self, msg):
        pass

class VehicleControlWheel(VehicleControlBase):
    FACTORY_TUNABLES = {'reference_joint': TunableStringHash32(description='\n            The joint we use to determine where the wheel is on the bike.\n            '), 'control_joint': TunableStringHash32(description="\n            The joint that is controlled and rotates with the actor's velocity.\n            "), 'terrain_alignment': Tunable(description='\n            If enabled, the client will align the vehicle to the terrain using\n            this control.\n            ', tunable_type=bool, default=False), 'bump_sound': OptionalTunable(description="\n            If enabled, this is the name of the sound to play when the control\n            hits a 'bump' in the terrain.\n            ", tunable=Tunable(description='\n                The name of the sound to play when the control hits a bump in\n                the terrain. We use a string here instead of a hash so that we\n                can modify the sound name based on the terrain and other\n                factors from locomotion.\n                ', tunable_type=str, default=''))}

    def build_control_msg(self, msg):
        msg.control_type = VehicleControlType.WHEEL
        msg.enable_terrain_alignment = self.terrain_alignment
        msg.joint_name_hash = self.control_joint
        msg.reference_joint_name_hash = self.reference_joint
        if self.bump_sound:
            msg.bump_sound_name = self.bump_sound
