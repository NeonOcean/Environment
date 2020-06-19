from _sims4_collections import frozendict
from autonomy.content_sets import ContentSet
from buffs.tunable import TunableBuffReference
from objects.mixins import SuperAffordanceProviderMixin, MixerActorMixin, MixerProviderMixin
from objects.mixins import TargetSuperAffordanceProviderMixin
from sims import sim_info_types
from sims.culling.culling_tuning import CullingBehaviorDefault, CullingBehaviorImmune, CullingBehaviorImportanceAsNpc
from sims.lod_mixin import HasTunableLodMixin
from sims.outfits.outfit_enums import OutfitChangeReason
from sims.sim_info_types import Species, Age, Gender
from sims4.localization import TunableLocalizedString, TunableLocalizedStringFactory
from sims4.resources import CompoundTypes
from sims4.tuning.dynamic_enum import DynamicEnum
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import TunableResourceKey, OptionalTunable, TunableReference, TunableList, TunableEnumEntry, TunableSet, TunableMapping, Tunable, HasTunableReference, TunableTuple, TunableEnumFlags, TunableEnumWithFilter, TunableVariant, TunableInteractionAsmResourceKey
from sims4.tuning.tunable_base import ExportModes, SourceQueries, GroupNames
from sims4.utils import classproperty
from statistics.commodity import Commodity
from sims.fixup.sim_info_career_fixup_action import _SimInfoCareerFixupAction
from sims.fixup.sim_info_fixup_action import SimInfoFixupActionTiming
from sims.fixup.sim_info_perk_fixup_action import _SimInfoPerkFixupAction
from sims.fixup.sim_info_skill_fixup_action import _SimInfoSkillFixupAction
from sims.fixup.sim_info_unlock_fixup_action import _SimInfoUnlockFixupAction
from traits.trait_day_night_tracking import DayNightTracking
from traits.trait_plumbbob_override import PlumbbobOverrideRequest
from traits.trait_type import TraitType
from traits.trait_voice_effect import VoiceEffectRequest
from vfx.vfx_mask import VFXMask
import services
import sims4.log
import tag
logger = sims4.log.Logger('Trait', default_owner='cjiang')

def are_traits_conflicting(trait_a, trait_b):
    if trait_a is None or trait_b is None:
        return False
    return trait_a.is_conflicting(trait_b)

def get_possible_traits(sim_info_data, trait_type=TraitType.PERSONALITY):
    trait_manager = services.get_instance_manager(sims4.resources.Types.TRAIT)
    return [trait for trait in trait_manager.types.values() if trait.trait_type == trait_type if trait.is_valid_trait(sim_info_data)]

class TraitBuffReplacementPriority(DynamicEnum):
    NORMAL = 0

class TraitUICategory(DynamicEnum):
    PERSONALITY = 0
    GENDER = 1

