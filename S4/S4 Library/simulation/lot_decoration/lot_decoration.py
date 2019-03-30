from interactions.utils.display_mixin import get_display_mixin
from lot_decoration.lot_decoration_enums import DecorationLocation, DecorationPickerCategory
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import HasTunableReference, TunableDecoTrim, TunableEnumSet
import services
import sims4

class LotDecoration(HasTunableReference, get_display_mixin(has_icon=True, has_description=True, has_tooltip=True), metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.LOT_DECORATION)):
    INSTANCE_TUNABLES = {'decoration_resource': TunableDecoTrim(description='\n            The catalog decoration resource used for this lot decoration.\n            '), 'available_locations': TunableEnumSet(description='\n            The locations where this decoration may be applied.  Used for\n            picker filtering.\n            ', enum_type=DecorationLocation), 'picker_categories': TunableEnumSet(description='\n            The categories this decoration applies to.  Used for picker\n            drop-down filtering.\n            ', enum_type=DecorationPickerCategory, default_enum_list=(DecorationPickerCategory.ALL,))}
