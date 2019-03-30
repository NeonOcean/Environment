from animation.animation_utils import StubActor
from animation.arb import Arb
from interactions.constraints import get_global_stub_actor, GLOBAL_STUB_CONTAINER
from postures.base_postures import MobilePosture
from postures.posture_specs import get_origin_spec_carry, get_origin_spec
from routing import Location
from routing.portals.portal_data_base import _PortalTypeDataBase
from routing.portals.portal_location import TunableRoutingSurfaceVariant
from routing.portals.portal_tuning import PortalType
from sims.outfits.outfit_change import TunableOutfitChange
from sims.sim_info_types import SpeciesExtended
from sims4.tuning.tunable import OptionalTunable
import postures
import sims4.log
logger = sims4.log.Logger('Portal', default_owner='rmccord')

class _PortalTypeDataPosture(_PortalTypeDataBase):
    FACTORY_TUNABLES = {'posture_start': MobilePosture.TunableReference(description='\n            Define the entry posture as you cross through this portal. e.g. For\n            the pool, the start posture is stand.\n            '), 'routing_surface_start': TunableRoutingSurfaceVariant(description="\n            The routing surface of the portal's entry position. Sims are on this\n            surface while in the starting posture.\n            "), 'posture_end': MobilePosture.TunableReference(description='\n            Define the exit posture as you cross through this portal. e.g. For\n            the pool, the end posture is swim.\n            '), 'routing_surface_end': TunableRoutingSurfaceVariant(description="\n            The routing surface of the portal's exit position. Sims are on this\n            surface when in the ending posture.\n            "), '_outfit_change': OptionalTunable(tunable=TunableOutfitChange(description='\n                Define the outfit change that happens when a Sim enters or exits\n                this portal.\n                '))}

    @property
    def portal_type(self):
        return PortalType.PortalType_Animate

    @property
    def outfit_change(self):
        return self._outfit_change

    def get_portal_duration(self, portal_instance, is_mirrored, walkstyle, age, gender, species):
        stub_actor = StubActor(1, species=species)
        arb = Arb()
        portal_posture = postures.create_posture(self.posture_end, stub_actor, GLOBAL_STUB_CONTAINER)
        source_posture = postures.create_posture(self.posture_start, stub_actor, None)
        portal_posture.append_transition_to_arb(arb, source_posture, locked_params={('age', 'x'): age, 'is_mirrored': is_mirrored})
        (_, duration, _) = arb.get_timing()
        return duration

    def get_posture_change(self, portal_instance, is_mirrored, initial_posture):
        if initial_posture is not None and initial_posture.carry_target is not None:
            start_posture = get_origin_spec_carry(self.posture_start)
            end_posture = get_origin_spec_carry(self.posture_end)
        else:
            start_posture = get_origin_spec(self.posture_start)
            end_posture = get_origin_spec(self.posture_end)
        if is_mirrored:
            return (end_posture, start_posture)
        else:
            return (start_posture, end_posture)

    def split_path_on_portal(self):
        return True

    def get_portal_locations(self, obj):
        species_portals = []
        routing_surface_start = self.routing_surface_start(obj)
        routing_surface_end = self.routing_surface_end(obj)

        def get_outer_portal_goal(slot_constraint, stub_actor, entry=True):
            handles = slot_constraint.get_connectivity_handles(stub_actor, entry=entry)
            if not handles:
                logger.error('PosturePortal: Species {} has no entry boundary conditions for portal posture', species)
                return
            species_param = SpeciesExtended.get_animation_species_param(stub_actor.species)
            for handle in handles:
                handle_species_param = handle.locked_params.get(('species', 'x'))
                if handle_species_param is None:
                    break
                if handle_species_param == species_param:
                    break
            return
            return next(iter(handle.get_goals()), None)

        posture_species = self.posture_end.get_animation_species()
        for species in SpeciesExtended:
            if SpeciesExtended.get_species(species) not in posture_species:
                pass
            else:
                stub_actor = get_global_stub_actor(species)
                portal_posture = postures.create_posture(self.posture_end, stub_actor, obj, is_throwaway=True)
                slot_constraint = portal_posture.slot_constraint
                containment_constraint = next(iter(slot_constraint))
                there_start = get_outer_portal_goal(slot_constraint, stub_actor)
                if there_start is None:
                    pass
                else:
                    there_end = containment_constraint.containment_transform
                    back_start = containment_constraint.containment_transform_exit
                    back_end = get_outer_portal_goal(slot_constraint, stub_actor, entry=False)
                    if back_end is None:
                        pass
                    else:
                        there_entry = Location(there_start.position, orientation=there_start.orientation, routing_surface=routing_surface_start)
                        there_exit = Location(there_end.translation, orientation=there_end.orientation, routing_surface=routing_surface_end)
                        back_entry = Location(back_start.translation, orientation=back_start.orientation, routing_surface=routing_surface_end)
                        back_exit = Location(back_end.position, orientation=back_end.orientation, routing_surface=routing_surface_start)
                        species_portals.append((there_entry, there_exit, back_entry, back_exit, SpeciesExtended.get_portal_flag(species)))
        return species_portals
