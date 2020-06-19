import services
from animation.tunable_animation_overrides import TunableAnimationOverrides
from sims4.tuning.tunable import TunableReference, TunableList, TunableSet, TunableTuple

class FavoritesTuning:
    FAVORITES_ANIMATION_OVERRIDES = TunableList(description='\n        A list of favorite object definitions and animation overrides. These will\n        be applied any time one of these favorites is used (currently only with \n        prop overrides).\n        ', tunable=TunableTuple(description='\n            A set of favorite object definitions and animation overrides to apply\n            when one of those definitions is used as a favorite.\n            ', favorite_definitions=TunableSet(description='\n                A set of object definitions. If any object in this set is used as a \n                favorite, the corresponding Animation Overrides will be applied.\n                ', tunable=TunableReference(description='\n                    The definition of the favorite.\n                    ', manager=services.definition_manager(), pack_safe=True)), animation_overrides=TunableAnimationOverrides(description='\n                Any animation overrides to use when one of the listed favorite \n                objects is used. Currently, this only applies to prop overrides.\n                ')))
