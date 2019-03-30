from filters.tunable import FilterTermVariant
from sims.sim_spawner_enums import SimNameType
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import HasTunableReference, TunableMapping, TunableWorldDescription, TunableReference, TunableList, TunableTuple, TunableRange, TunablePackSafeReference, OptionalTunable, TunableEnumEntry, TunableLotDescription, TunableSet
from sims4.tuning.tunable_base import ExportModes
import services
import sims4.log
logger = sims4.log.Logger('Street', default_owner='rmccord')

class Street(HasTunableReference, metaclass=HashedTunedInstanceMetaclass, manager=services.street_manager()):
    WORLD_DESCRIPTION_TUNING_MAP = TunableMapping(description='\n        A mapping between Catalog world description and street tuning instance.\n        This way we can find out what world description the current zone\n        belongs to at runtime then grab its street tuning instance.\n        ', key_type=TunableWorldDescription(description='\n            Catalog-side World Description.\n            ', pack_safe=True, export_modes=ExportModes.All), value_type=TunableReference(description="\n            Street Tuning instance. This is retrieved at runtime based on what\n            the active zone's world description is.\n            ", pack_safe=True, manager=services.street_manager()), key_name='WorldDescription', value_name='Street', tuple_name='WorldDescriptionMappingTuple')
    INSTANCE_TUNABLES = {'open_street_director': TunablePackSafeReference(description='\n            The Scheduling Open Street Director to use for this world file.\n            This open street director will be able to load object layers and\n            spin up situations.\n            ', manager=services.get_instance_manager(sims4.resources.Types.OPEN_STREET_DIRECTOR)), 'travel_lot': OptionalTunable(description='\n            If enabled then this street will have a specific lot that it will\n            want to travel to when we travel to this "street."\n            ', tunable=TunableLotDescription(description='\n                The specific lot that we will travel to when asked to travel to\n                this street.\n                ')), 'townie_demographics': TunableTuple(description='\n            Townie population demographics for the street.\n            ', target_population=OptionalTunable(description='\n                If enabled, Sims created for other purposes will passively be\n                assigned to live on this street, gaining the filter features.\n                Sims are assigned out in round robin fashion up until all\n                streets have reached their target, after which those streets\n                will be assigned Sims in round robin fashion past their target.\n                \n                If disabled, this street will not passively be assigned townies\n                unless the Lives On Street filter explicitly requires the\n                Sim to be on the street.\n                ', tunable=TunableRange(description="\n                    The ideal number of townies that live on the street.\n                    \n                    0 is valid if you don't want Sims to live on this street\n                    while other streets haven't met their target population.\n                    ", tunable_type=int, default=1, minimum=0)), filter_features=TunableList(description='\n                Sims created as townies living on this street, they will gain\n                one set of features in this list. Features are applied as\n                Sim creation tags and additional filter terms to use.\n                ', tunable=TunableTuple(description='\n                    ', filter_terms=TunableList(description='\n                        Filter terms to inject into the filter.\n                        ', tunable=FilterTermVariant(conform_optional=True)), sim_creator_tags=TunableReference(description="\n                        Tags to inject into the filter's Sim template.\n                        ", manager=services.get_instance_manager(sims4.resources.Types.TAG_SET), allow_none=True), sim_name_type=TunableEnumEntry(description='\n                        What type of name the sim should have.\n                        ', tunable_type=SimNameType, default=SimNameType.DEFAULT), weight=TunableRange(description='\n                        Weighted chance.\n                        ', tunable_type=float, default=1, minimum=0)))), 'conditional_layers': TunableSet(description='\n            A list of all of the conditional_layers on this Street.\n            ', tunable=TunableReference(description='\n                A reference to a conditional layer that exists on this Street.\n                ', manager=services.get_instance_manager(sims4.resources.Types.CONDITIONAL_LAYER), pack_safe=True))}

    @classmethod
    def _cls_repr(cls):
        return "Street: <class '{}.{}'>".format(cls.__module__, cls.__name__)

    @classmethod
    def get_lot_to_travel_to(cls):
        if cls is services.current_street():
            return
        import world.lot
        return world.lot.get_lot_id_from_instance_id(cls.travel_lot)

    @classmethod
    def has_conditional_layer(cls, conditional_layer):
        return conditional_layer in cls.conditional_layers

def get_street_instance_from_zone_id(zone_id):
    world_description_id = get_world_description_id_from_zone_id(zone_id)
    if world_description_id is None:
        return
    return Street.WORLD_DESCRIPTION_TUNING_MAP.get(world_description_id)

def get_street_instance_from_world_id(world_id):
    world_description_id = services.get_world_description_id(world_id)
    return Street.WORLD_DESCRIPTION_TUNING_MAP.get(world_description_id, None)

def get_world_description_id_from_zone_id(zone_id):
    zone_data = services.get_persistence_service().get_zone_proto_buff(zone_id)
    return services.get_world_description_id(zone_data.world_id)
