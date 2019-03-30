from routing.portals.portal_event import TunablePortalEventVariant
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableList

class _PortalTypeDataBase(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'portal_events': TunableList(description='\n            A list of portal events to add when a Sim uses the portal.\n            ', tunable=TunablePortalEventVariant(description='\n                The tuning for a specific portal event.\n                '))}

    @property
    def portal_type(self):
        raise NotImplementedError

    @property
    def outfit_change(self):
        pass

    @property
    def requires_los_between_points(self):
        return True

    def add_portal_data(self, actor, portal_instance, is_mirrored, walkstyle):
        pass

    def add_portal_events(self, portal, actor, obj, time, route_pb):
        for portal_event in self.portal_events:
            op = portal_event.get_portal_op(actor, obj)
            event = route_pb.events.add()
            event.time = max(0, time + portal_event.time)
            event.type = portal_event.get_portal_event_type()
            event.data = op.SerializeToString()

    def get_destination_objects(self):
        return ()

    def get_portal_duration(self, portal_instance, is_mirrored, walkstyle, age, gender, species):
        raise NotImplementedError

    def get_portal_locations(self, obj):
        raise NotImplementedError

    def get_posture_change(self, portal_instance, is_mirrored, initial_posture):
        return (initial_posture, initial_posture)

    def is_ungreeted_sim_disallowed(self):
        return False

    def split_path_on_portal(self):
        return False
