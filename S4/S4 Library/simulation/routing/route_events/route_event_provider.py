
class RouteEventProviderMixin:

    def on_event_executed(self, route_event, sim):
        pass

    def provide_route_events(self, route_event_context, sim, path, failed_types=None, start_time=0, end_time=None, **kwargs):
        raise NotImplementedError

    def is_route_event_valid(self, route_event, time, sim, path):
        raise NotImplementedError
