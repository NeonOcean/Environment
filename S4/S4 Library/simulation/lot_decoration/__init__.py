from collections import namedtuple
from sims4.tuning.tunable import TunableSingletonFactory, TunableRealSecond
import sims4.log
decorations_logger = sims4.log.Logger('Lot Decorations', default_owner='jdimailig')
ClientLotDecorationParams = namedtuple('ClientLotDecorationParams', ('fade_duration', 'fade_variation_range', 'client_fade_delay'))
DECORATE_IMMEDIATELY = ClientLotDecorationParams(0, 0, 0)

class TunableClientLotDecorationParams(TunableSingletonFactory):
    FACTORY_TYPE = ClientLotDecorationParams

    def __init__(self, default_fade_duration=0, default_fade_variation_range=0, default_client_fade_delay=0, **kwargs):
        super().__init__(fade_duration=TunableRealSecond(description='\n                Amount of time alloted for fading in a decoration on a lot.\n                ', minimum=0, default=default_fade_duration), fade_variation_range=TunableRealSecond(description="\n                Randomized variation time range for fade in that is used \n                so that all deco trims on a lot don't fade in at the same time.\n                ", minimum=0, default=default_fade_variation_range), client_fade_delay=TunableRealSecond(description="\n                After an lot decoration request is made, this is the delay \n                amount given to the client decoration system before it starts \n                to fade in the lot decorations.\n                \n                Note when the request is processed, gameplay has already saved \n                that the lot is 'decorated', so there are save/load implications\n                when this is set to a large value.\n                ", minimum=0, default=default_client_fade_delay), **kwargs)
