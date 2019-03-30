from sims4.tuning.tunable import TunableEnumEntry, TunableEnumWithFilter
from tag import Tag
from venues.venue_object_test import VenueObjectTestTag

class RestaurantTagTuning:
    DINING_SPOT_OBJECT_TEST_TAG = TunableEnumEntry(description='\n        The enum tag to identify required object test in venue tuning for the dining spot.\n        ', tunable_type=VenueObjectTestTag, default=VenueObjectTestTag.INVALID, invalid_enums=(VenueObjectTestTag.INVALID,))
    RECIPE_FOOD_TAG = TunableEnumWithFilter(description='\n        The recipe tag to determine if this recipe is food recipe.\n        ', tunable_type=Tag, filter_prefixes=['recipe'], default=Tag.INVALID, invalid_enums=(Tag.INVALID,), pack_safe=True)
    RECIPE_DRINK_TAG = TunableEnumWithFilter(description='\n        The recipe tag to determine if this recipe is drink recipe.\n        ', tunable_type=Tag, filter_prefixes=['recipe'], default=Tag.INVALID, invalid_enums=(Tag.INVALID,), pack_safe=True)
    DINER_SITUATION_TAG = TunableEnumWithFilter(description='\n        The situation tag to determine whether the situation is diner situation.\n        ', tunable_type=Tag, filter_prefixes=['situation'], default=Tag.INVALID, invalid_enums=(Tag.INVALID,), pack_safe=True)
