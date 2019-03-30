from interactions.constraints import Circle
from routing.waypoints.waypoint_generator import _WaypointGeneratorBase
from sims.sim_info_types import SimInfoSpawnerTags
from sims4.random import pop_weighted
from sims4.tuning.tunable import TunableRange
from world.spawn_point import SpawnPoint
import routing
import services
import sims4.math

class _WaypointGeneratorSpawnPoints(_WaypointGeneratorBase):
    FACTORY_TUNABLES = {'constraint_radius': TunableRange(description='\n            The radius, in meters, for each of the generated waypoint\n            constraints.\n            ', tunable_type=float, default=6, minimum=0)}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sim = self._context.sim
        if self._context.pick is not None:
            pick_position = self._context.pick.location
            self._pick_vector = pick_position - self._sim.position
            self._pick_vector /= self._pick_vector.magnitude()
        else:
            self._pick_vector = self._sim.forward
        if self._sim.is_on_active_lot:
            plex_service = services.get_plex_service()
            if plex_service.is_active_zone_a_plex():
                tags = (SpawnPoint.VISITOR_ARRIVAL_SPAWN_POINT_TAG,)
            else:
                tags = (SpawnPoint.ARRIVAL_SPAWN_POINT_TAG,)
            spawn_point = services.current_zone().get_spawn_point(lot_id=services.active_lot_id(), sim_spawner_tags=tags)
            self._origin_position = spawn_point.get_approximate_center()
            self._routing_surface = routing.SurfaceIdentifier(services.current_zone_id(), 0, routing.SurfaceType.SURFACETYPE_WORLD)
            self._except_lot_id = services.active_lot_id()
        else:
            self._origin_position = self._sim.position
            self._routing_surface = self._sim.routing_surface
            self._except_lot_id = None
        self._start_constraint = Circle(self._origin_position, self.constraint_radius, routing_surface=self._routing_surface, los_reference_point=None)

    def get_start_constraint(self):
        return self._start_constraint

    def get_waypoint_constraints_gen(self, sim, waypoint_count):
        zone = services.current_zone()
        constraint_set = zone.get_spawn_points_constraint(except_lot_id=self._except_lot_id, generalize=True)
        constraints_weighted = []
        min_score = sims4.math.MAX_FLOAT
        for constraint in constraint_set:
            spawn_point_vector = constraint.average_position - self._sim.position
            score = sims4.math.vector_dot_2d(self._pick_vector, spawn_point_vector)
            min_score = score
            constraints_weighted.append((score, constraint))
        constraints_weighted = [(score - min_score, constraint) for (score, constraint) in constraints_weighted]
        constraints_weighted = sorted(constraints_weighted, key=lambda i: i[0])
        first_constraint = constraints_weighted[-1][1]
        del constraints_weighted[-1]
        first_constraint_circle = Circle(first_constraint.average_position, self.constraint_radius, routing_surface=first_constraint.routing_surface)
        jog_waypoint_constraints = []
        jog_waypoint_constraints.append(first_constraint_circle)
        last_waypoint_position = first_constraint.average_position
        for _ in range(waypoint_count - 1):
            constraints_weighted_next = []
            for (_, constraint) in constraints_weighted:
                average_position = constraint.average_position
                distance_last = (average_position - last_waypoint_position).magnitude_2d()
                distance_home = (average_position - self._origin_position).magnitude_2d()
                constraints_weighted_next.append((distance_last + distance_home, constraint))
            next_constraint = pop_weighted(constraints_weighted_next)
            next_constraint_circle = Circle(next_constraint.average_position, self.constraint_radius, routing_surface=next_constraint.routing_surface)
            jog_waypoint_constraints.append(next_constraint_circle)
            constraints_weighted = constraints_weighted_next
            break
            last_waypoint_position = next_constraint.average_position
        yield from jog_waypoint_constraints
        yield self._start_constraint
