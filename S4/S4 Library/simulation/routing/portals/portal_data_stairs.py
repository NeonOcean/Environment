from protocolbuffers import Routing_pb2 as routing_protocols
from routing import Location
from routing.portals.portal_data_base import _PortalTypeDataBase
from routing.portals.portal_tuning import PortalType, PortalFlags
from sims4 import hash_util
import build_buy
import routing
import sims4.log
logger = sims4.log.Logger('Portal')

class _PortalTypeDataStairs(_PortalTypeDataBase):

    @property
    def portal_type(self):
        return PortalType.PortalType_Animate

    def get_stair_count(self, obj):
        return build_buy.get_stair_count(obj.id, obj.zone_id)

    def add_portal_data(self, actor, portal_instance, is_mirrored, walkstyle):
        node_data = routing_protocols.RouteNodeData()
        obj = portal_instance.obj
        stair_count = self.get_stair_count(obj)
        node_data.type = routing_protocols.RouteNodeData.DATA_STAIRS
        op = routing_protocols.RouteStairsData()
        op.traversing_up = not is_mirrored
        op.stair_count = stair_count
        op.walkstyle = walkstyle
        op.stairs_per_cycle = 1
        node_data.data = op.SerializeToString()
        node_data.do_stop_transition = True
        node_data.do_start_transition = True
        return node_data

    def get_portal_duration(self, portal_instance, is_mirrored, walkstyle, age, gender, species):
        walkstyle_info_dict = routing.get_walkstyle_info_full(walkstyle, age, gender, species)
        builder_name = hash_util.hash32('stairs_down_cycle') if is_mirrored else hash_util.hash32('stairs_up_cycle')
        if builder_name not in walkstyle_info_dict:
            builder_name = hash_util.hash32('stairs_down_cycle_r') if is_mirrored else hash_util.hash32('stairs_up_cycle_r')
            if builder_name not in walkstyle_info_dict:
                logger.error('Failed to find stair builder for walkstyle {}.', walkstyle)
                return 0
        obj = portal_instance.obj
        stair_count = self.get_stair_count(obj)
        info = walkstyle_info_dict[builder_name]
        duration = info['duration']*stair_count
        return duration

    def get_portal_locations(self, obj):
        stair_lanes = routing.get_stair_portals(obj.id, obj.zone_id)
        if not stair_lanes:
            return ()
        locations = []
        for lane in stair_lanes:
            ((there_start, there_end), (back_start, back_end)) = lane
            (there_start_position, there_start_routing_surface) = there_start
            (there_end_position, there_end_routing_surface) = there_end
            (back_start_position, back_start_routing_surface) = back_start
            (back_end_position, back_end_routing_surface) = back_end
            if there_start_routing_surface == there_end_routing_surface:
                required_flags = PortalFlags.STAIRS_PORTAL_SHORT
            else:
                required_flags = PortalFlags.STAIRS_PORTAL_LONG
            locations.append((Location(there_start_position, routing_surface=there_start_routing_surface), Location(there_end_position, routing_surface=there_end_routing_surface), Location(back_start_position, routing_surface=back_start_routing_surface), Location(back_end_position, routing_surface=back_end_routing_surface), required_flags))
        return locations
