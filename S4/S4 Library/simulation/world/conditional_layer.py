from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import TunableReference, TunableList
from sims4.tuning.tunable_hash import TunableStringHash32
import services
import sims4.resources

class ConditionalLayer(metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.CONDITIONAL_LAYER)):
    INSTANCE_TUNABLES = {'layer_name': TunableStringHash32(description='\n            The name of the layer that will be loaded.\n            World Building should tell you what this should be.\n            '), 'conflicting_layers': TunableList(description='\n            A List of Zone Layers that conflict with this layer. If this layer\n            is present and one of the listed Zone Layers attempts to load it \n            will fail.        \n            ', tunable=TunableReference(description='\n                A Zone Layer that conflicts with this Zone Layer.\n                ', manager=services.get_instance_manager(sims4.resources.Types.CONDITIONAL_LAYER)), unique_entries=True)}
