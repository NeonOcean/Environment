from sims4.tuning.tunable import TunableMapping, TunableHouseDescription, TunableList
from sims4.tuning.tunable_base import ExportModes
from zone_modifier.zone_modifier import ZoneModifier

class ZoneModifierTuning:
    INITIAL_ZONE_MODIFIERS = TunableMapping(description='\n        A mapping of HouseDescription to zone modifiers the lot with that\n        HouseDescription should have.\n        ', key_type=TunableHouseDescription(description='\n            The lot with this HouseDescription will have the tuned ZoneModifiers.\n            ', pack_safe=True), value_type=TunableList(description='\n            The list of ZoneModifiers to give to the lot with the corresponding\n            HouseDescription.\n            ', tunable=ZoneModifier.TunableReference(pack_safe=True)), tuple_name='InitialZoneModifiersMapping', export_modes=ExportModes.All)
