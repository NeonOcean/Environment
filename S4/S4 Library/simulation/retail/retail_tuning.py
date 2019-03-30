from business.business_enums import BusinessAdvertisingType
from sims4.tuning.tunable import TunableMapping, TunableEnumEntry, TunableReference
import services
import sims4.resources

class RetailTuning:
    ADVERTISING_COMMODITY_MAP = TunableMapping(description='\n        The mapping between advertising enum and the advertising data for\n        that type.\n        ', key_name='advertising_enum', key_type=TunableEnumEntry(description='\n            The Advertising Type .\n            ', tunable_type=BusinessAdvertisingType, default=BusinessAdvertisingType.INVALID, invalid_enums=(BusinessAdvertisingType.INVALID,)), value_name='advertising_commodity', value_type=TunableReference(description='\n            The commodity that will be added to the lot when this\n            advertising type is chosen. This commodity is applied via\n            the Advertising Interaction. This makes it easier for design\n            to tune differences in how each business handles\n            advertising. i.e. Retail allows advertising on multiple\n            channels at the same time while restaurants only allow one\n            advertisement at a time.\n            ', manager=services.get_instance_manager(sims4.resources.Types.STATISTIC), class_restrictions=('Commodity',), pack_safe=True))
