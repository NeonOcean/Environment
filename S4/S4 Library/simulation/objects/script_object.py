import itertools
import time
from _collections import defaultdict

from _sims4_collections import frozendict

import build_buy
import caches
import distributor.fields
import indexed_manager
import objects.components.types
import objects.persistence_groups
import postures
import protocolbuffers.FileSerialization_pb2 as file_serialization
import routing
import services
import sims4.log
from animation.animation_overrides_tuning import TunableParameterMapping
from animation.animation_utils import AnimationOverrides
from animation.focus.focus_component import FocusComponent
from animation.tunable_animation_overrides import TunableAnimationObjectOverrides, TunableAnimationOverrides
from autonomy.autonomy_component import AutonomyComponent
from balloon.tunable_balloon import TunableBalloon
from build_buy import PlacementFlags, WALL_OBJECT_POSITION_PADDING, get_object_placement_flags
from caches import cached
from carry.carry_postures import CarryingObject
from carry.carry_utils import get_carried_objects_gen
from crafting.crafting_tunable import CraftingTuning
from curfew.curfew_component import CurfewComponent
from curfew.curfew_service import CurfewService
from distributor.rollback import ProtocolBufferRollback
from interactions.aop import AffordanceObjectPair
from interactions.base.basic import AFFORDANCE_LOADED_CALLBACK_STR
from interactions.constraints import Constraint
from interactions.utils.routing import RouteTargetType
from narrative.narrative_aware_component import NarrativeAwareComponent
from objects import slots
from objects.base_object import BaseObject, ResetReason
from objects.collection_manager import CollectableComponent
from objects.components import component_definition, forward_to_components, forward_to_components_gen, get_component_priority_and_name_using_persist_id
from objects.components.affordance_tuning import AffordanceTuningComponent
from objects.components.autonomy_marker_component import AutonomyMarkerComponent
from objects.components.camera_view_component import CameraViewComponent
from objects.components.canvas_component import CanvasComponent, FamilyPortraitComponent, SimPortraitComponent
from objects.components.carryable_component import CarryableComponent
from objects.components.censor_grid_component import TunableCensorGridComponent
from objects.components.consumable_component import ConsumableComponent
from objects.components.crafting_station_component import CraftingStationComponent
from objects.components.display_component import DisplayComponent
from objects.components.fishing_location_component import FishingLocationComponent
from objects.components.flowing_puddle_component import FlowingPuddleComponent
from objects.components.footprint_component import HasFootprintComponent
from objects.components.game_component import GameComponent
from objects.components.idle_component import IdleComponent
from objects.components.inventory_item import InventoryItemComponent
from objects.components.lighting_component import LightingComponent
from objects.components.line_of_sight_component import TunableLineOfSightComponent
from objects.components.linked_object_component import LinkedObjectComponent
from objects.components.live_drag_target_component import LiveDragTargetComponent
from objects.components.locking_components import ObjectLockingComponent
from objects.components.mannequin_component import MannequinComponent
from objects.components.name_component import NameComponent
from objects.components.object_age import TunableObjectAgeComponent
from objects.components.object_inventory_component import ObjectInventoryComponent
from objects.components.object_relationship_component import ObjectRelationshipComponent
from objects.components.object_teleportation_component import ObjectTeleportationComponent
from objects.components.ownable_component import OwnableComponent
from objects.components.owning_household_component import OwningHouseholdComponent
from objects.components.privacy_component import PrivacyComponent
from objects.components.proximity_component import ProximityComponent
from objects.components.routing_component import RoutingComponent
from objects.components.slot_component import SlotComponent
from objects.components.spawner_component import SpawnerComponent
from objects.components.state import TunableStateComponent
from objects.components.statistic_component import HasStatisticComponent
from objects.components.stolen_component import StolenComponent
from objects.components.stored_audio_component import StoredAudioComponent
from objects.components.time_of_day_component import TimeOfDayComponent
from objects.components.tooltip_component import TooltipComponent
from objects.components.vehicle_component import VehicleComponent
from objects.components.video import VideoComponent
from objects.game_object_properties import GameObjectTuning
from objects.gardening.gardening_component_variant import TunableGardeningComponentVariant
from objects.object_enums import ItemLocation, PersistenceType
from objects.parts.part_data import TunablePartDataMapping
from objects.persistence_groups import PersistenceGroups
from objects.slots import SlotType
from protocolbuffers import SimObjectAttributes_pb2 as protocols
from protocolbuffers.FileSerialization_pb2 import ObjectData
from retail.retail_component import TunableRetailComponentSnippet
from routing import SurfaceIdentifier, SurfaceType
from routing.portals.portal_component import PortalComponent
from seasons.season_aware_component import SeasonAwareComponent
from sims.university.university_scholarship_letter_component import ScholarshipLetterComponent
from sims4.localization import TunableLocalizedString
from sims4.math import MAX_FLOAT
from sims4.tuning.geometric import TunableVector2
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import OptionalTunable, Tunable, TunableEnumEntry, TunableEnumWithFilter, TunableList, TunableMapping, TunableRange, TunableReference, TunableSet, TunableTuple, TunableVariant
from sims4.tuning.tunable_base import FilterTag, GroupNames
from sims4.utils import classproperty, flexmethod
from singletons import EMPTY_SET
from statistics.mood import TunableEnvironmentScoreModifiers
from tag import Tag
from weather.weather_aware_component import WeatherAwareComponent
from whims.whim_component import WhimComponent
from world.spawn_point_component import SpawnPointComponent

logger = sims4.log.Logger('Objects')
COMMODITY_FLAGS_FROM_COMPONENTS_KEY = 'component_commodities'

