from sims4.tuning.tunable import TunableResourceKey
from sims4.tuning.tunable_hash import _Hash
import sims4.resources
import routing

class TunableWalkstyle(TunableResourceKey):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, resource_types=(sims4.resources.Types.WALKSTYLE,), **kwargs)

    @property
    def validate_pack_safe(self):
        return False

    def load_etree_node(self, *args, node, **kwargs):
        value = super().load_etree_node(*args, node=node, **kwargs)
        if value is not None:
            walkstyle_hash = routing.get_walkstyle_hash_from_resource(value)
            value = walkstyle_hash
        return value
