from autonomy.autonomy_modifier import AutonomyModifier, TunableAutonomyModifier
from game_effect_modifier.affordance_reference_scoring_modifier import TunableAffordanceScoringModifier
from game_effect_modifier.continuous_statistic_modifier import ContinuousStatisticModifier
from game_effect_modifier.statistic_static_modifier import StatisticStaticModifier
from game_effect_modifier.effective_skill_modifier import EffectiveSkillModifier
from game_effect_modifier.game_effect_type import GameEffectType
from game_effect_modifier.mood_effect_modifier import MoodEffectModifier
from game_effect_modifier.relationship_track_decay_locker import RelationshipTrackDecayLocker
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, TunableList, TunableVariant
from whims.whim_modifiers import SatisfactionPointMultiplierModifier, SatisfactionPointPeriodicGainModifier
import sims4.log
logger = sims4.log.Logger('GameEffectModifiers')

class TunableGameEffectVariant(TunableVariant):

    def __init__(self, description='A single game effect modifier.', **kwargs):
        super().__init__(autonomy_modifier=TunableAutonomyModifier(), affordance_modifier=TunableAffordanceScoringModifier(locked_args={'modifier_type': GameEffectType.AFFORDANCE_MODIFIER}), effective_skill_modifier=EffectiveSkillModifier.TunableFactory(), continuous_statistic_modifier=ContinuousStatisticModifier.TunableFactory(), relationship_track_decay_locker=RelationshipTrackDecayLocker.TunableFactory(), satisfaction_point_multiplier=SatisfactionPointMultiplierModifier.TunableFactory(), satisfaction_point_gain=SatisfactionPointPeriodicGainModifier.TunableFactory(), mood_effect_modifier=MoodEffectModifier.TunableFactory(), statistic_static_modifier=StatisticStaticModifier.TunableFactory(), description=description, **kwargs)

class GameEffectModifiers(HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'_game_effect_modifiers': TunableList(description='\n            A list of game effect modifiers', tunable=TunableGameEffectVariant())}

    def __init__(self, owner, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._owner = owner
        self._autonomy_modifier_handles = []
        self._topic_modifiers = []
        self._affordance_modifiers = []
        self._effective_skill_modifiers = []
        self._continuous_statistic_modifiers = []
        self._relationship_track_decay_lockers = []
        self._whim_modifiers = []
        self._mood_effect_modifiers = []
        self._statistic_static_modifiers = []

    def on_add(self):
        for modifier in self._game_effect_modifiers:
            if isinstance(modifier, AutonomyModifier):
                handle = self._owner.add_statistic_modifier(modifier)
                self._autonomy_modifier_handles.append(handle)
            elif isinstance(modifier, (SatisfactionPointMultiplierModifier, SatisfactionPointPeriodicGainModifier)):
                modifier.apply_modifier(self._owner, self)
                self._whim_modifiers.append(modifier)
            elif modifier.modifier_type == GameEffectType.AFFORDANCE_MODIFIER:
                self._affordance_modifiers.append(modifier)
            elif modifier.modifier_type == GameEffectType.EFFECTIVE_SKILL_MODIFIER:
                self._effective_skill_modifiers.append(modifier)
            elif modifier.modifier_type == GameEffectType.CONTINUOUS_STATISTIC_MODIFIER:
                modifier.apply_modifier(self._owner)
                self._continuous_statistic_modifiers.append(modifier)
            elif modifier.modifier_type == GameEffectType.RELATIONSHIP_TRACK_DECAY_LOCKER:
                modifier.apply_modifier(self._owner)
                self._relationship_track_decay_lockers.append(modifier)
            elif modifier.modifier_type == GameEffectType.MOOD_EFFECT_MODIFIER:
                self._mood_effect_modifiers.append(modifier)
            elif modifier.modifier_type == GameEffectType.STATISTIC_STATIC_MODIFIER:
                modifier.apply_modifier(self._owner)
                self._statistic_static_modifiers.append(modifier)

    def on_remove(self, on_destroy=False):
        if not on_destroy:
            for modifier in self._continuous_statistic_modifiers:
                if modifier.modifier_type == GameEffectType.CONTINUOUS_STATISTIC_MODIFIER:
                    modifier.remove_modifier(self._owner)
            for modifier in self._relationship_track_decay_lockers:
                if modifier.modifier_type == GameEffectType.RELATIONSHIP_TRACK_DECAY_LOCKER:
                    modifier.remove_modifier(self._owner)
            for modifier in self._whim_modifiers:
                modifier.remove_modifier(self._owner, self)
            for handle in self._autonomy_modifier_handles:
                self._owner.remove_statistic_modifier(handle)
            for modifier in self._statistic_static_modifiers:
                if modifier.modifier_type == GameEffectType.STATISTIC_STATIC_MODIFIER:
                    modifier.remove_modifier(self._owner)
        self._autonomy_modifier_handles.clear()
        self._autonomy_modifier_handles = []
        self._effective_skill_modifiers.clear()
        self._effective_skill_modifiers = []
        self._continuous_statistic_modifiers.clear()
        self._continuous_statistic_modifiers = []
        self._relationship_track_decay_lockers.clear()
        self._relationship_track_decay_lockers = []
        self._whim_modifiers = []
        self._mood_effect_modifiers = []
        self._statistic_static_modifiers = []

    def get_affordance_scoring_modifier(self, affordance, resolver):
        return sum(modifier.get_score_for_type(affordance, resolver) for modifier in self._affordance_modifiers)

    def get_affordance_success_modifier(self, affordance, resolver):
        return sum(modifier.get_success_for_type(affordance, resolver) for modifier in self._affordance_modifiers)

    def get_affordance_new_pie_menu_icon_and_parent_name(self, affordance, resolver):
        icon = None
        parent = None
        icon_tag = None
        parent_tag = None
        for modifier in self._affordance_modifiers:
            (new_icon, new_parent, new_tag) = modifier.get_new_pie_menu_icon_and_parent_name_for_type(affordance, resolver)
            if new_icon is not None:
                if icon is not None and icon is not new_icon:
                    logger.error('different valid pie menu icons specified in {}', self._owner, owner='nabaker')
                else:
                    icon = new_icon
                    if icon_tag is None:
                        icon_tag = new_tag
                    else:
                        icon_tag &= new_tag
            if new_parent is not None:
                if parent is not None and parent is not new_parent:
                    logger.error('different valid pie menu parent name specified in {}', self._owner, owner='nabaker')
                else:
                    parent = new_parent
                    if parent_tag is None:
                        parent_tag = new_tag
                    else:
                        parent_tag &= parent_tag
        return (icon, parent, icon_tag, parent_tag)

    def get_affordance_basic_extras_reversed_gen(self, affordance, resolver):
        for modifier in self._affordance_modifiers:
            yield from reversed(modifier.get_basic_extras_for_type(affordance, resolver))

    def get_effective_skill_modifier(self, skill):
        return sum(modifier.get_modifier_value(skill) for modifier in self._effective_skill_modifiers)

    def get_mood_category_weight_mapping(self):
        mood_modifier_map = {}
        for modifier in self._mood_effect_modifiers:
            for (mood, value) in modifier.mood_effect_mapping.items():
                total_modifier = mood_modifier_map.get(mood, 1)*value
                mood_modifier_map[mood] = total_modifier
        return mood_modifier_map
