import enum
import placement
import services
import sims4.log
import sims4.math
from distributor.rollback import ProtocolBufferRollback
from event_testing.resolver import DoubleSimResolver
from event_testing.tests import TunableTestSet
from interactions.constraint_variants import TunableConstraintVariant
from interactions.constraints import ANYWHERE
from placement import FGLSearchFlag, FGLSearchFlagsDefault, FGLSearchFlagsDefaultForSim, FindGoodLocationContext
from postures import DerailReason
from protocolbuffers import Routing_pb2
from routing.formation.formation_behavior import RoutingFormationBehavior
from routing.formation.formation_liability import RoutingFormationLiability
from routing.route_enums import RoutingStageEvent
from routing.walkstyle.walkstyle_request import WalkStyleRequest
from routing.walkstyle.walkstyle_tuning import TunableWalkstyle
from sims4 import math
from sims4.geometry import RelativeFacingRange
from sims4.math import Location, MAX_INT32, Quaternion, Vector2, Vector3
from sims4.tuning.geometric import TunableVector2
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import HasTunableReference, Tunable, TunableList, TunableMapping, TunableRange, TunableReference
from sims4.utils import classproperty
from tunable_utils.tunable_white_black_list import TunableWhiteBlackList

logger = sims4.log.Logger('RoutingFormations', default_owner = 'rmccord')

class RoutingFormationFollowType(enum.Int, export = False):
	NODE_TYPE_FOLLOW_LEADER = 0
	NODE_TYPE_CHAIN = 1

class _RoutingFormationAttachmentNode:
	__slots__ = ('_parent_offset', '_offset', '_radius', '_angle_constraint', '_flags', '_type')

	def __init__ (self, parent_offset: Vector2, offset: Vector2, radius, angle_constraint, flags, node_type):
		self._parent_offset = parent_offset
		self._offset = offset
		self._radius = radius
		self._angle_constraint = angle_constraint
		self._flags = flags
		self._type = node_type

	@property
	def parent_offset (self):
		return self._parent_offset

	@property
	def offset (self):
		return self._offset

	@property
	def radius (self):
		return self._radius

	@property
	def node_type (self):
		return self._type

	def populate_attachment_pb (self, attachment_pb):
		attachment_pb.parent_offset.x = self._parent_offset.x
		attachment_pb.parent_offset.y = self._parent_offset.y
		attachment_pb.offset.x = self._offset.x
		attachment_pb.offset.y = self._offset.y
		attachment_pb.radius = self._radius
		attachment_pb.angle_constraint = self._angle_constraint
		attachment_pb.flags = self._flags
		attachment_pb.type = self._type

