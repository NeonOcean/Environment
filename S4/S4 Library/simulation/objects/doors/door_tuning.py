from services import get_instance_manager
from sims4.tuning.tunable import TunableTuple, TunableReference
import sims4.resources

class DoorTuning:
    FRONT_DOOR_AVAILABILITY_STATE = TunableTuple(description='\n        State values for front door availability.\n        ', enabled=TunableReference(description='\n            State value for door being available to be a front door.\n            ', manager=get_instance_manager(sims4.resources.Types.OBJECT_STATE), class_restrictions='ObjectStateValue'), disabled=TunableReference(description='\n            State value for door being unavailable to be a front door.\n            ', manager=get_instance_manager(sims4.resources.Types.OBJECT_STATE), class_restrictions='ObjectStateValue'))
    FRONT_DOOR_STATE = TunableTuple(description="\n        State values for a door is or isn't a front door.\n        ", enabled=TunableReference(description='\n            State value for door is front door.\n            ', manager=get_instance_manager(sims4.resources.Types.OBJECT_STATE), class_restrictions='ObjectStateValue'), disabled=TunableReference(description='\n            State value for door is not front door.\n            ', manager=get_instance_manager(sims4.resources.Types.OBJECT_STATE), class_restrictions='ObjectStateValue'))
    INACTIVE_APARTMENT_DOOR_STATE = TunableTuple(description="\n        State values for a door is or isn't for an inactive apartment.\n        ", enabled=TunableReference(description='\n            State value for door is for an inactive apartment.\n            ', manager=get_instance_manager(sims4.resources.Types.OBJECT_STATE), class_restrictions='ObjectStateValue'), disabled=TunableReference(description='\n            State value for door is not for an inactive apartment.\n            ', manager=get_instance_manager(sims4.resources.Types.OBJECT_STATE), class_restrictions='ObjectStateValue'))
