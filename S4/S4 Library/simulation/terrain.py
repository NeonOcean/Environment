import services
from routing import SurfaceType
try:
    import _terrain
    get_lot_level_height = _terrain.get_lot_level_height
    get_lot_level_height_and_surface_object = _terrain.get_lot_level_height_and_surface_object
    get_snowmask_value = _terrain.get_snowmask_value

    def get_terrain_size(zone_id=None):
        if zone_id is None or zone_id == 0:
            zone_id = services.current_zone().id
        return _terrain.get_size(zone_id)

    def get_terrain_center(zone_id=None):
        if zone_id is None or zone_id == 0:
            zone_id = services.current_zone().id
        return _terrain.get_center(zone_id)

    def get_terrain_height(x, z, routing_surface=None):
        zone = services.current_zone()
        level = 0 if routing_surface is None else routing_surface.secondary_id
        surface_type = SurfaceType.SURFACETYPE_UNKNOWN if routing_surface is None else routing_surface.type
        val = get_lot_level_height(x, z, level, zone.id, surface_type)
        return val

    def is_position_in_bounds(x, z, zone_id=None):
        if zone_id is None or zone_id == 0:
            zone_id = services.current_zone().id
        return _terrain.is_position_in_bounds(x, z, zone_id)

    def is_position_in_street(position):
        return _terrain.is_position_in_markup_region(position)

except ImportError:

    def get_terrain_size(*args, **kwargs):
        pass

    def get_terrain_center(*args, **kwargs):
        pass

    def get_lot_level_height(*args, **kwargs):
        return 0

    def get_lot_level_height_and_surface_object(*args, **kwargs):
        pass

    def get_terrain_height(*args, **kwargs):
        return 0

    def is_position_in_bounds(*args, **kwargs):
        return False

    def is_position_in_street(*args, **kwargs):
        return False

    def get_snowmask_value(*args, **kwargs):
        return 0
