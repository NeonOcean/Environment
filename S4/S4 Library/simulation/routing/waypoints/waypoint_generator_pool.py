import random
from animation.posture_manifest_constants import SWIM_AT_NONE_CONSTRAINT
from interactions.constraints import Nowhere, create_constraint_set
from objects.pools import pool_utils
from postures.posture_graph import SIM_SWIM_POSTURE_TYPE
from routing.waypoints.waypoint_generator import _WaypointGeneratorBase
from sims4.tuning.tunable import TunableRange
import build_buy

class _WaypointGeneratorPool(_WaypointGeneratorBase):
    FACTORY_TUNABLES = {'constraint_width': TunableRange(description='\n            The width of the constraint created around the edge of the pool.\n            ', tunable_type=float, default=1.5, minimum=0), 'locked_args': {'mobile_posture_override': SIM_SWIM_POSTURE_TYPE}}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sim = self._context.sim
        position = self._target.position if self._target is not None else sim.position
        level = self._routing_surface.secondary_id
        if not build_buy.is_location_pool(sim.zone_id, position, level):
            self._start_constraint = Nowhere('SwimmingWaypointInteraction, selected position is not inside any pool on the lot.')
            self._waypoint_constraints = []
        else:
            pool_block_id = build_buy.get_block_id(sim.zone_id, position, level - 1)
            pool = pool_utils.get_pool_by_block_id(pool_block_id)
            if pool is not None:
                pool_edge_constraints = pool.get_edge_constraint(constraint_width=self.constraint_width, inward_dir=True, return_constraint_list=True)
                self._start_constraint = create_constraint_set(pool_edge_constraints)
                self._waypoint_constraints = pool_edge_constraints
            else:
                self._start_constraint = Nowhere('Failed to find pool at position: {}, level: {}', position, level - 1)
                self._waypoint_constraints = []

    def get_posture_constraint(self):
        return SWIM_AT_NONE_CONSTRAINT

    def get_start_constraint(self):
        return self._start_constraint

    def get_waypoint_constraints_gen(self, sim, waypoint_count):
        available_waypoint_count = len(self._waypoint_constraints)
        for i in range(waypoint_count):
            if i % available_waypoint_count == 0:
                random.shuffle(self._waypoint_constraints)
            yield self._waypoint_constraints[i % available_waypoint_count]