class Trait(HasTunableReference, SuperAffordanceProviderMixin, TargetSuperAffordanceProviderMixin, HasTunableLodMixin, MixerActorMixin, MixerProviderMixin, metaclass=HashedTunedInstanceMetaclass, manager=services.trait_manager()):
    EQUIP_SLOT_NUMBER_MAP = TunableMapping(description='\n        The number of personality traits available to Sims of specific ages.\n        ', key_type=TunableEnumEntry(description="\n            The Sim's age.\n            ", tunable_type=sim_info_types.Age, default=sim_info_types.Age.YOUNGADULT), value_type=Tunable(description='\n            The number of personality traits available to a Sim of the specified\n            age.\n            ', tunable_type=int, default=3), key_name='Age', value_name='Slot Number')
    PERSONALITY_TRAIT_TAG = TunableEnumEntry(description='\n        The tag that marks a trait as a personality trait.\n        ', tunable_type=tag.Tag, default=tag.Tag.INVALID, invalid_enums=(tag.Tag.INVALID,))
    DAY_NIGHT_TRACKING_BUFF_TAG = TunableEnumWithFilter(description='\n        The tag that marks buffs as opting in to Day Night Tracking on traits..\n        ', tunable_type=tag.Tag, filter_prefixes=['buff'], default=tag.Tag.INVALID, invalid_enums=(tag.Tag.INVALID,))
    INSTANCE_TUNABLES = {'trait_type': TunableEnumEntry(description='\n            The type of the trait.\n            ', tunable_type=TraitType, default=TraitType.PERSONALITY, export_modes=ExportModes.All, tuning_group=GroupNames.APPEARANCE), 'display_name': TunableLocalizedStringFactory(description="\n            The trait's display name. This string is provided with the owning\n            Sim as its only token.\n            ", allow_none=True, export_modes=ExportModes.All, tuning_group=GroupNames.APPEARANCE), 'display_name_gender_neutral': TunableLocalizedString(description="\n            The trait's gender-neutral display name. This string is not provided\n            any tokens, and thus can't rely on context to properly form\n            masculine and feminine forms.\n            ", allow_none=True, tuning_group=GroupNames.APPEARANCE), 'trait_description': TunableLocalizedStringFactory(description="\n            The trait's description.\n            ", allow_none=True, export_modes=ExportModes.All, tuning_group=GroupNames.APPEARANCE), 'trait_origin_description': TunableLocalizedString(description="\n            A description of how the Sim obtained this trait. Can be overloaded\n            for other uses in certain cases:\n            - When the trait type is AGENT this string is the name of the \n                agency's Trade type and will be provided with the owning sim \n                as its token.\n            - When the trait type is HIDDEN and the trait is used by the CAS\n                STORIES flow, this can be used as a secondary description in \n                the CAS Stories UI. If this trait is tagged as a CAREER CAS \n                stories trait, this description will be used to explain which \n                skills are also granted with this career.\n            ", allow_none=True, export_modes=ExportModes.All, tuning_group=GroupNames.APPEARANCE), 'icon': TunableResourceKey(description="\n            The trait's icon.\n            ", allow_none=True, resource_types=CompoundTypes.IMAGE, export_modes=ExportModes.All, tuning_group=GroupNames.APPEARANCE), 'pie_menu_icon': TunableResourceKey(description="\n            The trait's pie menu icon.\n            ", resource_types=CompoundTypes.IMAGE, default=None, allow_none=True, tuning_group=GroupNames.APPEARANCE), 'trait_asm_overrides': TunableTuple(description='\n            Tunables that will specify if a Trait will add any parameters\n            to the Sim and how it will affect their boundary conditions.\n            ', param_type=OptionalTunable(description='\n                Define if this trait is parameterized as an on/off value or as\n                part of an enumeration.\n                ', tunable=Tunable(description='\n                    The name of the parameter enumeration. For example, if this\n                    value is tailType, then the tailType actor parameter is set\n                    to the value specified in param_value, for this Sim.\n                    ', tunable_type=str, default=None), disabled_name='boolean', enabled_name='enum'), trait_asm_param=Tunable(description="\n                The ASM parameter for this trait. If unset, it will be auto-\n                generated depending on the instance name (e.g. 'trait_Clumsy').\n                ", tunable_type=str, default=None), consider_for_boundary_conditions=Tunable(description='\n                If enabled the trait_asm_param will be considered when a Sim\n                is building the goals and validating against its boundary\n                conditions.\n                This should ONLY be enabled, if we need this parameter for\n                cases like a posture transition, or boundary specific cases. \n                On regular cases like an animation outcome, this is not needed.\n                i.e. Vampire trait has an isVampire parameter set to True, so\n                when animatin out of the coffin it does different get in/out \n                animations.  When this is enabled, isVampire will be set to \n                False for every other Sim.\n                ', tunable_type=bool, default=False), tuning_group=GroupNames.ANIMATION), 'ages': TunableSet(description='\n            The allowed ages for this trait. If no ages are specified, then all\n            ages are considered valid.\n            ', tunable=TunableEnumEntry(tunable_type=Age, default=None, export_modes=ExportModes.All), tuning_group=GroupNames.AVAILABILITY), 'genders': TunableSet(description='\n            The allowed genders for this trait. If no genders are specified,\n            then all genders are considered valid.\n            ', tunable=TunableEnumEntry(tunable_type=Gender, default=None, export_modes=ExportModes.All), tuning_group=GroupNames.AVAILABILITY), 'species': TunableSet(description='\n            The allowed species for this trait. If not species are specified,\n            then all species are considered valid.\n            ', tunable=TunableEnumEntry(tunable_type=Species, default=Species.HUMAN, invalid_enums=(Species.INVALID,), export_modes=ExportModes.All), tuning_group=GroupNames.AVAILABILITY), 'conflicting_traits': TunableList(description='\n            Conflicting traits for this trait. If the Sim has any of the\n            specified traits, then they are not allowed to be equipped with this\n            one.\n            \n            e.g.\n             Family Oriented conflicts with Hates Children, and vice-versa.\n            ', tunable=TunableReference(manager=services.trait_manager(), pack_safe=True), export_modes=ExportModes.All, tuning_group=GroupNames.AVAILABILITY), 'is_npc_only': Tunable(description='\n            If checked, this trait will get removed from Sims that have a home\n            when the zone is loaded or whenever they switch to a household that\n            has a home zone.\n            ', tunable_type=bool, default=False, tuning_group=GroupNames.AVAILABILITY), 'cas_selected_icon': TunableResourceKey(description='\n            Icon to be displayed in CAS when this trait has already been applied\n            to a Sim.\n            ', resource_types=CompoundTypes.IMAGE, default=None, allow_none=True, export_modes=(ExportModes.ClientBinary,), tuning_group=GroupNames.CAS), 'cas_idle_asm_key': TunableInteractionAsmResourceKey(description='\n            The ASM to use for the CAS idle.\n            ', default=None, allow_none=True, category='asm', export_modes=ExportModes.All, tuning_group=GroupNames.CAS), 'cas_idle_asm_state': Tunable(description='\n            The state to play for the CAS idle.\n            ', tunable_type=str, default=None, source_location='cas_idle_asm_key', source_query=SourceQueries.ASMState, export_modes=ExportModes.All, tuning_group=GroupNames.CAS), 'cas_trait_asm_param': Tunable(description='\n            The ASM parameter for this trait for use with CAS ASM state machine,\n            driven by selection of this Trait, i.e. when a player selects the a\n            romantic trait, the Flirty ASM is given to the state machine to\n            play. The name tuned here must match the animation state name\n            parameter expected in Swing.\n            ', tunable_type=str, default=None, export_modes=ExportModes.All, tuning_group=GroupNames.CAS), 'tags': TunableList(description="\n            The associated categories of the trait. Need to distinguish among\n            'Personality Traits', 'Achievement Traits' and 'Walkstyle\n            Traits'.\n            ", tunable=TunableEnumEntry(tunable_type=tag.Tag, default=tag.Tag.INVALID), export_modes=ExportModes.All, tuning_group=GroupNames.CAS), 'sim_info_fixup_actions': TunableList(description='\n            A list of fixup actions which will be performed on a sim_info with\n            this trait when it is loaded.\n            ', tunable=TunableVariant(career_fixup_action=_SimInfoCareerFixupAction.TunableFactory(description='\n                    A fix up action to set a career with a specific level.\n                    '), skill_fixup_action=_SimInfoSkillFixupAction.TunableFactory(description='\n                    A fix up action to set a skill with a specific level.\n                    '), unlock_fixup_action=_SimInfoUnlockFixupAction.TunableFactory(description='\n                    A fix up action to unlock certain things for a Sim\n                    '), perk_fixup_action=_SimInfoPerkFixupAction.TunableFactory(description='\n                    A fix up action to grant perks to a Sim. It checks perk required\n                    unlock tuning and unlocks prerequisite perks first.\n                    '), default='career_fixup_action'), tuning_group=GroupNames.CAS), 'sim_info_fixup_actions_timing': TunableEnumEntry(description="\n            This is DEPRECATED, don't tune this field. We usually don't do trait-based\n            fixup unless it's related to CAS stories. We keep this field only for legacy\n            support reason.\n            \n            This is mostly to optimize performance when applying fix-ups to\n            a Sim.  We ideally would not like to spend time scanning every Sim \n            on every load to see if they need fixups.  Please be sure you \n            consult a GPE whenever you are creating fixup tuning.\n            ", tunable_type=SimInfoFixupActionTiming, default=SimInfoFixupActionTiming.ON_FIRST_SIMINFO_LOAD, tuning_group=GroupNames.DEPRECATED, deprecated=True), 'teleport_style_interaction_to_inject': TunableReference(description='\n             When this trait is added to a Sim, if a teleport style interaction\n             is specified, any time another interaction runs, we may run this\n             teleport style interaction to shorten or replace the route to the \n             target.\n             ', manager=services.get_instance_manager(sims4.resources.Types.INTERACTION), class_restrictions=('TeleportStyleSuperInteraction',), allow_none=True, tuning_group=GroupNames.SPECIAL_CASES), 'interactions': OptionalTunable(description='\n            Mixer interactions that are available to Sims equipped with this\n            trait.\n            ', tunable=ContentSet.TunableFactory(locked_args={'phase_affordances': frozendict(), 'phase_tuning': None})), 'buffs_add_on_spawn_only': Tunable(description='\n            If unchecked, buffs are added to the Sim as soon as this trait is\n            added. If checked, buffs will be added only when the Sim is\n            instantiated and removed when the Sim uninstantiates.\n            \n            General guidelines: If the buffs only matter to Sims, for example\n            buffs that alter autonomy behavior or walkstyle, this should be\n            checked.\n            ', tunable_type=bool, default=True), 'buffs': TunableList(description='\n            Buffs that should be added to the Sim whenever this trait is\n            equipped.\n            ', tunable=TunableBuffReference(pack_safe=True), unique_entries=True), 'buffs_proximity': TunableList(description='\n            Proximity buffs that are active when this trait is equipped.\n            ', tunable=TunableReference(manager=services.buff_manager())), 'buff_replacements': TunableMapping(description='\n            A mapping of buff replacement. If Sim has this trait on, whenever he\n            get the buff tuned in the key of the mapping, it will get replaced\n            by the value of the mapping.\n            ', key_type=TunableReference(description='\n                Buff that will get replaced to apply on Sim by this trait.\n                ', manager=services.buff_manager(), reload_dependent=True, pack_safe=True), value_type=TunableTuple(description='\n                Data specific to this buff replacement.\n                ', buff_type=TunableReference(description='\n                    Buff used to replace the buff tuned as key.\n                    ', manager=services.buff_manager(), reload_dependent=True, pack_safe=True), buff_reason=OptionalTunable(description='\n                    If enabled, override the buff reason.\n                    ', tunable=TunableLocalizedString(description='\n                        The overridden buff reason.\n                        ')), buff_replacement_priority=TunableEnumEntry(description="\n                    The priority of this buff replacement, relative to other\n                    replacements. Tune this to be a higher value if you want\n                    this replacement to take precedence.\n                    \n                    e.g.\n                     (NORMAL) trait_HatesChildren (buff_FirstTrimester -> \n                                                   buff_FirstTrimester_HatesChildren)\n                     (HIGH)   trait_Male (buff_FirstTrimester -> \n                                          buff_FirstTrimester_Male)\n                                          \n                     In this case, both traits have overrides on the pregnancy\n                     buffs. However, we don't want males impregnated by aliens\n                     that happen to hate children to lose their alien-specific\n                     buffs. Therefore we tune the male replacement at a higher\n                     priority.\n                    ", tunable_type=TraitBuffReplacementPriority, default=TraitBuffReplacementPriority.NORMAL))), 'excluded_mood_types': TunableList(TunableReference(description='\n            List of moods that are prevented by having this trait.\n            ', manager=services.mood_manager())), 'outfit_replacements': TunableMapping(description="\n            A mapping of outfit replacements. If the Sim has this trait, outfit\n            change requests are intercepted to produce the tuned result. If\n            multiple traits with outfit replacements exist, the behavior is\n            undefined.\n            \n            Tuning 'Invalid' as a key acts as a fallback and applies to all\n            reasons.\n            \n            Tuning 'Invalid' as a value keeps a Sim in their current outfit.\n            ", key_type=TunableEnumEntry(tunable_type=OutfitChangeReason, default=OutfitChangeReason.Invalid), value_type=TunableEnumEntry(tunable_type=OutfitChangeReason, default=OutfitChangeReason.Invalid)), 'disable_aging': OptionalTunable(description='\n            If enabled, aging out of specific ages can be disabled.\n            ', tunable=TunableTuple(description='\n                The tuning that disables aging out of specific age groups.\n                ', allowed_ages=TunableSet(description='\n                    A list of ages that the Sim CAN age out of. If an age is in\n                    this list then the Sim is allowed to age out of it. If an\n                    age is not in this list than a Sim is not allowed to age out\n                    of it. For example, if the list only contains Child and\n                    Teen, then a Child Sim would be able to age up to Teen and\n                    a Teen Sim would be able to age up to Young Adult. But, a\n                    Young Adult, Adult, or Elder Sim would not be able to age\n                    up.\n                    ', tunable=TunableEnumEntry(Age, default=Age.ADULT)), tooltip=OptionalTunable(description='\n                    When enabled, this tooltip will be displayed in the aging\n                    progress bar when aging is disabled because of the trait.\n                    ', tunable=TunableLocalizedStringFactory(description='\n                        The string that displays in the aging UI when aging up\n                        is disabled due to the trait.\n                        '))), tuning_group=GroupNames.SPECIAL_CASES), 'can_die': Tunable(description='\n            When set, Sims with this trait are allowed to die. When unset, Sims\n            are prevented from dying.\n            ', tunable_type=bool, default=True, tuning_group=GroupNames.SPECIAL_CASES), 'culling_behavior': TunableVariant(description='\n            The culling behavior of a Sim with this trait.\n            ', default_behavior=CullingBehaviorDefault.TunableFactory(), immune_to_culling=CullingBehaviorImmune.TunableFactory(), importance_as_npc_score=CullingBehaviorImportanceAsNpc.TunableFactory(), default='default_behavior', tuning_group=GroupNames.SPECIAL_CASES), 'always_send_test_event_on_add': Tunable(description='\n            If checked, will send out a test event when added to a trait\n            tracker even if the receiving sim is hidden or not instanced.\n            ', tunable_type=bool, default=False, tuning_group=GroupNames.SPECIAL_CASES), 'voice_effect': OptionalTunable(description='\n            The voice effect of a Sim with this trait. This is prioritized\n            against other traits with voice effects.\n            \n            The Sim may only have one voice effect at a time.\n            ', tunable=VoiceEffectRequest.TunableFactory()), 'plumbbob_override': OptionalTunable(description='\n            If enabled, allows a new plumbbob model to be used when a Sim has\n            this occult type.\n            ', tunable=PlumbbobOverrideRequest.TunableFactory()), 'vfx_mask': OptionalTunable(description='\n            If enabled when this trait is added the masks will be applied to\n            the Sim affecting the visibility of specific VFX.\n            Example: TRAIT_CHILDREN will provide a mask MASK_CHILDREN which \n            the monster battle object will only display VFX for any Sim \n            using that mask.\n            ', tunable=TunableEnumFlags(description="\n                Mask that will be added to the Sim's mask when the trait is\n                added.\n                ", enum_type=VFXMask), enabled_name='apply_vfx_mask', disabled_name='no_vfx_mask'), 'day_night_tracking': OptionalTunable(description="\n            If enabled, allows this trait to track various aspects of day and\n            night via buffs on the owning Sim.\n            \n            For example, if this is enabled and the Sunlight Buff is tuned with\n            buffs, the Sim will get the buffs added every time they're in\n            sunlight and removed when they're no longer in sunlight.\n            ", tunable=DayNightTracking.TunableFactory()), 'persistable': Tunable(description='\n            If checked then this trait will be saved onto the sim.  If\n            unchecked then the trait will not be saved.\n            Example unchecking:\n            Traits that are applied for the sim being in the region.\n            ', tunable_type=bool, default=True), 'initial_commodities': TunableSet(description='\n            A list of commodities that will be added to a sim on load, if the\n            sim has this trait.\n            \n            If a given commodity is also blacklisted by another trait that the\n            sim also has, it will NOT be added.\n            \n            Example:\n            Adult Age Trait adds Hunger.\n            Vampire Trait blacklists Hunger.\n            Hunger will not be added.\n            ', tunable=Commodity.TunableReference(pack_safe=True)), 'initial_commodities_blacklist': TunableSet(description="\n            A list of commodities that will be prevented from being\n            added to a sim that has this trait.\n            \n            This always takes priority over any commodities listed in any\n            trait's initial_commodities.\n            \n            Example:\n            Adult Age Trait adds Hunger.\n            Vampire Trait blacklists Hunger.\n            Hunger will not be added.\n            ", tunable=Commodity.TunableReference(pack_safe=True)), 'ui_commodity_sort_override': OptionalTunable(description='\n            Optional list of commodities to override the default UI sort order.\n            ', tunable=TunableList(description='\n                The position of the commodity in this list represents the sort order.\n                Add all possible combination of traits in the list.\n                If we have two traits which have sort override, we will implement\n                a priority system to determine which determines which trait sort\n                order to use.\n                ', tunable=Commodity.TunableReference())), 'ui_category': OptionalTunable(description='\n            If enabled then this trait will be displayed in a specific category\n            within the relationship panel if this trait would be displayed\n            within that panel.\n            ', tunable=TunableEnumEntry(description='\n                The UI trait category that we use to categorize this trait\n                within the relationship panel.\n                ', tunable_type=TraitUICategory, default=TraitUICategory.PERSONALITY), export_modes=ExportModes.All, enabled_name='ui_trait_category_tag'), 'loot_on_trait_add': OptionalTunable(description='\n            If tuned, this list of loots will be applied when trait is added in game.\n            ', tunable=TunableList(description='\n                List of loot to apply on the sim when this trait is added not\n                through CAS.\n                ', tunable=TunableReference(description='\n                    Loot to apply.\n                    ', manager=services.get_instance_manager(sims4.resources.Types.ACTION), pack_safe=True))), 'npc_leave_lot_interactions': OptionalTunable(description='\n            If enabled, allows tuning a set of Leave Lot and Leave Lot Must Run\n            interactions that this trait provides. NPC Sims with this trait will\n            use these interactions to leave the lot instead of the defaults.\n            ', tunable=TunableTuple(description='\n                Leave Lot Now and Leave Lot Now Must Run interactions.\n                ', leave_lot_now_interactions=TunableSet(TunableReference(description='\n                    If tuned, the Sim will consider these interaction when trying to run\n                    any "leave lot" situation.\n                    ', manager=services.get_instance_manager(sims4.resources.Types.INTERACTION), allow_none=False, pack_safe=True)), leave_lot_now_must_run_interactions=TunableSet(TunableReference(description='\n                    If tuned, the Sim will consider these interaction when trying to run\n                    any "leave lot must run" situation.\n                    ', manager=services.get_instance_manager(sims4.resources.Types.INTERACTION), allow_none=False, pack_safe=True)))), 'hide_relationships': Tunable(description='\n            If checked, then any relationships with a Sim who has this trait\n            will not be displayed in the UI. This is done by keeping the\n            relationship from having any tracks to actually track which keeps\n            it out of the UI.\n            ', tunable_type=bool, default=False, tuning_group=GroupNames.RELATIONSHIP), 'whim_set': OptionalTunable(description='\n            If enabled then this trait will offer a whim set to the Sim when it\n            is active.\n            ', tunable=TunableReference(description='\n                A whim set that is active when this trait is active.\n                ', manager=services.get_instance_manager(sims4.resources.Types.ASPIRATION), class_restrictions=('ObjectivelessWhimSet',))), 'allow_from_gallery': Tunable(description='\n            If checked, then this trait is allowed to be transferred over from\n            Sims downloaded from the gallery.\n            ', tunable_type=bool, default=True, tuning_group=GroupNames.SPECIAL_CASES)}
    _asm_param_name = None
    default_trait_params = set()

    def __repr__(self):
        return '<Trait:({})>'.format(self.__name__)

    def __str__(self):
        return '{}'.format(self.__name__)

    @classmethod
    def _tuning_loaded_callback(cls):
        cls._asm_param_name = cls.trait_asm_overrides.trait_asm_param
        if cls._asm_param_name is None:
            cls._asm_param_name = cls.__name__
        if cls.trait_asm_overrides.trait_asm_param is not None and cls.trait_asm_overrides.consider_for_boundary_conditions:
            cls.default_trait_params.add(cls.trait_asm_overrides.trait_asm_param)
        for (buff, replacement_buff) in cls.buff_replacements.items():
            if buff.trait_replacement_buffs is None:
                buff.trait_replacement_buffs = {}
            buff.trait_replacement_buffs[cls] = replacement_buff
        for mood in cls.excluded_mood_types:
            if mood.excluding_traits is None:
                mood.excluding_traits = []
            mood.excluding_traits.append(cls)

    @classmethod
    def _verify_tuning_callback(cls):
        if cls.display_name:
            if not cls.display_name_gender_neutral.hash:
                logger.error('Trait {} specifies a display name. It must also specify a gender-neutral display name. These must use different string keys.', cls, owner='BadTuning')
            if cls.display_name._string_id == cls.display_name_gender_neutral.hash:
                logger.error('Trait {} has the same string tuned for its display name and its gender-neutral display name. These must be different strings for localization.', cls, owner='BadTuning')
        if cls.day_night_tracking is not None:
            if not cls.day_night_tracking.sunlight_buffs and not (not cls.day_night_tracking.shade_buffs and not (not cls.day_night_tracking.day_buffs and not cls.day_night_tracking.night_buffs)):
                logger.error('Trait {} has Day Night Tracking enabled but no buffs are tuned. Either tune buffs or disable the tracking.', cls, owner='BadTuning')
            else:
                tracking_buff_tag = Trait.DAY_NIGHT_TRACKING_BUFF_TAG
                if any(buff for buff in cls.day_night_tracking.sunlight_buffs if not buff.buff_type.has_tag(tracking_buff_tag)) or (any(buff for buff in cls.day_night_tracking.shade_buffs if not buff.buff_type.has_tag(tracking_buff_tag)) or any(buff for buff in cls.day_night_tracking.day_buffs if not buff.buff_type.has_tag(tracking_buff_tag))) or any(buff for buff in cls.day_night_tracking.night_buffs if not buff.buff_type.has_tag(tracking_buff_tag)):
                    logger.error('Trait {} has Day Night tracking with an invalid\n                    buff. All buffs must be tagged with {} in order to be\n                    used as part of Day Night Tracking. Add these buffs with the\n                    understanding that, regardless of what system added them, they\n                    will always be on the Sim when the condition is met (i.e.\n                    Sunlight Buffs always added with sunlight is out) and they will\n                    always be removed when the condition is not met. Even if another\n                    system adds the buff, they will be removed if this trait is\n                    tuned to do that.\n                    ', cls, tracking_buff_tag)
        for buff_reference in cls.buffs:
            if buff_reference.buff_type.broadcaster is not None:
                logger.error('Trait {} has a buff {} with a broadcaster tuned that will never be removed. This is a potential performance hit, and a GPE should decide whether this is the best place for such.', cls, buff_reference, owner='rmccord')
        for commodity in cls.initial_commodities:
            if not commodity.persisted_tuning:
                logger.error('Trait {} has an initial commodity {} that does not have persisted tuning.', cls, commodity)

    @classproperty
    def is_personality_trait(cls):
        return cls.trait_type == TraitType.PERSONALITY

    @classproperty
    def is_aspiration_trait(cls):
        return cls.trait_type == TraitType.ASPIRATION

    @classproperty
    def is_gender_option_trait(cls):
        return cls.trait_type == TraitType.GENDER_OPTIONS

    @classproperty
    def is_ghost_trait(cls):
        return cls.trait_type == TraitType.GHOST

    @classproperty
    def is_robot_trait(cls):
        return cls.trait_type == TraitType.ROBOT

    @classmethod
    def is_valid_trait(cls, sim_info_data):
        if cls.ages and sim_info_data.age not in cls.ages:
            return False
        if cls.genders and sim_info_data.gender not in cls.genders:
            return False
        elif cls.species and sim_info_data.species not in cls.species:
            return False
        return True

    @classmethod
    def should_apply_fixup_actions(cls, fixup_source):
        if cls.sim_info_fixup_actions and cls.sim_info_fixup_actions_timing == fixup_source:
            if fixup_source != SimInfoFixupActionTiming.ON_FIRST_SIMINFO_LOAD:
                logger.warn('Trait {} has fixup actions not from CAS flow.This should only happen to old saves before EP08', cls, owner='yozhang')
            return True
        return False

    @classmethod
    def apply_fixup_actions(cls, sim_info):
        for fixup_action in cls.sim_info_fixup_actions:
            fixup_action(sim_info)

    @classmethod
    def can_age_up(cls, current_age):
        if not cls.disable_aging:
            return True
        return current_age in cls.disable_aging.allowed_ages

    @classmethod
    def is_conflicting(cls, trait):
        if trait is None:
            return False
        if cls.conflicting_traits and trait in cls.conflicting_traits:
            return True
        elif trait.conflicting_traits and cls in trait.conflicting_traits:
            return True
        return False

    @classmethod
    def get_outfit_change_reason(cls, outfit_change_reason):
        replaced_reason = cls.outfit_replacements.get(outfit_change_reason if outfit_change_reason is not None else OutfitChangeReason.Invalid)
        if replaced_reason is not None:
            return replaced_reason
        elif outfit_change_reason is not None:
            replaced_reason = cls.outfit_replacements.get(OutfitChangeReason.Invalid)
            if replaced_reason is not None:
                return replaced_reason
        return outfit_change_reason

    @classmethod
    def get_teleport_style_interaction_to_inject(cls):
        return cls.teleport_style_interaction_to_inject
