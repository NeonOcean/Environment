from interactions.liability import Liability
from sims4.tuning.tunable import AutoFactoryInit, HasTunableFactory, TunableEnumEntry
from teleport.teleport_enums import TeleportStyle

class TeleportStyleLiability(Liability, HasTunableFactory, AutoFactoryInit):
    LIABILITY_TOKEN = 'TeleportStyleLiability'
    FACTORY_TUNABLES = {'teleport_style': TunableEnumEntry(description='\n            Style to be used while the liability is active.\n            ', tunable_type=TeleportStyle, default=TeleportStyle.NONE, invalid_enums=(TeleportStyle.NONE,), pack_safe=True)}
    SOURCE_LIABILITY = 0

    def __init__(self, interaction, **kwargs):
        super().__init__(**kwargs)
        self._sim_info = interaction.sim.sim_info
        self._sim_info.add_teleport_style(self.SOURCE_LIABILITY, self.teleport_style)

    def release(self):
        self._sim_info.remove_teleport_style(self.SOURCE_LIABILITY, self.teleport_style)
