from interactions.utils.display_mixin import get_display_mixin
from lot_decoration.lot_decoration_enums import DecorationLocation
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import HasTunableReference, TunableMapping, TunableEnumEntry, TunableDecoTrim, Tunable
from sims4.tuning.tunable_base import ExportModes
import services
import sims4

class LotDecorationPreset(HasTunableReference, get_display_mixin(has_icon=True, has_description=True, export_modes=ExportModes.All), metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.LOT_DECORATION_PRESET)):
    INSTANCE_TUNABLES = {'location_content': TunableMapping(description='\n            A mapping of location to the content available for that location.\n            ', key_type=TunableEnumEntry(description='\n                Location with available content.\n                ', tunable_type=DecorationLocation, default=DecorationLocation.FOUNDATIONS), value_type=TunableMapping(description='\n                A mapping of decoration trim to the weight of that trim\n                versus other trims available for this location.\n                ', key_type=TunableDecoTrim(), value_type=Tunable(description='\n                    The weight of the respective trim versus other trims\n                    in the same location.\n                    ', default=1.0, tunable_type=float), tuple_name='TrimWeightKeyValue'), tuple_name='LocationContentKeyValue', export_modes=ExportModes.All)}
