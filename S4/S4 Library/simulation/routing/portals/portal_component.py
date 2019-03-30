from collections import namedtuple
from animation.animation_utils import AnimationOverrides
from objects.components import Component, types, componentmethod_with_fallback, componentmethod
from objects.components.portal_locking_component import PortalLockingComponent
from routing import remove_portal
from routing.portals.portal_animation_component import PortalAnimationComponent
from routing.portals.portal_data import TunablePortalReference
from routing.portals.portal_tuning import PortalType
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, TunableList, OptionalTunable
from tag import TunableTags
import services
import sims4.utils
import tag
_PortalPair = namedtuple('_PortalPair', ['there', 'back'])

class PortalComponent(Component, HasTunableFactory, AutoFactoryInit, component_name=types.PORTAL_COMPONENT):
    FACTORY_TUNABLES = {'_portal_data': TunableList(description='\n            The portals that are to be created for this object.\n            ', tunable=TunablePortalReference(pack_safe=True)), '_portal_animation_component': OptionalTunable(description='\n            If enabled, this portal animates in response to agents traversing\n            it. Use Enter/Exit events to control when and for how long an\n            animation plays.\n            ', tunable=PortalAnimationComponent.TunableFactory()), '_portal_locking_component': OptionalTunable(description='\n            If enabled then this object will be capable of being locked using\n            the same system as Portal Objects.\n            \n            If not enabled then it will not have a portal locking component\n            and will therefore not be lockable.\n            ', tunable=PortalLockingComponent.TunableFactory()), '_portal_disallowed_tags': TunableTags(description='\n            A set of tags used to prevent Sims in particular role states from\n            using this portal.\n            ', filter_prefixes=tag.PORTAL_DISALLOWANCE_PREFIX)}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._portals = {}

    def get_subcomponents_gen(self):
        yield from super().get_subcomponents_gen()
        if self._portal_locking_component is not None:
            portal_locking_component = self._portal_locking_component(self.owner)
            yield from portal_locking_component.get_subcomponents_gen()
        if self._portal_animation_component is not None:
            portal_animation_component = self._portal_animation_component(self.owner)
            yield from portal_animation_component.get_subcomponents_gen()

    def on_buildbuy_exit(self, *_, **__):
        self._refresh_portals()

    def on_location_changed(self, *_, **__):
        zone = services.current_zone()
        if zone.is_in_build_buy or zone.is_zone_loading:
            return
        self._refresh_portals()

    def finalize_portals(self):
        self._refresh_portals()

    def _refresh_portals(self):
        self._remove_portals()
        self._add_portals()
        self.owner.refresh_locks()

    def on_add(self, *_, **__):
        services.object_manager().add_portal_to_cache(self.owner)

    def on_remove(self, *_, **__):
        self._remove_portals()
        services.object_manager().remove_portal_from_cache(self.owner)

    @componentmethod
    @sims4.utils.exception_protected(default_return=0)
    def c_api_get_portal_duration(self, portal_id, walkstyle, age, gender, species):
        portal = self._portals.get(portal_id)
        if portal is not None:
            return portal.get_portal_duration(portal_id, walkstyle, age, gender, species)
        return 0

    @componentmethod
    def add_portal_data(self, portal_id, actor, walkstyle):
        portal = self._portals.get(portal_id)
        if portal is not None:
            return portal.add_portal_data(portal_id, actor, walkstyle)

    @componentmethod
    def split_path_on_portal(self, portal_id):
        portal = self._portals.get(portal_id)
        if portal is not None:
            return portal.split_path_on_portal(portal_id)
        return False

    @componentmethod
    def get_posture_change(self, portal_id, initial_posture):
        portal = self._portals.get(portal_id)
        if portal is not None:
            return portal.get_posture_change(portal_id, initial_posture)
        return (initial_posture, initial_posture)

    @componentmethod
    def add_portal_events(self, portal_id, actor, time, route_pb):
        for portal_data in self._portal_data:
            portal_data.traversal_type.add_portal_events(portal_id, actor, self.owner, time, route_pb)

    @componentmethod
    def get_portal_anim_overrides(self):
        return AnimationOverrides()

    @componentmethod
    def get_portal_owner(self, portal_id):
        portal = self._portals.get(portal_id)
        if portal is not None:
            return portal.obj
        return self.owner

    @componentmethod
    def get_target_surface(self, portal_id, sim):
        portal = self._portals.get(portal_id)
        if portal is not None:
            return portal.get_target_surface(portal_id, sim)
        return self.owner.routing_surface

    def _add_portals(self):
        for portal_data in self._portal_data:
            self._add_portal_internal(self.owner, portal_data)
        if self.owner.parts is not None:
            for part in self.owner.parts:
                part_definition = part.part_definition
                for portal_data in part_definition.portal_data:
                    self._add_portal_internal(part, portal_data)

    def _add_portal_internal(self, obj, portal_data):
        for portal in portal_data.get_portal_instances(obj):
            if portal.there is not None:
                self._portals[portal.there] = portal
            if portal.back is not None:
                self._portals[portal.back] = portal

    def _remove_portals(self):
        for portal_id in self._portals:
            remove_portal(portal_id)
        self._portals.clear()

    @componentmethod_with_fallback(lambda *_, **__: False)
    def has_portals(self, check_parts=True):
        if self._portal_data:
            return True
        elif check_parts and self.owner.parts is not None:
            return any(part.part_definition is not None and part.part_definition.portal_data is not None for part in self.owner.parts)
        return False

    @componentmethod_with_fallback(lambda *_, **__: [])
    def get_portal_pairs(self):
        return set(_PortalPair(portal.there, portal.back) for portal in self._portals.values())

    @componentmethod_with_fallback(lambda *_, **__: None)
    def get_portal_data(self):
        return self._portal_data

    @componentmethod
    def get_portal_instances(self):
        return frozenset(self._portals.values())

    @componentmethod
    def get_portal_type(self, portal_id):
        portal = self._portals.get(portal_id)
        if portal is not None:
            return portal.portal_type
        return PortalType.PortalType_Animate

    @componentmethod
    def update_portal_cache(self, portal, portal_id):
        self._portals[portal_id] = portal

    @componentmethod_with_fallback(lambda *_, **__: None)
    def get_portal_by_id(self, portal_id):
        return self._portals.get(portal_id, None)

    @componentmethod_with_fallback(lambda *_, **__: ())
    def get_dynamic_portal_locations_gen(self):
        for portal_data in self._portal_data:
            yield from portal_data.get_dynamic_portal_locations_gen(self.owner)

    @componentmethod
    def get_single_portal_locations(self):
        portal_pair = next(iter(self._portals.values()), None)
        if portal_pair is not None:
            portal_there = self.get_portal_by_id(portal_pair.there)
            portal_back = self.get_portal_by_id(portal_pair.back)
            front_location = None
            if portal_there is not None:
                front_location = portal_there.there_entry
            back_location = None
            if portal_back is not None:
                back_location = portal_back.back_entry
            return (front_location, back_location)
        return (None, None)

    @componentmethod
    def set_portal_cost_override(self, portal_id, cost, sim=None):
        portal = self._portals.get(portal_id)
        if portal is not None:
            portal.set_portal_cost_override(cost, sim=sim)

    @componentmethod
    def get_portal_cost(self, portal_id):
        portal = self._portals.get(portal_id)
        if portal is not None:
            return portal.get_portal_cost(portal_id)

    @componentmethod
    def get_portal_cost_override(self, portal_id):
        portal = self._portals.get(portal_id)
        if portal is not None:
            return portal.get_portal_cost_override()

    @componentmethod
    def clear_portal_cost_override(self, portal_id, sim=None):
        portal = self._portals.get(portal_id)
        if portal is not None:
            portal.clear_portal_cost_override(sim=sim)

    @componentmethod
    def is_ungreeted_sim_disallowed(self):
        return any(p.is_ungreeted_sim_disallowed() for p in self._portals.values())

    @componentmethod
    def get_portal_disallowed_tags(self):
        return self._portal_disallowed_tags

    @componentmethod
    def get_entry_clothing_change(self, interaction, portal_id, **kwargs):
        portal = self._portals.get(portal_id)
        if portal is not None:
            return portal.get_entry_clothing_change(interaction, portal_id, **kwargs)

    @componentmethod
    def get_exit_clothing_change(self, interaction, portal_id, **kwargs):
        portal = self._portals.get(portal_id)
        if portal is not None:
            return portal.get_exit_clothing_change(interaction, portal_id, **kwargs)

    @componentmethod
    def get_on_entry_outfit(self, interaction, portal_id, **kwargs):
        portal = self._portals.get(portal_id)
        if portal is not None:
            return portal.get_on_entry_outfit(interaction, portal_id, **kwargs)

    @componentmethod
    def get_on_exit_outfit(self, interaction, portal_id, **kwargs):
        portal = self._portals.get(portal_id)
        if portal is not None:
            return portal.get_on_exit_outfit(interaction, portal_id, **kwargs)

    @componentmethod
    def get_gsi_portal_items_list(self, key_name, value_name):
        gsi_portal_items = self.owner.get_gsi_portal_items(key_name, value_name)
        return gsi_portal_items

    @componentmethod
    def get_nearest_posture_change(self, sim):
        shortest_dist = sims4.math.MAX_FLOAT
        nearest_portal_id = None
        nearest_portal = None
        sim_position = sim.position
        for (portal_id, portal_instance) in self._portals.items():
            (posture_entry, posture_exit) = portal_instance.get_posture_change(portal_id, None)
            if posture_entry is posture_exit:
                pass
            else:
                (entry_loc, _) = portal_instance.get_portal_locations(portal_id)
                dist = (entry_loc.position - sim_position).magnitude_squared()
                if not nearest_portal is None:
                    if shortest_dist > dist:
                        shortest_dist = dist
                        nearest_portal = portal_instance
                        nearest_portal_id = portal_id
                shortest_dist = dist
                nearest_portal = portal_instance
                nearest_portal_id = portal_id
        if nearest_portal is None:
            return (None, None)
        return nearest_portal.get_posture_change(nearest_portal_id, None)

    @componentmethod_with_fallback(lambda *_, **__: False)
    def has_posture_portals(self):
        for (portal_id, portal_instance) in self._portals.items():
            (posture_entry, _) = portal_instance.get_posture_change(portal_id, None)
            if posture_entry is not None:
                return True
