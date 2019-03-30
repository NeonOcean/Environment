import itertools
from event_testing.resolver import DoubleSimResolver
from relationships.global_relationship_tuning import RelationshipGlobalTuning
from relationships.tunable import RelationshipTrackData2dLink
from singletons import DEFAULT
import services
import sims4.log
from statistics.base_statistic_tracker import BaseStatisticTracker
logger = sims4.log.Logger('Relationship', default_owner='msantander')

class RelationshipTrackTracker(BaseStatisticTracker):
    __slots__ = ('_rel_data', 'load_in_progress', '_longterm_tracks_locked')

    def __init__(self, rel_data):
        super().__init__()
        self._rel_data = rel_data
        self.load_in_progress = False
        self._longterm_tracks_locked = False

    def set_longterm_tracks_locked(self, value):
        self._longterm_tracks_locked = value
        self.enable_player_sim_track_decay()

    def is_track_locked(self, track):
        return self._longterm_tracks_locked and not track.is_short_term_context

    @property
    def rel_data(self):
        return self._rel_data

    def add_statistic(self, stat_type, owner=None, **kwargs):
        if self.is_track_locked(stat_type):
            return
        if stat_type.species_requirements is not None:
            sim_info_a = services.sim_info_manager().get(self.rel_data.sim_id_a)
            sim_info_b = services.sim_info_manager().get(self.rel_data.sim_id_b)
            if sim_info_a is not None and sim_info_b is not None:
                sim_a_species = sim_info_a.species
                sim_b_species = sim_info_b.species
                species_list_one = stat_type.species_requirements.species_list_one
                species_list_two = stat_type.species_requirements.species_list_two
                if (sim_a_species not in species_list_one or sim_b_species not in species_list_two) and (sim_b_species not in species_list_one or sim_a_species not in species_list_two):
                    return
                if sim_info_a.trait_tracker.hide_relationships or sim_info_b.trait_tracker.hide_relationships:
                    return
        relationship_track = super().add_statistic(stat_type, owner=owner, **kwargs)
        relationship_service = services.relationship_service()
        for relationship_multipliers in itertools.chain(relationship_service.get_relationship_multipliers_for_sim(self._rel_data.sim_id_a), relationship_service.get_relationship_multipliers_for_sim(self._rel_data.sim_id_b)):
            for (rel_track, multiplier) in relationship_multipliers.items():
                if rel_track is stat_type:
                    relationship_track.add_statistic_multiplier(multiplier)
        if self.load_in_progress or relationship_track.tested_initial_modifier is not None:
            sim_info_a = services.sim_info_manager().get(self.rel_data.sim_id_a)
            sim_info_b = services.sim_info_manager().get(self.rel_data.sim_id_b)
            if sim_info_a is None or sim_info_b is None:
                return relationship_track
            modified_amount = relationship_track.tested_initial_modifier.get_max_modifier(DoubleSimResolver(sim_info_a, sim_info_b))
            relationship_track.add_value(modified_amount)
        return relationship_track

    def set_value(self, stat_type, value, apply_initial_modifier=False, **kwargs):
        modified_amount = 0.0
        if stat_type.tested_initial_modifier is not None:
            sim_info_a = services.sim_info_manager().get(self.rel_data.sim_id_a)
            sim_info_b = services.sim_info_manager().get(self.rel_data.sim_id_b)
            if sim_info_b is not None:
                modified_amount = stat_type.tested_initial_modifier.get_max_modifier(DoubleSimResolver(sim_info_a, sim_info_b))
        super().set_value(stat_type, value + modified_amount, **kwargs)

    def get_statistic(self, stat_type, add=False):
        if stat_type is DEFAULT:
            stat_type = RelationshipGlobalTuning.REL_INSPECTOR_TRACK
        if stat_type is None:
            logger.error('stat_type is None in RelationshipTrackTracker.get_statistic()', owner='jjacobson')
            return
        return super().get_statistic(stat_type, add)

    def trigger_test_event(self, sim_info, event):
        if sim_info is None:
            return
        services.get_event_manager().process_event(event, sim_info=sim_info, sim_id=sim_info.sim_id, target_sim_id=self._rel_data.relationship.find_other_sim_id(sim_info.sim_id))

    def save(self):
        raise NotImplementedError

    def load(self, load_list):
        raise NotImplementedError

    def enable_player_sim_track_decay(self, to_enable=True):
        if self._statistics is None:
            return
        for track in self._statistics.values():
            if track.decay_only_affects_played_sims:
                logger.debug('    Updating track {} for {}', track, self._rel_data)
                track.reset_decay_alarm(use_cached_time=True)

    def are_all_tracks_that_cause_culling_at_convergence(self):
        if self._statistics is None:
            return True
        tracks_that_cause_culling_at_convergence = [track for track in self._statistics.values() if track.causes_delayed_removal_on_convergence]
        if not tracks_that_cause_culling_at_convergence:
            return False
        for track in tracks_that_cause_culling_at_convergence:
            if not track.is_at_convergence():
                return False
        return True