class RoutingFormation(HasTunableReference, metaclass = HashedTunedInstanceMetaclass, manager = services.snippet_manager()):
	ATTACH_NODE_COUNT = 3
	ATTACH_NODE_RADIUS = 0.25
	ATTACH_NODE_ANGLE = math.PI
	ATTACH_NODE_FLAGS = 4
	RAYTRACE_HEIGHT = 1.5
	RAYTRACE_RADIUS = 0.1
	INSTANCE_TUNABLES = {
		'formation_behavior': RoutingFormationBehavior.TunableFactory(),
		'formation_offsets': TunableList(description = '\n            A list of offsets, relative to the master, that define where slaved\n            Sims are positioned.\n            ', tunable = TunableVector2(default = Vector2.ZERO()), minlength = 1),
		'formation_constraints': TunableList(description = '\n            A list of constraints that slaved Sims must satisfy any time they\n            run interactions while in this formation. This can be a geometric\n            constraint, for example, that ensures Sims are always placed within\n            a radius or cone of their slaved position.\n            ', tunable = TunableConstraintVariant(constraint_locked_args = {
			'multi_surface': True
		}, circle_locked_args = {
			'require_los': False
		}, disabled_constraints = { 'spawn_points', 'relative_circle' })),
		'formation_compatibility': TunableWhiteBlackList(description = '\n            This routing formation is able to coexist with any other formation\n            listed here. For example, "Walk Dog" on the right side of a Sim is\n            compatible with "Walk Dog" on their left side (and vice-versa).\n            ', tunable = TunableReference(manager = services.get_instance_manager(sims4.resources.Types.SNIPPET), class_restrictions = ('RoutingFormation',), pack_safe = True)),
		'route_length_minimum': TunableRange(description = '\n            Sims are slaved in formation only if the route is longer that this\n            amount, in meters. Furthermore, routes shorter than this distance\n            will not interrupt behavior (e.g. a socializing Sim will not force\n            dogs to get up and move around)\n            ', tunable_type = float, default = 1, minimum = 0),
		'formation_tests': TunableTestSet(description = '\n            A test set to determine whether or not the master and slave can be\n            in a formation together.\n            \n            Master: Participant Actor\n            Slave: Participant Slave\n            '),
		'walkstyle_mapping': TunableMapping(description = '\n            Mapping of Master walkstyles to Slave walkstyles. This is how we\n            ensure that slaves use a walkstyle to keep pace with their masters.\n            \n            Note you do not need to worry about combo replacement walkstyles\n            like GhostRun or GhostWalk. We get the first non-combo from the\n            master and apply the walkstyle to get any combos from the slave.\n            ', key_type = TunableWalkstyle(description = '\n                The walkstyle that the master must be in to apply the value\n                walkstyle to the slave.\n                '), value_type = WalkStyleRequest.TunableFactory(), key_name = 'Master Walkstyle', value_name = 'Slave Walkstyle Request'),
		'slave_should_face_master': Tunable(description = '\n            If enabled, the Slave should attempt to face the master at the end\n            of routes.\n            ', tunable_type = bool, default = False),
		'should_increase_master_agent_radius': Tunable(description = "\n            If enabled, we combine the slave's agent radius with the master's.\n            ", tunable_type = bool, default = True)
	}

	def __init__ (self, master, slave, *args, interaction = None, **kwargs):
		super().__init__(*args, **kwargs)
		self._master = master
		self._slave = slave
		self._attachment_chain = []
		formation_count = master.get_routing_slave_data_count(self.formation_type)
		self._formation_offset = self.formation_offsets[formation_count]
		self._formation_behavior = self.formation_behavior(master, slave)
		self._setup_right_angle_connections()
		self._offset = Vector3.ZERO()
		for attachment_info in self._attachment_chain:
			self._offset.x = self._offset.x + attachment_info.parent_offset.x - attachment_info.offset.x
			self._offset.z = self._offset.z + attachment_info.parent_offset.y - attachment_info.offset.y
		master.routing_component.add_routing_slave(self)
		self._slave_constraint = None
		if interaction is not None:
			formation_liability = RoutingFormationLiability(self)
			interaction.add_liability(formation_liability.LIABILITY_TOKEN, formation_liability)
		else:
			logger.callstack('Routing Formation created without an interaction, this should not happen. Slave: {} Master: {} Formation: {}', slave, master, self)
			self.release_formation_data()
		self._slave_lock = None

	@classmethod
	def test_formation (cls, master, slave):
		test_slave = slave.sim_info if slave.is_sim else slave
		resolver = DoubleSimResolver(master.sim_info, test_slave)
		return cls.formation_tests.run_tests(resolver)

	@classproperty
	def formation_type (cls):
		return cls

	@property
	def master (self):
		return self._master

	@property
	def slave (self):
		return self._slave

	@property
	def offset (self):
		return self._formation_offset

	def on_add (self):
		self.master.register_routing_stage_event(RoutingStageEvent.ROUTE_START, self._on_master_route_start)
		self.master.register_routing_stage_event(RoutingStageEvent.ROUTE_END, self._on_master_route_end)
		self._formation_behavior.on_add()

	def on_release (self):
		self._unlock_slave()
		self._formation_behavior.on_release()
		self.master.unregister_routing_stage_event(RoutingStageEvent.ROUTE_START, self._on_master_route_start)
		self.master.unregister_routing_stage_event(RoutingStageEvent.ROUTE_END, self._on_master_route_end)

	def attachment_info_gen (self):
		yield from self._attachment_chain

	def _on_master_route_start (self, sim_info, routing_stage_event, **kwargs):
		self._build_routing_slave_constraint()
		self._lock_slave()
		if self._slave.is_sim:
			for si in self._slave.get_all_running_and_queued_interactions():
				if si.transition is not None and si.transition is not self.master.transition_controller:
					si.transition.derail(DerailReason.CONSTRAINTS_CHANGED, self._slave)

	def _on_master_route_end (self, sim_info, routing_stage_event, **kwargs):
		self._build_routing_slave_constraint()
		if self._slave.is_sim:
			for si in self._slave.get_all_running_and_queued_interactions():
				if si.transition is not None and si.transition is not self.master.transition_controller:
					si.transition.derail(DerailReason.CONSTRAINTS_CHANGED, self._slave)
		self._unlock_slave()

	def _lock_slave (self):
		self._slave_lock = self._slave.add_work_lock(self)

	def _unlock_slave (self):
		self._slave.remove_work_lock(self)

	def _build_routing_slave_constraint (self):
		self._slave_constraint = ANYWHERE
		for constraint in self.formation_constraints:
			constraint = constraint.create_constraint(self._slave, target = self._master, target_position = self._master.intended_position)
			self._slave_constraint = self._slave_constraint.intersect(constraint)

	def get_routing_slave_constraint (self):
		if self._slave_constraint is None or not self._slave_constraint.valid:
			self._build_routing_slave_constraint()
		return self._slave_constraint

	def _add_attachment_node (self, parent_offset: Vector2, offset: Vector2, radius, angle_constraint, flags, node_type):
		attachment_node = _RoutingFormationAttachmentNode(parent_offset, offset, radius, angle_constraint, flags, node_type)
		self._attachment_chain.append(attachment_node)

	def get_walkstyle_override (self):
		walkstyle_request = self.walkstyle_mapping.get(self.master.get_walkstyle())
		slaved_walkstyle = self._slave.get_walkstyle()
		if walkstyle_request is not None:
			with self._slave.routing_component.temporary_walkstyle_request(walkstyle_request):
				slaved_walkstyle = self._slave.get_walkstyle()
		return slaved_walkstyle

	def find_good_location_for_slave (self, master_location):
		restrictions = []
		fgl_kwargs = { }
		fgl_flags = 0
		if self.slave_should_face_master:
			restrictions.append(RelativeFacingRange(master_location.transform.translation, 0))
			fgl_kwargs = {
				'raytest_radius': RoutingFormation.RAYTRACE_RADIUS,
				'raytest_start_offset': RoutingFormation.RAYTRACE_HEIGHT,
				'raytest_end_offset': RoutingFormation.RAYTRACE_HEIGHT,
				'ignored_object_ids': { self.master.id, self.slave.id },
				'max_distance': self._offset.magnitude(),
				'min_distance': self._offset.magnitude()
			}
			fgl_flags = FGLSearchFlag.SHOULD_RAYTEST | FGLSearchFlag.SPIRAL_INWARDS
			slave_position = master_location.transform.translation
			orientation = master_location.transform.orientation
			orientation_offset = sims4.math.angle_to_yaw_quaternion(sims4.math.vector3_angle(sims4.math.vector_normalize(self._offset)))
			orientation = Quaternion.concatenate(orientation, orientation_offset)
			starting_location = placement.create_starting_location(position = slave_position, orientation = orientation, routing_surface = master_location.routing_surface)
		else:
			slave_position = master_location.transform.transform_point(self._offset)
			starting_location = placement.create_starting_location(position = slave_position, orientation = master_location.transform.orientation, routing_surface = master_location.routing_surface)
		if self.slave.is_sim:
			fgl_flags |= FGLSearchFlagsDefaultForSim
			fgl_context = placement.create_fgl_context_for_sim(starting_location, self.slave, search_flags = fgl_flags, restrictions = restrictions, **fgl_kwargs)
		else:
			fgl_flags |= FGLSearchFlagsDefault
			footprint = self.slave.get_footprint()
			fgl_context = FindGoodLocationContext(starting_location, object_id = self.slave.id, object_footprints = (footprint,) if footprint is not None else None, search_flags = fgl_flags, restrictions = restrictions, **fgl_kwargs)
		(new_position, new_orientation) = placement.find_good_location(fgl_context)
		if new_position is None or new_orientation is None:
			logger.info('No good location found for {} after slaved in a routing formation headed to {}.', self.slave, starting_location, owner = 'rmccord')
			return sims4.math.Transform(Vector3(*starting_location.position), Quaternion(*starting_location.orientation))
		new_position.y = services.terrain_service.terrain_object().get_routing_surface_height_at(slave_position.x, slave_position.z, master_location.routing_surface)
		final_transform = sims4.math.Transform(new_position, new_orientation)
		return final_transform

	def add_routing_slave_to_pb (self, route_pb, path = None):
		slave_pb = route_pb.slaves.add()
		slave_pb.id = self._slave.id
		slave_pb.type = Routing_pb2.SlaveData.SLAVE_FOLLOW_ATTACHMENT
		walkstyle_override_msg = slave_pb.walkstyle_overrides.add()
		walkstyle_override_msg.from_walkstyle = 0
		walkstyle_override_msg.to_walkstyle = self.get_walkstyle_override()
		for (from_walkstyle, to_walkstyle_request) in self.walkstyle_mapping.items():
			walkstyle_override_msg = slave_pb.walkstyle_overrides.add()
			walkstyle_override_msg.from_walkstyle = from_walkstyle
			with self._slave.routing_component.temporary_walkstyle_request(to_walkstyle_request):
				walkstyle_override_msg.to_walkstyle = self._slave.get_walkstyle()
		for attachment_node in self._attachment_chain:
			with ProtocolBufferRollback(slave_pb.offset) as attachment_pb:
				attachment_node.populate_attachment_pb(attachment_pb)
		if path is not None:
			starting_location = path.final_location
		else:
			starting_location = self.master.intended_location
		slave_transform = self.find_good_location_for_slave(starting_location)
		if slave_transform is not None:
			slave_loc = slave_pb.final_location_override
			(slave_loc.translation.x, slave_loc.translation.y, slave_loc.translation.z) = slave_transform.translation
			(slave_loc.orientation.x, slave_loc.orientation.y, slave_loc.orientation.z, slave_loc.orientation.w) = slave_transform.orientation
		return (self._slave, slave_pb)

	def release_formation_data (self):
		self._unlock_slave()
		self._master.routing_component.clear_slave(self._slave)

	def _setup_right_angle_connections (self):
		formation_offset_x = Vector2(self._formation_offset.x / 6.0, 0.0)
		formation_offset_y = Vector2(0.0, self._formation_offset.y)
		for _ in range(self.ATTACH_NODE_COUNT):
			self._add_attachment_node(formation_offset_x, formation_offset_x * -1, self.ATTACH_NODE_RADIUS, 0, self.ATTACH_NODE_FLAGS, RoutingFormationFollowType.NODE_TYPE_FOLLOW_LEADER)
		self._setup_direct_connections(formation_offset_y)

	def _setup_direct_connections (self, formation_offset):
		formation_vector_magnitude = formation_offset.magnitude()
		normalized_offset = formation_offset / formation_vector_magnitude
		attachment_node_step = formation_vector_magnitude / ((self.ATTACH_NODE_COUNT - 1) * 2)
		attachment_vector = normalized_offset * attachment_node_step
		for i in range(0, self.ATTACH_NODE_COUNT - 1):
			flags = self.ATTACH_NODE_FLAGS
			if i == self.ATTACH_NODE_COUNT - 2:
				flags = 5
			self._add_attachment_node(attachment_vector, attachment_vector * -1, self.ATTACH_NODE_RADIUS, self.ATTACH_NODE_ANGLE, flags, RoutingFormationFollowType.NODE_TYPE_CHAIN)

	def should_slave_for_path (self, path):
		path_length = path.length() if path is not None else MAX_INT32
		final_path_node = path.nodes[-1]
		final_position = sims4.math.Vector3(*final_path_node.position)
		final_orientation = sims4.math.Quaternion(*final_path_node.orientation)
		routing_surface = final_path_node.routing_surface_id
		final_position.y = services.terrain_service.terrain_object().get_routing_surface_height_at(final_position.x, final_position.z, routing_surface)
		final_transform = sims4.math.Transform(final_position, final_orientation)
		slave_position = final_transform.transform_point(self._offset)
		slave_position.y = services.terrain_service.terrain_object().get_routing_surface_height_at(slave_position.x, slave_position.z, routing_surface)
		final_dist_sq = (slave_position - self.slave.position).magnitude_squared()
		if path_length >= self.route_length_minimum or final_dist_sq >= self.route_length_minimum * self.route_length_minimum:
			return True
		return False

	def update_slave_position (self, master_transform, master_orientation, routing_surface, distribute = True, path = None):
		if distribute:
			slave_transform = self.find_good_location_for_slave(Location(master_transform, routing_surface))
			slave_position = slave_transform.translation
		else:
			slave_position = master_transform.transform_point(self._offset)
			slave_transform = sims4.math.Transform(slave_position, master_orientation)
		if path is not None and path.length() < self.route_length_minimum and (self._slave.position - slave_position).magnitude_squared() < self.route_length_minimum * self.route_length_minimum:
			return
		if distribute:
			self._slave.move_to(routing_surface = routing_surface, transform = slave_transform)
		else:
			location = self.slave.location.clone(routing_surface = routing_surface, transform = slave_transform)
			self.slave.set_location_without_distribution(location)