class ScriptObject(BaseObject, HasStatisticComponent, HasFootprintComponent, metaclass = HashedTunedInstanceMetaclass, manager = services.definition_manager()):
	INSTANCE_TUNABLES = {
		'_super_affordances': TunableList(description = '\n            Super affordances on this object.\n            ', tunable = TunableReference(description = '\n                A super affordance on this object.\n                ', manager = services.affordance_manager(), class_restrictions = ('SuperInteraction',), pack_safe = True)),
		'_preroll_super_affordances': TunableList(description = '\n            Super affordances on this object that can be run during preroll.\n            ', tunable = TunableReference(description = '\n                A super affordance on this object that can be run during preroll.\n                ', manager = services.affordance_manager(), class_restrictions = ('SuperInteraction',), pack_safe = True), unique_entries = True),
		'_part_data': TunableList(description = '\n            THIS FIELD IS DEPRECATED!\n        \n            Use this to define parts for an object. Parts allow multiple Sims to\n            use an object in different or same ways, at the same time. The model\n            and the animations for this object will have to support parts.\n            Ensure this is the case with animation and modeling.\n           \n            There will be one entry in this list for every part the object has.\n           \n            e.g. The bed has six parts (two sleep parts, and four sit parts).\n              add two entries for the sleep parts add four entries for the sit\n              parts\n            ',
								  tunable = TunableTuple(description = '\n                Data that is specific to this part.\n                ', part_definition = TunableReference(description = '\n                    The part definition data.\n                    ', manager = services.object_part_manager()), subroot_index = OptionalTunable(description = '\n                    If enabled, this part will have a subroot index associated\n                    with it. This will affect the way Sims animate, i.e. they\n                    will animate relative to the position of the part, not\n                    relative to the object.\n                    ', tunable = Tunable(description = '\n                        The subroot index/suffix associated to this part.\n                        ', tunable_type = int, default = 0, needs_tuning = False), enabled_by_default = True),
														 overlapping_parts = TunableList(description = "\n                    The indices of parts that are unusable when this part is in\n                    use. The index is the zero-based position of the part within\n                    the object's Part Data list.\n                    ", tunable = int),
														 adjacent_parts = OptionalTunable(description = '\n                    Define adjacent parts. If disabled, adjacent parts will be\n                    generated automatically based on indexing. If enabled,\n                    adjacent parts must be specified here.\n                    ', tunable = TunableList(description = "\n                        The indices of parts that are adjacent to this part. The\n                        index is the zero-based position of the part within the\n                        object's Part Data list.\n                        \n                        An empty list indicates that no part is ajdacent to this\n                        part.\n                        ", tunable = int)),
														 is_mirrored = OptionalTunable(description = '\n                    Specify whether or not solo animations played on this part\n                    should be mirrored or not.\n                    ', tunable = Tunable(description = '\n                        If checked, mirroring is enabled. If unchecked,\n                        mirroring is disabled.\n                        ', tunable_type = bool, default = False)),
														 forward_direction_for_picking = TunableVector2(description = "\n                    When you click on the object this part belongs to, this\n                    offset will be applied to this part when determining which\n                    part is closest to where you clicked. By default, the\n                    object's forward vector will be used. It should only be\n                    necessary to tune this value if multiple parts overlap at\n                    the same location (e.g. the single bed).\n                    ", default = sims4.math.Vector2(0, 1), x_axis_name = 'x', y_axis_name = 'z'), disable_sim_aop_forwarding = Tunable(description = '\n                    If checked, Sims using this specific part will never forward\n                    AOPs.\n                    ', tunable_type = bool, default = False),
														 disable_child_aop_forwarding = Tunable(description = '\n                    If checked, objects parented to this specific part will\n                    never forward AOPs.\n                    ', tunable_type = bool, default = False), anim_overrides = TunableAnimationOverrides(description = 'Animation overrides for this part.'), restrict_autonomy_preference = Tunable(description = '\n                    If checked, this specific part can be used for use only autonomy\n                    restriction.\n                    ', tunable_type = bool, default = False), name = OptionalTunable(description = '\n                    Name of this part.  For use if the part name needs to be surfaced\n                    to the player.  (i.e. when assigning sim to specific side of bed.)\n                    ', tunable = TunableLocalizedString())), deprecated = True),
		'_part_data_map': TunablePartDataMapping(description = '\n            Use this to define parts for an object. Parts allow multiple Sims to\n            use an object in different or same ways, at the same time. The model\n            and the animations for this object will have to support parts.\n            Ensure this is the case with animation and modeling.\n           \n            There will be one entry in this list for every part the object has.\n           \n            e.g. The bed has six parts (two sleep parts, and four sit parts).\n                  add two entries for the sleep parts add four entries for the\n                  sit parts\n            '),
		'custom_posture_target_name': Tunable(
			description = '\n            An additional non-virtual actor to set for this object when used as\n            a posture target.\n            \n            This tunable is used when the object has parts. In most cases, the\n            state machines will only have one actor for the part that is\n            involved in animation. In that case, this field should not be set.\n            \n            e.g. The Sit posture requires the sitTemplate actor to be set, but\n            does not make a distinction between, for instance, Chairs and Sofas,\n            because no animation ever involves the whole object.\n            \n            However, there may be cases when, although we are dealing with\n            parts, the animation will need to also reference the entire object.\n            In that case, the ASM will have an extra actor to account for the\n            whole object, in addition to the part. Set this field to be that\n            actor name.\n            \n            e.g. The Sleep posture on the bed animates the Sim on one part.\n            However, the sheets and pillows need to animate on the entire bed.\n            In that case, we need to set this field on Bed so that the state\n            machine can have this actor set.\n            ',
			tunable_type = str, default = None),
		'posture_transition_target_tag': TunableEnumEntry(description = '\n            A tag to apply to this script object so that it is taken into\n            account for posture transition preference scoring.  For example, you\n            could tune this object (and others) to be a DINING_SURFACE.  Any SI\n            that is set up to have posture preference scoring can override the\n            score for any objects that are tagged with DINING_SURFACE.\n            \n            For a more detailed description of how posture preference scoring\n            works, see the posture_target_preference tunable field description\n            in SuperInteraction.\n            ', tunable_type = postures.PostureTransitionTargetPreferenceTag, default = postures.PostureTransitionTargetPreferenceTag.INVALID, pack_safe = True),
		'_anim_overrides': OptionalTunable(description = '\n            If enabled, specify animation overrides for this object.\n            ', tunable = TunableAnimationObjectOverrides()),
		'_default_anim_params': TunableParameterMapping(description = '\n            A list of animation parameters to use as defaults for this object. \n            This should be used if this object is a base game object, but can\n            specify pack specific parameters, to ensure the correct clip is\n            played when running without the pack that specifies the parameter.\n            \n            example: isInfected:False for Bathtubs. GP07 can set this parameter\n            to True.\n            \n            Please consult a GPE before adding a parameter to this list.\n            '),
		'social_clustering': OptionalTunable(description = '\n            If enabled, specify how this objects affects clustering for\n            preferred locations for socialization.\n            ', tunable = TunableTuple(is_datapoint = Tunable(description = '\n                     Whether or not this object is a data point for social\n                     clusters.\n                     ', tunable_type = bool, default = True))),
		'aop_forward_data': TunableTuple(description = '\n            Tuning data about forwarding aop from other related object.\n            ', should_search_forwarded_sim_aop = Tunable(description = "\n                If enabled, interactions on Sims using this object will appear in\n                this object's pie menu as long as they are also tuned to allow\n                forwarding.\n                ", tunable_type = bool, default = False), should_search_forwarded_child_aop = Tunable(description = "\n                If enabled, interactions on children of this object will appear in\n                this object's pie menu as long as they are also tuned to allow\n                forwarding.\n                ", tunable_type = bool, default = False),
										 child_obj_tags = TunableSet(description = '\n                Tags for the child to look for. If empty means no tag requirement.\n                ', tunable = TunableEnumWithFilter(tunable_type = Tag, filter_prefixes = ['func'], default = Tag.INVALID, invalid_enums = (Tag.INVALID,), pack_safe = True)), should_search_forwarded_parent_aop = Tunable(description = "\n                If enabled, interactions on parent of this object will appear in\n                this object's pie menu as long as they are also tuned to allow\n                forwarding.\n                ", tunable_type = bool, default = False)),
		'_disable_child_footprint_and_shadow': Tunable(description = "\n            If checked, all objects parented to this object will have their\n            footprints and dropshadows disabled.\n            \n            Example Use: object_sim has this checked so when a Sim picks up a\n            plate of food, the plate's footprint and dropshadow turn off\n            temporarily.\n            ", tunable_type = bool, default = False),
		'disable_los_reference_point': Tunable(description = '\n            If checked, goal points for this interaction will not be discarded\n            if a ray-test from the object fails to connect without intersecting\n            walls or other objects.  The reason for allowing this, is for\n            objects like the door where we want to allow the sim to interact\n            with the object, but since the object doesnt have a footprint we\n            want to allow him to use the central point as a reference point and\n            not fail the LOS test.\n            ', tunable_type = bool, default = False),
		'_components': TunableTuple(
			description = '\n            The components that instances of this object should have.\n            ',
			tuning_group = GroupNames.COMPONENTS,
			affordance_tuning = OptionalTunable(AffordanceTuningComponent.TunableFactory()),
			autonomy = OptionalTunable(AutonomyComponent.TunableFactory()),
			autonomy_marker = OptionalTunable(AutonomyMarkerComponent.TunableFactory()),
			camera_view = OptionalTunable(CameraViewComponent.TunableFactory()),
			canvas = OptionalTunable(tunable = TunableVariant(canvas_component = CanvasComponent.TunableFactory(),
															  family_portrait = FamilyPortraitComponent.TunableFactory(),
															  sim_portrait = SimPortraitComponent.TunableFactory(),
															  default = 'canvas_component')),
			carryable = OptionalTunable(CarryableComponent.TunableFactory()),
			censor_grid = OptionalTunable(TunableCensorGridComponent()),
			collectable = OptionalTunable(CollectableComponent.TunableFactory()),
			consumable = OptionalTunable(ConsumableComponent.TunableFactory()),
			crafting_station = OptionalTunable(CraftingStationComponent.TunableFactory()),
			curfew = OptionalTunable(CurfewComponent.TunableFactory()),
			display_component = OptionalTunable(DisplayComponent.TunableFactory()),
			fishing_location = OptionalTunable(FishingLocationComponent.TunableFactory()),
			flowing_puddle = OptionalTunable(FlowingPuddleComponent.TunableFactory()),
			focus = OptionalTunable(FocusComponent.TunableFactory()),
			game = OptionalTunable(GameComponent.TunableFactory()),
			gardening = TunableGardeningComponentVariant(),
			idle_component = OptionalTunable(IdleComponent.TunableFactory()),
			inventory = OptionalTunable(ObjectInventoryComponent.TunableFactory()),
			inventory_item = OptionalTunable(InventoryItemComponent.TunableFactory()),
			lighting = OptionalTunable(LightingComponent.TunableFactory()),
			line_of_sight = OptionalTunable(TunableLineOfSightComponent()),
			linked_object_component = OptionalTunable(LinkedObjectComponent.TunableFactory()),
			live_drag_target = OptionalTunable(LiveDragTargetComponent.TunableFactory()),
			mannequin = OptionalTunable(MannequinComponent.TunableFactory()),
			name = OptionalTunable(NameComponent.TunableFactory()),
			narrative_aware_component = OptionalTunable(NarrativeAwareComponent.TunableFactory()),
			object_age = OptionalTunable(TunableObjectAgeComponent()),
			object_locking_component = OptionalTunable(ObjectLockingComponent.TunableFactory()),
			object_relationships = OptionalTunable(ObjectRelationshipComponent.TunableFactory()),
			object_teleportation = OptionalTunable(ObjectTeleportationComponent.TunableFactory()),
			ownable_component = OptionalTunable(OwnableComponent.TunableFactory()),
			owning_household_component = OptionalTunable(OwningHouseholdComponent.TunableFactory()),
			portal = OptionalTunable(PortalComponent.TunableFactory()),
			privacy = OptionalTunable(PrivacyComponent.TunableFactory()),
			proximity_component = OptionalTunable(ProximityComponent.TunableFactory()),
			retail_component = OptionalTunable(TunableRetailComponentSnippet()),
			routing_component = OptionalTunable(RoutingComponent.TunableFactory()),
			scholarship_letter_component = OptionalTunable(ScholarshipLetterComponent.TunableFactory()),
			season_aware_component = OptionalTunable(SeasonAwareComponent.TunableFactory()),
			spawner_component = OptionalTunable(SpawnerComponent.TunableFactory()),
			spawn_point = OptionalTunable(SpawnPointComponent.TunableFactory()),
			state = OptionalTunable(TunableStateComponent()),
			stolen = OptionalTunable(StolenComponent.TunableFactory()),
			stored_audio_component = OptionalTunable(StoredAudioComponent.TunableFactory()),
			time_of_day_component = OptionalTunable(TimeOfDayComponent.TunableFactory()),
			tooltip_component = OptionalTunable(TooltipComponent.TunableFactory()),
			vehicle_component = OptionalTunable(VehicleComponent.TunableFactory()),
			weather_aware_component = OptionalTunable(WeatherAwareComponent.TunableFactory()),
			whim_component = OptionalTunable(WhimComponent.TunableFactory())),
		'_components_native': TunableTuple(description = '\n            Tuning for native components, those that an object will have even\n            if not tuned.\n            ', tuning_group = GroupNames.COMPONENTS, Slot = OptionalTunable(SlotComponent.TunableFactory()), Video = OptionalTunable(VideoComponent.TunableFactory())),
		'_persistence': TunableEnumEntry(description = '\n            The type of persistence this object has.\n            FULL means object will persist across save/load.\n            BUILDBUY means object will support persistence enough for build buy\n            operations to successfully interact with the object.  (i.e. it can\n            be destroyed if you place a room/wall on top of it, then that can\n            be undone/redone.)\n            NONE means object will not persist at all.  Build buy operations \n            (such as the aforementioned room/wall placement) will\n            likely report errors if they intersect the object.\n            ', tunable_type = PersistenceType, default = PersistenceType.FULL),
		'_world_file_object_persists': Tunable(description = "\n            If object is from world file, check this if object state should\n            persist. \n            Example:\n                If grill is dirty, but this is unchecked and it won't stay\n                dirty when reloading the street. \n                If Magic tree has this checked, all object relationship data\n                will be saved.\n            ", tunable_type = bool, default = False, tuning_filter = FilterTag.EXPERT_MODE),
		'_object_state_remaps': TunableList(description = '\n            If this object is part of a Medator object suite, this list\n            specifies which object tuning file to use for each catalog object\n            state.\n            ', tunable = TunableReference(description = '\n                Current object state.\n                ', manager = services.definition_manager(), tuning_filter = FilterTag.EXPERT_MODE)),
		'environment_score_trait_modifiers': TunableMapping(description = '\n            Each trait can put modifiers on any number of moods as well as the\n            negative environment scoring.\n            \n            If tuning becomes a burden, consider making prototypes for many\n            objects and tuning the prototype.\n            \n            Example: A Sim with the Geeky trait could have a modifier for the\n            excited mood on objects like computers and tablets.\n            \n            Example: A Sim with the Loves Children trait would have a modifier\n            for the happy mood on toy objects.\n            \n            Example: A Sim that has the Hates Art trait could get an Angry\n            modifier, and should set modifiers like Happy to multiply by 0.\n            ',
															key_type = TunableReference(description = '\n                The Trait that the Sim must have to enable this modifier.\n                ', manager = services.get_instance_manager(sims4.resources.Types.TRAIT), pack_safe = True), value_type = TunableEnvironmentScoreModifiers.TunableFactory(description = '\n                The Environmental Score modifiers for a particular trait.\n                '), key_name = 'trait', value_name = 'modifiers'),
		'slot_cost_modifiers': TunableMapping(description = "\n            A mapping of slot types to modifier values.  When determining slot\n            scores in the transition sequence, if the owning object of a slot\n            has a modifier for its type specified here, that slot will have the\n            modifier value added to its cost.  A positive modifier adds to the\n            cost of a path using this slot and means that a slot will be less\n            likely to be chosen.  A negative modifier subtracts from the cost\n            of a path using this slot and means that a slot will be more likely\n            to be chosen.\n            \n            ex: Both bookcases and toilets have deco slots on them, but you'd\n            rather a Sim prefer to put down an object in a bookcase than on the\n            back of a toilet.\n            ",
											  key_type = SlotType.TunableReference(description = '\n                A reference to the type of slot to be given a score modifier\n                when considered for this object.\n                '), value_type = Tunable(description = '\n                A tunable float specifying the score modifier for the\n                corresponding slot type on this object.\n                ', tunable_type = float, default = 0)),
		'fire_retardant': Tunable(description = '\n            If an object is fire retardant then not only will it not burn, but\n            it also cannot overlap with fire, so fire will not spread into an\n            area occupied by a fire retardant object.\n            ', tunable_type = bool, default = False),
		'blocking_balloon_overrides': OptionalTunable(TunableList(description = '\n            Balloons to override the blocking balloon from route fail tuning.\n            ', tunable = TunableBalloon())),
		'provides_terrain_interactions': Tunable(description = '\n            If enabled, this object will also provide terrain interactions such\n            as GoHere at the pick point. This is used for objects like Dance\n            Floor who have their own object interactions but would also like to\n            provide GoHere/Do Situps/etc.\n            NOTE: This should not be tuned on objects that are already terrain\n            (eg. Terrain, Rugs, etc.)\n            ', tunable_type = bool, default = False),
		'provides_ocean_interactions': Tunable(description = '\n            If enabled, this object will also provide ocean interactions such \n            Swim Here at the pick point.  This is used for ocean objects like\n            the Dolphin Spawner that have their own object interactions but \n            would also like to provide Swim Here.\n            ', tunable_type = bool, default = False),
		'forward_offset_on_connectivity_check': OptionalTunable(description = "\n            If enabled, when doing connectivity test to this object, \n            destination location for connectivity test will be the position of \n            this object slightly moved by this offset in object's forward \n            directions. \n            \n            ex: When washer placed against the wall and there is a shelf above \n            it, connectivity test to the washer always fail. Because the washer\n            position is on shelf footprint. In that case, tune this offset \n            to prevent the destination location on the test from being placed\n            inside shelf's footprint.\n            ", tunable = TunableRange(description = '\n                The forward offset value.\n                ', tunable_type = float, minimum = 0, default = 0)),
		'apply_children_component_anim_overrides': Tunable(description = '\n            If enabled, apply the component animation overrides the children \n            objects of this object may have (in addition to those of this \n            object).\n            ', tunable_type = bool, default = False),
		'force_multi_surface_constraints': Tunable(description = '\n            If checked, any constraints generated against this object will be\n            forced to be multi-surface. This is helpful if this object is on an\n            object surface and has an animation constraint to satisfy (i.e. the\n            Ship Wheel object from EP06).\n            ', tunable_type = bool, default = False),
		'disallow_social_group_placement': Tunable(description = '\n            If checked, any routing surface this object provides will not be \n            considered a valid location for forming a social group. Instead,\n            a new location adjacent to the object will be chosen.\n            ', tunable_type = bool, default = False),
		'wall_object_padding': OptionalTunable(description = '\n            If checked, this allows padding offset to be set specific to the target\n            object. Otherwise the default value in is used. This is in particular used when\n            the object is deep within the wall and lies outside sim constraints.       \n            ', tunable = Tunable(float, WALL_OBJECT_POSITION_PADDING))
	}
	_commodity_flags = None
	_preroll_commodity_flags = None
	additional_interaction_constraints = None
	_has_reservation_tests = False
	_specific_supported_posture_types = None
	_supported_posture_families = None
	_provided_mobile_posture_types = None

	def __init__ (self, definition, **kwargs):
		super().__init__(definition, tuned_native_components = self._components_native, **kwargs)
		self._dynamic_commodity_flags_map = None
		self._dynamic_animation_overrides = None
		self._cached_commodity_flags = None
		self._cached_locations_for_posture = ()
		self._cached_position_and_routing_surface_for_posture = ()
		self.mark_get_locations_for_posture_needs_update()
		tuned_part_data = self.get_part_data()
		if tuned_part_data:
			self._parts = []
			for part_data in tuned_part_data:
				self._parts.append(objects.part.Part(self, part_data))
		self.item_location = ItemLocation.INVALID_LOCATION
		for component_factory in self._components.values():
			if component_factory is not None:
				component = component_factory(self)
				for sub_component in component.get_subcomponents_gen():
					self.add_component(sub_component)
		if self._persistence == PersistenceType.NONE:
			self._persistence_group = PersistenceGroups.NONE
		else:
			self._persistence_group = PersistenceGroups.OBJECT
		self._registered_transition_controllers = None
		if self.definition.negative_environment_score != 0 or (self.definition.positive_environment_score != 0 or self.definition.environment_score_mood_tags) or self.environment_score_trait_modifiers:
			self.add_dynamic_component(objects.components.types.ENVIRONMENT_SCORE_COMPONENT)

	@BaseObject.visible_to_client.getter
	def visible_to_client (self):
		if self.item_location == ItemLocation.HOUSEHOLD_INVENTORY:
			return False
		return self._visible_to_client

	@property
	def routing_master (self):
		return self.routing_component.routing_master

	@routing_master.setter
	def routing_master (self, value):
		self.routing_component.routing_master = value

	@staticmethod
	def _can_show_affordance (shift_held, affordance):
		if shift_held:
			if affordance.cheat:
				return True
			if affordance.debug and False:
				return True
		elif not affordance.debug and not affordance.cheat:
			return True
		return False

	def destroy (self, *args, **kwargs):
		if self.item_location == ItemLocation.HOUSEHOLD_INVENTORY:
			self.on_reset_destroy()
		else:
			super().destroy(*args, **kwargs)

	def on_reset_early_detachment (self, reset_reason):
		super().on_reset_early_detachment(reset_reason)
		if self._registered_transition_controllers is not None:
			for transition_controller in self._registered_transition_controllers:
				transition_controller.on_reset_early_detachment(self, reset_reason)

	def on_reset_get_interdependent_reset_records (self, reset_reason, reset_records):
		super().on_reset_get_interdependent_reset_records(reset_reason, reset_records)
		if self._registered_transition_controllers is not None:
			for transition_controller in self._registered_transition_controllers:
				transition_controller.on_reset_add_interdependent_reset_records(self, reset_reason, reset_records)

	def on_reset_internal_state (self, reset_reason):
		if reset_reason == ResetReason.BEING_DESTROYED:
			if self._registered_transition_controllers is not None:
				self._registered_transition_controllers = None
			if not self.is_sim:
				self.statistic_tracker.set_callback_alarm_calculation_supression(True)
				self.commodity_tracker.set_callback_alarm_calculation_supression(True)
		else:
			if self.parent is not None and self.parent.is_sim and not self.parent.posture_state.is_carrying(self):
				CarryingObject.snap_to_good_location_on_floor(self, starting_transform = self.parent.transform, starting_routing_surface = self.parent.routing_surface)
			self.location = self.location
		if self.routing_component is not None:
			self.routing_component.on_reset_internal_state(reset_reason)
		super().on_reset_internal_state(reset_reason)

	def add_reservation_handler (self, reservation_handler):
		pass

	def get_reservation_handlers (self):
		return ()

	def remove_reservation_handler (self, reservation_handler):
		pass

	def register_transition_controller (self, controller):
		if self._registered_transition_controllers is None:
			self._registered_transition_controllers = set()
		self._registered_transition_controllers.add(controller)

	def unregister_transition_controller (self, controller):
		if self._registered_transition_controllers is not None:
			self._registered_transition_controllers.discard(controller)
			if not self._registered_transition_controllers:
				self._registered_transition_controllers = None

	@property
	def _use_locations_for_posture_for_connect_to_sim_test (self):
		return False

	def _get_locations_for_posture_internal_no_location (self):
		pass

	def _get_wall_object_positional_padding (self):
		return self.wall_object_padding or WALL_OBJECT_POSITION_PADDING

	def _get_locations_for_posture_internal_forward_wall_padding (self):
		return self.position + self.forward * self._get_wall_object_positional_padding()

	def _get_locations_for_posture_internal_world_transform (self):
		return self.location.world_transform.translation

	def _bind_get_locations_for_posture_internal (self):
		if self.location is None:
			logger.error('Trying to get a posture location for an object {} that has no location.', self, owner = 'shouse')
			self._get_locations_for_posture_internal = self._get_locations_for_posture_internal_no_location
		if self.routing_surface is None:
			if self.is_in_inventory():
				self._get_locations_for_posture_internal = self._get_locations_for_posture_internal_no_location
				return
			logger.error('About to create a position where routing surface is None for obj {} and object not in inventory', self, owner = 'shouse')
		if self.wall_or_fence_placement:
			self._get_locations_for_posture_internal = self._get_locations_for_posture_internal_forward_wall_padding
		else:
			self._get_locations_for_posture_internal = self._get_locations_for_posture_internal_world_transform

	def _rebind_and_get_locations_for_posture_internal (self):
		self._bind_get_locations_for_posture_internal()
		return self._get_locations_for_posture_internal()

	def mark_get_locations_for_posture_needs_update (self):
		self._get_locations_for_posture_internal = self._rebind_and_get_locations_for_posture_internal
		self.get_locations_for_posture = self._cache_and_return_get_locations_for_posture
		self.get_position_and_routing_surface_for_posture = self._cache_and_return_get_position_and_routing_surface_for_posture

	def _cached_get_locations_for_posture (self, node):
		return self._cached_locations_for_posture

	def _cache_and_return_get_locations_for_posture (self, node):
		self.get_locations_for_posture = self._cached_get_locations_for_posture
		position = self._get_locations_for_posture_internal()
		if position is None:
			self._cached_locations_for_posture = ()
			return self._cached_locations_for_posture
		self._cached_locations_for_posture = (routing.Location(position, orientation = self.orientation, routing_surface = self.routing_surface),)
		return self._cached_locations_for_posture

	def _cached_get_position_and_routing_surface_for_posture (self, node):
		return self._cached_position_and_routing_surface_for_posture

	def _cache_and_return_get_position_and_routing_surface_for_posture (self, node):
		self.get_position_and_routing_surface_for_posture = self._cached_get_position_and_routing_surface_for_posture
		position = self._get_locations_for_posture_internal()
		if position is None:
			self._cached_position_and_routing_surface_for_posture = ()
			return self._cached_position_and_routing_surface_for_posture
		routing_surface = self.routing_surface
		self._cached_position_and_routing_surface_for_posture = [(position, routing_surface)]
		if routing_surface.type == SurfaceType.SURFACETYPE_OBJECT:
			world_routing_surface = SurfaceIdentifier(routing_surface.primary_id, routing_surface.secondary_id, SurfaceType.SURFACETYPE_WORLD)
			self._cached_position_and_routing_surface_for_posture.append((position, world_routing_surface))
		return self._cached_position_and_routing_surface_for_posture

	@classmethod
	def _tuning_loaded_callback (cls):
		cls._has_reservation_tests = any(sa.object_reservation_tests for sa in cls._super_affordances)
		specific_supported_posture_types = defaultdict(set)
		supported_posture_families = set()
		for super_affordance in cls._super_affordances:
			provided_posture_type = super_affordance.provided_posture_type
			if provided_posture_type is None:
				continue
			specific_supported_posture_types[provided_posture_type].add(super_affordance)
			supported_posture_families.add(provided_posture_type.family_name)
		if specific_supported_posture_types:
			cls._specific_supported_posture_types = frozendict(specific_supported_posture_types)
		if supported_posture_families:
			cls._supported_posture_families = frozenset(supported_posture_families)
		if cls.provided_mobile_posture_affordances:
			cls._provided_mobile_posture_types = frozenset({ affordance.provided_posture_type for affordance in cls.provided_mobile_posture_affordances })
		cls_affordance_tuning_component = cls._components.affordance_tuning
		if cls_affordance_tuning_component:
			object_tuning_id = cls.guid64
			for (affordance, affordance_tuning) in cls_affordance_tuning_component.affordance_map.items():
				affordance.clear_registered_callbacks_for_object_tuning_id(object_tuning_id)
				for basic_extra in affordance_tuning.basic_extras:
					if hasattr(basic_extra.factory, AFFORDANCE_LOADED_CALLBACK_STR):
						basic_extra.factory.on_affordance_loaded_callback(affordance, basic_extra, object_tuning_id = object_tuning_id)
				for basic_extra in affordance_tuning.outcome.get_basic_extras_gen():
					if hasattr(basic_extra.factory, AFFORDANCE_LOADED_CALLBACK_STR):
						basic_extra.factory.on_affordance_loaded_callback(affordance, basic_extra, object_tuning_id = object_tuning_id)

	@staticmethod
	def __reload_update_class__ (oldobj, newobj, update):
		newobj._has_reservation_tests = any(sa.object_reservation_tests for sa in newobj._super_affordances)
		return newobj

	@classmethod
	def _verify_tuning_callback (cls):
		for (i, part_data) in enumerate(cls.get_part_data()):
			if part_data.forward_direction_for_picking.magnitude() != 1.0:
				logger.warn('On {}, forward_direction_for_picking is {} on part {}, which is not a normalized vector.', cls, part_data.forward_direction_for_picking, i, owner = 'bhill')
		posture_providing_interactions = { }
		for sa in cls._super_affordances:
			if sa._provided_posture_type is not None:
				keys = [(sa._provided_posture_type, sa._provided_posture_type_species)]
				if cls.get_part_data():
					keys = [(sa._provided_posture_type, sa._provided_posture_type_species, i) for (i, part_data) in enumerate(cls.get_part_data()) if part_data.part_definition.supported_affordance_data.compatibility(sa)]
				for key in keys:
					if key in posture_providing_interactions:
						logger.error('{} has two interactions providing the same posture: {} and {}. This is not allowed', cls.__name__, sa.__name__, posture_providing_interactions[key].__name__)
					posture_providing_interactions[key] = sa
			if sa.allow_user_directed and not sa.display_name:
				logger.error('Interaction {} on {} does not have a valid display name.', sa.__name__, cls.__name__)
			if not sa.consumes_object():
				if sa.contains_stat(CraftingTuning.CONSUME_STATISTIC):
					logger.error('ScriptObject: Interaction {} on {} is consume affordance, should tune on ConsumableComponent of the object.', sa.__name__, cls.__name__, owner = 'tastle/cjiang')
			logger.error('ScriptObject: Interaction {} on {} is consume affordance, should tune on ConsumableComponent of the object.', sa.__name__, cls.__name__, owner = 'tastle/cjiang')
		cls_state_component = cls._components.state
		if cls_state_component:
			affordance_set = set(cls._super_affordances)
			for state in cls_state_component._tuned_values.states:
				all_state_affordances = set()
				default_value = state.default_value
				if hasattr(default_value, 'state'):
					actual_state = default_value.state
				else:
					default_value = default_value[0].state
					actual_state = default_value.state
				if actual_state is None:
					logger.error('ScriptObject: state value {} on object {} has no state', default_value.__name__, cls.__name__, owner = 'nabaker')
				else:
					for state_value in actual_state.values:
						all_state_affordances = all_state_affordances | state_value.super_affordances
						intersection = affordance_set & state_value.super_affordances
						for sa in intersection:
							logger.error('ScriptObject: Interaction {} in state value {}  in state {} on object {} already exist on object or other state', sa.__name__, state_value.__name__, actual_state.__name__, cls.__name__, owner = 'nabaker')
						for sa in state_value.super_affordances:
							if sa.allow_user_directed and not sa.display_name:
								logger.error('ScriptObject: Interaction {} in state value {}  in state {} on object {} does not have a valid display name.', sa.__name__, state_value.__name__, actual_state.__name__, cls.__name__, owner = 'nabaker')
					affordance_set = affordance_set | all_state_affordances
		else:
			if cls._components.season_aware_component is not None:
				logger.error(f'Season Aware Component is tuned on {cls} but there is no State Component, things will not work.', owner = 'jdimailig')
			if cls._components.narrative_aware_component is not None:
				logger.error(f'Narrative Aware Component is tuned on {cls} but there is no State Component, things will not work.', owner = 'jdimailig')
		cls_curfew_component = cls._components.curfew
		if cls_curfew_component:
			tuned_values = list(cls_curfew_component._tuned_values.times_set.keys())
			if list(CurfewService.ALLOWED_CURFEW_TIMES) != tuned_values:
				logger.error("Tuning for curfew Component on {} doesn't have the correct tuning. Valid times for curfew are {} and tuned values are {}", cls, CurfewService.ALLOWED_CURFEW_TIMES, tuned_values)

	@classmethod
	def get_part_data (cls):
		if cls._part_data:
			return cls._part_data
		return cls._part_data_map

	@classmethod
	def update_commodity_flags (cls):
		commodity_flags = set(flag for sa in cls._super_affordances for flag in sa.commodity_flags)
		if commodity_flags:
			cls._commodity_flags = tuple(commodity_flags)
		else:
			cls._commodity_flags = EMPTY_SET

	@classmethod
	def has_updated_commodity_flags (cls):
		return cls._commodity_flags is not None

	@classmethod
	def clear_commodity_flags (cls):
		cls._commodity_flags = None

	@property
	def commodity_flags (self):
		if self._commodity_flags is None:
			self.update_commodity_flags()
			self._cached_commodity_flags = None
		if self._cached_commodity_flags is None:
			if self._dynamic_commodity_flags_map is None:
				dynamic_commodity_flags = EMPTY_SET
			else:
				dynamic_commodity_flags = frozenset(flag for commodity_set in self._dynamic_commodity_flags_map.values() for flag in commodity_set)
			self._cached_commodity_flags = frozenset(self._commodity_flags) | dynamic_commodity_flags
		return self._cached_commodity_flags

	@classmethod
	def _update_preroll_commodity_flags (cls):
		cls._preroll_commodity_flags = frozenset(flag for sa in cls._preroll_super_affordances for flag in sa.commodity_flags)

	@property
	def preroll_commodity_flags (self):
		if self._preroll_commodity_flags is None:
			self._update_preroll_commodity_flags()
		return self._preroll_commodity_flags

	def update_component_commodity_flags (self, affordance_provider = None):
		commodity_flags = frozenset(flag for sa in self.component_super_affordances_gen() for flag in sa.commodity_flags)
		if commodity_flags:
			self.add_dynamic_commodity_flags(COMMODITY_FLAGS_FROM_COMPONENTS_KEY, commodity_flags)
		else:
			self.remove_dynamic_commodity_flags(COMMODITY_FLAGS_FROM_COMPONENTS_KEY)

	def add_dynamic_commodity_flags (self, key, commodity_flags):
		if self._dynamic_commodity_flags_map is None:
			self._dynamic_commodity_flags_map = { }
		self._dynamic_commodity_flags_map[key] = commodity_flags
		self._cached_commodity_flags = None

	def remove_dynamic_commodity_flags (self, key):
		if self._dynamic_commodity_flags_map is not None:
			if key in self._dynamic_commodity_flags_map:
				del self._dynamic_commodity_flags_map[key]
				self._cached_commodity_flags = None
			if not self._dynamic_commodity_flags_map:
				self._dynamic_commodity_flags_map = None

	@classproperty
	def tuned_components (cls):
		return cls._components

	@flexmethod
	def get_allowed_hands (cls, inst, *args, **kwargs):
		if inst is not None:
			carryable_component = inst.carryable_component
			if carryable_component is not None:
				return carryable_component.get_allowed_hands(*args, **kwargs)
			return ()
		else:
			carryable_tuning = cls._components.carryable
			if carryable_tuning is not None:
				return carryable_tuning.allowed_hands_data.get_allowed_hands(*args, **kwargs)
		return ()

	def is_surface (self, *args, **kwargs):
		return False

	def add_dynamic_animation_overrides (self, anim_overrides):
		if self._dynamic_animation_overrides is None:
			self._dynamic_animation_overrides = []
		self._dynamic_animation_overrides.append(anim_overrides)

	def remove_dynamic_animation_overrides (self, anim_overrides):
		if self._dynamic_animation_overrides is not None:
			if anim_overrides in self._dynamic_animation_overrides:
				self._dynamic_animation_overrides.remove(anim_overrides)
			if not self._dynamic_animation_overrides:
				self._dynamic_animation_overrides = None

	@property
	def in_pool (self):
		current_zone_id = services.current_zone_id()
		parent = self.parent
		if parent is not None:
			routing_surface = parent.routing_surface
		else:
			routing_surface = self.location.routing_surface
		if routing_surface.type == SurfaceType.SURFACETYPE_OBJECT:
			return False
		return build_buy.is_location_pool(current_zone_id, self.location.transform.translation, routing_surface.secondary_id)

	@classproperty
	def _anim_overrides_cls (cls):
		if cls._anim_overrides is not None:
			return cls._anim_overrides(None)

	@property
	def _anim_overrides_internal (self):
		params = {
			'isParented': self.parent is not None,
			'heightAboveFloor': slots.get_surface_height_parameter_for_object(self),
			'objectPosition': self.position,
			'objectOrientation': self.orientation,
			'hasChildren': True if self.children else False
		}
		if not self.is_sim:
			for (param_name, param_value) in self._default_anim_params.items():
				params[param_name] = param_value
		if self.routing_surface is not None:
			params['isBobbing'] = self.routing_surface.type == SurfaceType.SURFACETYPE_POOL and not self.in_pool
		if self.is_part:
			params['subroot'] = self.part_suffix
			params['isMirroredPart'] = True if self.is_mirrored() else False
		overrides = AnimationOverrides(params = params)
		if self._anim_overrides is not None:
			overrides = overrides(self._anim_overrides())
		for component_overrides in self.component_anim_overrides_gen():
			overrides = overrides(component_overrides())
		if self.apply_children_component_anim_overrides:
			for obj in self.children:
				if not obj.is_prop:
					for component_overrides in obj.component_anim_overrides_gen():
						overrides = overrides(component_overrides())
		if self._dynamic_animation_overrides is not None:
			for dynamic_overrides in self._dynamic_animation_overrides:
				overrides = overrides(dynamic_overrides())
		return overrides

	@forward_to_components_gen
	def component_anim_overrides_gen (self):
		pass

	@property
	def parent (self):
		pass

	def ancestry_gen (self):
		obj = self
		while obj is not None:
			yield obj
			if obj.is_part:
				obj = obj.part_owner
			else:
				obj = obj.parent

	@property
	def parent_slot (self):
		pass

	@property
	def remove_children_from_posture_graph_on_delete (self):
		return True

	def get_closest_parts_to_position (self, position, posture = None, posture_spec = None, restrict_autonomy_preference = False, has_name = False):
		best_parts = set()
		best_distance = MAX_FLOAT
		if position is not None:
			if self.parts is not None:
				for part in self.parts:
					if part.part_definition is not None:
						if part.part_definition.can_pick:
							if not posture is None:
								if part.supports_posture_type(posture):
									if not posture_spec is None:
										if part.supports_posture_spec(posture_spec):
											if not restrict_autonomy_preference is False:
												if part.restrict_autonomy_preference:
													if not has_name is False:
														if part.part_name is not None:
															dist = (part.position_with_forward_offset - position).magnitude_2d_squared()
															if dist < best_distance:
																best_parts.clear()
																best_parts.add(part)
																best_distance = dist
															elif dist == best_distance:
																best_parts.add(part)
													dist = (part.position_with_forward_offset - position).magnitude_2d_squared()
													if dist < best_distance:
														best_parts.clear()
														best_parts.add(part)
														best_distance = dist
													elif dist == best_distance:
														best_parts.add(part)
											if not has_name is False:
												if part.part_name is not None:
													dist = (part.position_with_forward_offset - position).magnitude_2d_squared()
													if dist < best_distance:
														best_parts.clear()
														best_parts.add(part)
														best_distance = dist
													elif dist == best_distance:
														best_parts.add(part)
											dist = (part.position_with_forward_offset - position).magnitude_2d_squared()
											if dist < best_distance:
												best_parts.clear()
												best_parts.add(part)
												best_distance = dist
											elif dist == best_distance:
												best_parts.add(part)
									if not restrict_autonomy_preference is False:
										if part.restrict_autonomy_preference:
											if not has_name is False:
												if part.part_name is not None:
													dist = (part.position_with_forward_offset - position).magnitude_2d_squared()
													if dist < best_distance:
														best_parts.clear()
														best_parts.add(part)
														best_distance = dist
													elif dist == best_distance:
														best_parts.add(part)
											dist = (part.position_with_forward_offset - position).magnitude_2d_squared()
											if dist < best_distance:
												best_parts.clear()
												best_parts.add(part)
												best_distance = dist
											elif dist == best_distance:
												best_parts.add(part)
									if not has_name is False:
										if part.part_name is not None:
											dist = (part.position_with_forward_offset - position).magnitude_2d_squared()
											if dist < best_distance:
												best_parts.clear()
												best_parts.add(part)
												best_distance = dist
											elif dist == best_distance:
												best_parts.add(part)
									dist = (part.position_with_forward_offset - position).magnitude_2d_squared()
									if dist < best_distance:
										best_parts.clear()
										best_parts.add(part)
										best_distance = dist
									elif dist == best_distance:
										best_parts.add(part)
							if not posture_spec is None:
								if part.supports_posture_spec(posture_spec):
									if not restrict_autonomy_preference is False:
										if part.restrict_autonomy_preference:
											if not has_name is False:
												if part.part_name is not None:
													dist = (part.position_with_forward_offset - position).magnitude_2d_squared()
													if dist < best_distance:
														best_parts.clear()
														best_parts.add(part)
														best_distance = dist
													elif dist == best_distance:
														best_parts.add(part)
											dist = (part.position_with_forward_offset - position).magnitude_2d_squared()
											if dist < best_distance:
												best_parts.clear()
												best_parts.add(part)
												best_distance = dist
											elif dist == best_distance:
												best_parts.add(part)
									if not has_name is False:
										if part.part_name is not None:
											dist = (part.position_with_forward_offset - position).magnitude_2d_squared()
											if dist < best_distance:
												best_parts.clear()
												best_parts.add(part)
												best_distance = dist
											elif dist == best_distance:
												best_parts.add(part)
									dist = (part.position_with_forward_offset - position).magnitude_2d_squared()
									if dist < best_distance:
										best_parts.clear()
										best_parts.add(part)
										best_distance = dist
									elif dist == best_distance:
										best_parts.add(part)
							if not restrict_autonomy_preference is False:
								if part.restrict_autonomy_preference:
									if not has_name is False:
										if part.part_name is not None:
											dist = (part.position_with_forward_offset - position).magnitude_2d_squared()
											if dist < best_distance:
												best_parts.clear()
												best_parts.add(part)
												best_distance = dist
											elif dist == best_distance:
												best_parts.add(part)
									dist = (part.position_with_forward_offset - position).magnitude_2d_squared()
									if dist < best_distance:
										best_parts.clear()
										best_parts.add(part)
										best_distance = dist
									elif dist == best_distance:
										best_parts.add(part)
							if not has_name is False:
								if part.part_name is not None:
									dist = (part.position_with_forward_offset - position).magnitude_2d_squared()
									if dist < best_distance:
										best_parts.clear()
										best_parts.add(part)
										best_distance = dist
									elif dist == best_distance:
										best_parts.add(part)
							dist = (part.position_with_forward_offset - position).magnitude_2d_squared()
							if dist < best_distance:
								best_parts.clear()
								best_parts.add(part)
								best_distance = dist
							elif dist == best_distance:
								best_parts.add(part)
		return best_parts

	def is_same_object_or_part (self, obj):
		if not isinstance(obj, ScriptObject):
			return False
		if obj is self:
			return True
		if obj.is_part and obj.part_owner is self or self.is_part and self.part_owner is obj:
			return True
		elif obj.is_part and self.is_part and obj.part_owner is self.part_owner:
			return True
		return False

	def get_compatible_parts (self, posture):
		if posture is not None and posture.target is not None and posture.target.is_part:
			return (posture.target,)
		return self.get_parts_for_posture(posture)

	def get_parts_for_posture (self, posture):
		if self.parts is not None:
			return (part for part in self.parts if part.supports_posture_type(posture.posture_type))
		return ()

	def may_reserve (self, *args, **kwargs):
		return True

	@property
	def build_buy_lockout (self):
		return False

	@property
	def route_target (self):
		return (RouteTargetType.NONE, None)

	@flexmethod
	def super_affordances (cls, inst, context = None):
		inst_or_cls = inst if inst is not None else cls
		component_affordances_gen = inst.component_super_affordances_gen(context = context) if inst is not None else EMPTY_SET
		for sa in itertools.chain(inst_or_cls._super_affordances, component_affordances_gen):
			if sa.is_affordance_available(context = context):
				yield sa
		if inst is not None:
			for affordance in inst._potential_behavior_affordances_gen(context):
				yield affordance

	@forward_to_components_gen
	def component_super_affordances_gen (self, context = None):
		pass

	@caches.cached_generator
	def get_posture_aops_gen (self):
		if self._specific_supported_posture_types is not None:
			for affordance in itertools.chain.from_iterable(self._specific_supported_posture_types.values()):
				if affordance.debug:
					continue
				yield from affordance.potential_interactions(self, None)

	@classproperty
	def provided_mobile_posture_affordances (cls):
		return EMPTY_SET

	@classproperty
	def provided_mobile_posture_types (cls):
		return cls._provided_mobile_posture_types or frozenset()

	def supports_affordance (self, affordance):
		return True

	def potential_interactions (self, context, get_interaction_parameters = None, allow_forwarding = True, **kwargs):
		try:
			for affordance in self.super_affordances(context):
				if not self.supports_affordance(affordance):
					continue
				if get_interaction_parameters is not None:
					interaction_parameters = get_interaction_parameters(affordance, kwargs)
				else:
					interaction_parameters = kwargs
				for aop in affordance.potential_interactions(self, context, **interaction_parameters):
					yield aop
			for aop in self._search_forwarded_interactions(context, get_interaction_parameters = get_interaction_parameters, **kwargs):
				yield aop
			if not allow_forwarding or not self.allow_aop_forward() or self.parent is not None:
				yield from self.parent.child_provided_aops_gen(self, context, **kwargs)
			club_service = services.get_club_service()
			if club_service is not None:
				for (club, affordance) in club_service.provided_clubs_and_interactions_gen(context):
					aop = AffordanceObjectPair(affordance, self, affordance, None, associated_club = club, **kwargs)
					if aop.test(context):
						yield aop
			context_sim = context.sim
			if context_sim is not None:
				if context_sim.posture_state is not None:
					for (_, _, carried_object) in get_carried_objects_gen(context_sim):
						yield from carried_object.get_provided_aops_gen(self, context, **kwargs)
			if context_sim is not None:
				yield from context_sim.get_object_provided_target_affordances_gen(self, context, **kwargs)
		except Exception:
			logger.exception('Exception while generating potential interactions for {}:', self)

	def potential_preroll_interactions (self, context, get_interaction_parameters = None, **kwargs):
		potential_affordances = []
		try:
			for affordance in self._preroll_super_affordances:
				if not affordance.is_affordance_available(context = context):
					continue
				if not self.supports_affordance(affordance):
					continue
				if get_interaction_parameters is not None:
					interaction_parameters = get_interaction_parameters(affordance, kwargs)
				else:
					interaction_parameters = kwargs
				for aop in affordance.potential_interactions(self, context, **interaction_parameters):
					potential_affordances.append(aop)
		except Exception:
			logger.exception('Exception while generating potential interactions for {}:', self)
		finally:
			return potential_affordances

	def _potential_behavior_affordances_gen (self, context, **kwargs):
		shift_held = False
		shift_held = context.shift_held
		if not context is not None or context is not None:
			if context.sim is not None:
				for (affordance, _) in context.sim.sim_info.get_target_super_affordance_availability_gen(context, self):
					if self._can_show_affordance(shift_held, affordance):
						yield affordance
				for (affordance, _) in context.sim.sim_info.trait_tracker.get_cached_target_super_affordances_gen(context, self):
					if self._can_show_affordance(shift_held, affordance):
						yield affordance
				for (affordance, _) in context.sim.sim_info.commodity_tracker.get_cached_target_super_affordances_gen(context, self):
					if self._can_show_affordance(shift_held, affordance):
						yield affordance
				for (affordance, _) in context.sim.sim_info.unlock_tracker.get_cached_target_super_affordances_gen(context, self):
					if self._can_show_affordance(shift_held, affordance):
						yield affordance
				if not context.sim.sim_info.unlock_tracker is not None or context.sim.career_tracker is not None:
					for (affordance, _) in context.sim.career_tracker.get_cached_target_super_affordances_gen(context, self):
						if self._can_show_affordance(shift_held, affordance):
							yield affordance

	def allow_aop_forward (self):
		return self.aop_forward_data.should_search_forwarded_sim_aop or self.aop_forward_data.should_search_forwarded_child_aop

	def supports_posture_type (self, posture_type, *args, is_specific = True, **kwargs):
		if is_specific:
			if self._specific_supported_posture_types is None:
				return False
			if posture_type in self._specific_supported_posture_types:
				return True
		elif self._supported_posture_families is None:
			return False
		elif posture_type.family_name in self._supported_posture_families:
			return True
		return False

	def _search_forwarded_interactions (self, context, **kwargs):

		def allowed_interactions_gen (source, context, **kwargs):
			for aop in source.potential_interactions(context, **kwargs):
				if aop.affordance.is_affordance_available(context = context):
					if aop.affordance.is_allowed_to_forward(self):
						yield aop

		if self.aop_forward_data.should_search_forwarded_sim_aop:
			all_users = set()
			while True:
				for part_or_object in itertools.chain(self.parts if self.parts else [], (self,)):
					user_list = part_or_object.get_users(sims_only = True)
					for user in user_list:
						if part_or_object.is_part and part_or_object.disable_child_aop_forwarding:
							continue
						all_users.add(user)
			for user in all_users:
				yield from allowed_interactions_gen(user, context, **kwargs)
		if not self.aop_forward_data.should_search_forwarded_child_aop:
			return
		for child in self.children:
			if child.parent is None:
				logger.error('{} is not a child of {}, but has no parent set.', child, self)
			else:
				if child.parent.is_part and child.parent.disable_child_aop_forwarding:
					continue
				if self.aop_forward_data.child_obj_tags and not any(child.definition.has_build_buy_tag(tag) for tag in self.aop_forward_data.child_obj_tags):
					continue
				yield from allowed_interactions_gen(child, context, **kwargs)
		if not self.aop_forward_data.should_search_forwarded_parent_aop:
			return
		if self.parent is not None:
			yield from allowed_interactions_gen(self.parent, context, **kwargs)

	def add_dynamic_component (self, *args, **kwargs):
		result = super().add_dynamic_component(*args, **kwargs)
		if result:
			self.resend_interactable()
		return result

	@distributor.fields.Field(op = distributor.ops.SetInteractable, default = False)
	def interactable (self):
		if self.build_buy_lockout:
			return False
		if self._super_affordances:
			return True
		for _ in self.component_interactable_gen():
			return True
		return False

	resend_interactable = interactable.get_resend()

	@forward_to_components_gen
	def component_interactable_gen (self):
		pass

	@caches.cached(maxsize = 20)
	def check_line_of_sight (self, transform, verbose = False, ignored_objects = (), for_carryable = False):
		(reference_pt, top_level_parent) = Constraint.get_validated_routing_position(self)
		if self.is_in_inventory():
			if verbose:
				return (routing.RAYCAST_HIT_TYPE_NONE, None)
			return (True, None)
		else:
			object_transform = sims4.math.Transform(self.transform.translation, self.transform.orientation)
			if top_level_parent.wall_or_fence_placement:
				if not self.has_tag(GameObjectTuning.WALL_OBJ_LOS_TUNING_FLAG):
					if verbose:
						return (routing.RAYCAST_HIT_TYPE_NONE, None)
					return (True, None)
				object_transform.translation = reference_pt
		return (True, None)
		object_transform.translation = reference_pt
		slot_routing_location = self.get_routing_location_for_transform(transform, routing_surface = top_level_parent.routing_surface)
		routing_location = self.get_routing_location_for_transform(object_transform, routing_surface = top_level_parent.routing_surface)
		ignored_footprint_ids = []
		try:
			raycast_context = self.raycast_context(for_carryable = for_carryable)
			for ignored_object in ignored_objects:
				if ignored_object is not None:
					if not ignored_object.is_sim:
						if ignored_object.routing_context is not None:
							object_footprint_id = ignored_object.routing_context.object_footprint_id
							if object_footprint_id is not None:
								if not raycast_context.is_footprint_contour_ignored(object_footprint_id):
									ignored_footprint_ids.append(object_footprint_id)
									raycast_context.ignore_footprint_contour(object_footprint_id)
			if verbose:
				(result, blocking_object_id) = routing.ray_test_verbose(slot_routing_location, routing_location, raycast_context, return_object_id = True)
				if result != routing.RAYCAST_HIT_TYPE_IMPASSABLE or blocking_object_id in services.object_manager():
					blocking_object_id = None if blocking_object_id == 0 else blocking_object_id
					return (result, blocking_object_id)
				return (routing.RAYCAST_HIT_TYPE_NONE, [])
			else:
				return routing.ray_test(slot_routing_location, routing_location, self.raycast_context(), return_object_id = True)
		finally:
			for object_footprint_id in ignored_footprint_ids:
				raycast_context.remove_footprint_contour_override(object_footprint_id)

	clear_check_line_of_sight_cache = check_line_of_sight.cache.clear

	def _create_raycast_context (self, *args, **kwargs):
		super()._create_raycast_context(*args, **kwargs)
		if not self.is_sim:
			self.clear_check_line_of_sight_cache()

	def _fill_ignored_objects_and_test_halfwalls (self, routing_context, sim_loc, obj, ignored_object_set):
		if obj in ignored_object_set:
			return (False, False)
		for ignore_object in obj.parenting_hierarchy_gen():
			if ignore_object.is_sim:
				posture_target = ignore_object.posture.target
				if posture_target is not None:
					if ignore_object.parent is not posture_target:
						(tested_halfwalls, halfwall_result) = self._fill_ignored_objects_and_test_halfwalls(routing_context, sim_loc, posture_target, ignored_object_set)
						if tested_halfwalls:
							return (tested_halfwalls, halfwall_result)
							if not ignore_object.routing_context is None:
								if ignore_object.routing_context.object_footprint_id is None:
									continue
								if ignore_object._use_locations_for_posture_for_connect_to_sim_test:
									for location in ignore_object.get_locations_for_posture(None):
										if routing.test_connectivity_pt_pt(sim_loc, location, routing_context):
											return (True, True)
									return (True, False)
								ignored_object_set.add(ignore_object)
			elif not ignore_object.routing_context is None:
				if ignore_object.routing_context.object_footprint_id is None:
					continue
				if ignore_object._use_locations_for_posture_for_connect_to_sim_test:
					for location in ignore_object.get_locations_for_posture(None):
						if routing.test_connectivity_pt_pt(sim_loc, location, routing_context):
							return (True, True)
					return (True, False)
				ignored_object_set.add(ignore_object)
		return (False, False)

	@cached
	def is_connected (self, routing_agent, ignore_all_objects = False):
		routing_context = routing_agent.get_routing_context()
		sim_loc = routing_agent.routing_location
		objects_to_ignore = set()
		if not ignore_all_objects:
			(tested_halfwalls, halfwall_result) = self._fill_ignored_objects_and_test_halfwalls(routing_context, sim_loc, self, objects_to_ignore)
			if tested_halfwalls:
				return halfwall_result
		try:
			for ignore_object in objects_to_ignore:
				routing_context.ignore_footprint_contour(ignore_object.routing_context.object_footprint_id)
			if self.forward_offset_on_connectivity_check is not None:
				destination_location = routing.Location(self.position + self.forward * self.forward_offset_on_connectivity_check, self.orientation, self.routing_surface)
			elif PlacementFlags.EDGE_AGAINST_WALL & get_object_placement_flags(self.definition.id):
				destination_location = routing.Location(self.routing_location.position + self.forward * WALL_OBJECT_POSITION_PADDING, self.routing_location.orientation, self.routing_location.routing_surface)
			else:
				destination_location = self.routing_location
			if routing.test_connectivity_pt_pt(sim_loc, destination_location, routing_context, ignore_objects = ignore_all_objects):
				return True
			elif destination_location.routing_surface.type == SurfaceType.SURFACETYPE_OBJECT:
				parent = self.parent
				if parent is not None:
					destination_location = parent.routing_location
					if routing.test_connectivity_pt_pt(sim_loc, destination_location, routing_context, ignore_objects = ignore_all_objects):
						return True
			return False
		finally:
			for ignore_object in objects_to_ignore:
				routing_context.remove_footprint_contour_override(ignore_object.routing_context.object_footprint_id)

	@property
	def connectivity_handles (self):
		routing_context = self.get_or_create_routing_context()
		return routing_context.connectivity_handles

	@forward_to_components
	def on_state_changed (self, state, old_value, new_value, from_init):
		pass

	@forward_to_components
	def on_post_load (self):
		pass

	@forward_to_components
	def on_finalize_load (self):
		if self.is_downloaded:
			services.active_lot().flag_as_premade(False)

	@property
	def attributes (self):
		pass

	@property
	def flammable (self):
		return False

	@attributes.setter
	def attributes (self, value):
		logger.debug('PERSISTENCE: Attributes property on {0} were set', self)
		try:
			if indexed_manager.capture_load_times:
				time_stamp = time.time()
			object_data = ObjectData()
			object_data.ParseFromString(value)
			self.load_object(object_data)
			if indexed_manager.capture_load_times:
				time_elapsed = time.time() - time_stamp
				indexed_manager.object_load_times[self.definition].loads += 1
				indexed_manager.object_load_times[self.definition].time_spent_loading += time_elapsed
		except:
			logger.exception('Exception applying attributes to object {0}', self)

	def load_object (self, object_data):
		save_data = protocols.PersistenceMaster()
		save_data.ParseFromString(object_data.attributes)
		self.load(save_data)
		self.on_post_load()

	def is_persistable (self, from_bb = False):
		if self.persistence_group == objects.persistence_groups.PersistenceGroups.OBJECT:
			return self._persistence == PersistenceType.FULL or from_bb and self._persistence == PersistenceType.BUILDBUY
		if self.persistence_group == objects.persistence_groups.PersistenceGroups.IN_OPEN_STREET:
			if self.item_location == ItemLocation.FROM_WORLD_FILE:
				return self._world_file_object_persists
			elif self.item_location == ItemLocation.ON_LOT or (self.item_location == ItemLocation.FROM_OPEN_STREET or self.item_location == ItemLocation.FROM_CONDITIONAL_LAYER) or self.item_location == ItemLocation.INVALID_LOCATION:
				return self._persistence == PersistenceType.FULL
		return False

	def save_object (self, object_list, item_location = ItemLocation.ON_LOT, container_id = 0, from_bb = False):
		if not self.is_persistable(from_bb = from_bb):
			return
		with ProtocolBufferRollback(object_list) as save_data:
			attribute_data = self.get_attribute_save_data()
			save_data.object_id = self.id
			if attribute_data is not None:
				save_data.attributes = attribute_data.SerializeToString()
			save_data.guid = self.definition.id
			save_data.loc_type = item_location
			save_data.container_id = container_id
			return save_data

	@cached
	def get_attribute_save_data (self):
		attribute_data = protocols.PersistenceMaster()
		self.save(attribute_data)
		return attribute_data

	@forward_to_components
	def save (self, persistence_master_message):
		pass

	def load (self, persistence_master_message):
		component_priority_list = []
		for persistable_data in persistence_master_message.data:
			component_priority_list.append((get_component_priority_and_name_using_persist_id(persistable_data.type), persistable_data))
		component_priority_list.sort(key = lambda priority: priority[0][0], reverse = True)
		for ((_, (class_attr, inst_attr)), persistable_data) in component_priority_list:
			if inst_attr:
				component_def = component_definition(class_attr, inst_attr)
				self.add_dynamic_component(component_def)
				if self.has_component(component_def):
					getattr(self, inst_attr).load(persistable_data)
				else:
					self.on_failed_to_load_component(component_def, persistable_data)

	def finalize (self, **kwargs):
		self.on_finalize_load()

	def clone (self, definition_override = None, post_add = None, **kwargs):
		clone = objects.system.create_object(definition_override or self.definition, **kwargs)
		object_list = file_serialization.ObjectList()
		save_data = self.save_object(object_list.objects)
		clone.load_object(save_data)
		if post_add is not None:
			post_add(clone)
		clone.resend_interactable()
		return clone

	@forward_to_components
	def modify_interactable_flags (self, flags):
		pass

	@forward_to_components
	def on_set_sold (self):
		pass

	@forward_to_components
	def on_restock (self):
		pass

	def claim (self):
		if self.object_claim_component is None:
			self.add_dynamic_component(objects.components.types.OBJECT_CLAIM_COMPONENT, require_claiming = True)
		services.object_manager().set_claimed_item(self.id)

	def remove_claim_requirement (self):
		if self.object_claim_component is not None:
			self.remove_component(objects.components.types.OBJECT_CLAIM_COMPONENT)
		services.object_manager().set_unclaimed_item(self.id)
