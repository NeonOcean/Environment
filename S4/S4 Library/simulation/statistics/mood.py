from buffs import BuffPolarity
from buffs.tunable import TunableBuffReference
from sims import sim_info_types
from sims4.localization import TunableLocalizedString
from sims4.resources import Types
from sims4.tuning.geometric import TunableVector3
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import Tunable, TunableMapping, TunableReference, TunableTuple, TunableList, OptionalTunable, HasTunableReference, AutoFactoryInit, HasTunableSingletonFactory, TunableResourceKey, TunableEnumEntry, TunableColor, TunableRange
from sims4.tuning.tunable_base import SourceQueries, ExportModes, GroupNames
from sims4.utils import classproperty
from statistics.base_statistic import logger
from statistics.commodity import Commodity
from vfx import PlayEffect
import services
import sims4

class TunableModifiers(TunableTuple):

    def __init__(self, **kwargs):
        super().__init__(add_modifier=Tunable(description='\n                The modifier to add to a value\n                ', tunable_type=float, default=0), multiply_modifier=Tunable(description='\n                The modifier to multiply a value by\n                ', tunable_type=float, default=1))

class TunableEnvironmentScoreModifiers(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'mood_modifiers': TunableMapping(description='\n                Modifiers to apply to a given Mood for the environment scoring of an object.\n                ', key_type=TunableReference(description='\n                    The Mood we want to modify for objects in question.\n                    ', manager=services.get_instance_manager(sims4.resources.Types.MOOD)), value_type=TunableModifiers(description="\n                    Modifiers to apply to an object's environment score\n                    "), key_name='mood', value_name='modifiers'), 'negative_modifiers': OptionalTunable(description="\n                Modifiers for an object's negative environment score\n                ", tunable=TunableModifiers(), enabled_by_default=False), 'positive_modifiers': OptionalTunable(description="\n                Modifiers for an object's positive environment score\n                ", tunable=TunableModifiers(), enabled_by_default=False)}
    DEFAULT_MODIFIERS = (0, 1)

    def combine_modifiers(self, object_mood_modifiers, object_negative_modifiers, object_positive_modifiers):
        new_mood_modifiers = {}
        new_negative_modifiers = object_negative_modifiers
        new_positive_modifiers = object_positive_modifiers
        for (mood, modifiers) in object_mood_modifiers.items():
            new_mood_modifiers[mood] = modifiers
        for (mood, modifiers) in self.mood_modifiers.items():
            old_modifiers = new_mood_modifiers.get(mood, (0, 1))
            new_mood_modifiers[mood] = (old_modifiers[0] + modifiers.add_modifier, old_modifiers[1]*modifiers.multiply_modifier)
        new_modifiers = self.get_negative_modifiers()
        new_negative_modifiers = (new_negative_modifiers[0] + new_modifiers[0], new_negative_modifiers[1]*new_modifiers[1])
        new_modifiers = self.get_positive_modifiers()
        new_positive_modifiers = (new_positive_modifiers[0] + new_modifiers[0], new_positive_modifiers[1]*new_modifiers[1])
        return (new_mood_modifiers, new_negative_modifiers, new_positive_modifiers)

    def get_mood_modifiers(self, mood):
        mood_mods = self.mood_modifiers.get(mood)
        if mood_mods is not None:
            return (mood_mods.add_modifier, mood_mods.multiply_modifier)
        return self.DEFAULT_MODIFIERS

    def get_negative_modifiers(self):
        if self.negative_modifiers is not None:
            return (self.negative_modifiers.add_modifier, self.negative_modifiers.multiply_modifier)
        return self.DEFAULT_MODIFIERS

    def get_positive_modifiers(self):
        if self.positive_modifiers is not None:
            return (self.positive_modifiers.add_modifier, self.positive_modifiers.multiply_modifier)
        return self.DEFAULT_MODIFIERS

class TunableMoodDescriptionTraitOverride(TunableTuple):

    def __init__(self, **kwargs):
        super().__init__(trait=TunableReference(manager=services.get_instance_manager(sims4.resources.Types.TRAIT), allow_none=True), descriptions=TunableList(description='\n                Description for the UI tooltip, per intensity.\n                ', tunable=TunableLocalizedString()), **kwargs)

class Mood(HasTunableReference, metaclass=HashedTunedInstanceMetaclass, manager=services.mood_manager()):
    INSTANCE_TUNABLES = {'mood_asm_param': OptionalTunable(description='\n            If set, then this mood will specify an asm parameter to affect\n            animations. If not set, then the ASM parameter will be determined by\n            the second most prevalent mood.\n            ', tunable=Tunable(description="\n                The ASM parameter for Sim's mood, if not set, will use 'xxx'\n                from instance name pattern with 'mood_xxx'.\n                ", tunable_type=str, default='', source_query=SourceQueries.SwingEnumNamePattern.format('mood')), enabled_name='Specify', disabled_name='Determined_By_Other_Moods'), 'intensity_thresholds': TunableList(description='\n            List of thresholds at which the intensity of this mood levels up.\n            If empty, this mood has a single threshold and all mood tuning lists should\n            have a single item in them.\n            For each threshold added, you may add a new item to the Buffs, Mood Names,\n            Portrait Pose Indexes and Portrait Frames lists.\n            ', tunable=int), 'buffs': TunableList(description='\n            A list of buffs that will be added while this mood is the active mood\n            on a Sim. \n            The first item is applied for the initial intensity, and each\n            subsequent item replaces the previous buff as the intensity levels up.\n            ', tunable=TunableBuffReference(reload_dependent=True, allow_none=True)), 'mood_names': TunableList(description='\n            A list of localized names of this mood.\n            The first item is applied for the initial intensity, and each\n            subsequent item replaces the name as the intensity levels up.\n            ', tunable=TunableLocalizedString(), export_modes=(ExportModes.ServerXML, ExportModes.ClientBinary)), 'portrait_pose_indexes': TunableList(description='\n            A list of the indexes of the pose passed to thumbnail generation on the\n            client to pose the Sim portrait when they have this mood.\n            You can find the list of poses in tuning\n            (Client_ThumnailPoses)\n            The first item is applied for the initial intensity, and each\n            subsequent item replaces the pose as the intensity levels up.\n            ', tunable=Tunable(tunable_type=int, default=0), export_modes=(ExportModes.ClientBinary,)), 'portrait_frames': TunableList(description='\n            A list of the frame labels (NOT numbers!) from the UI .fla file that the\n            portrait should be set to when this mood is active. Determines\n            background color, font color, etc.\n            The first item is applied for the initial intensity, and each\n            subsequent item replaces the pose as the intensity levels up.\n            ', tunable=Tunable(tunable_type=str, default=''), export_modes=(ExportModes.ClientBinary,)), 'environment_scoring_commodity': Commodity.TunableReference(description="\n            Defines the ranges and corresponding buffs to apply for this\n            mood's environmental contribution.\n            \n            Be sure to tune min, max, and the different states. The\n            convergence value is what will remove the buff. Suggested to be\n            0.\n            "), 'descriptions': TunableList(description='\n            Description for the UI tooltip, per intensity.\n            ', tunable=TunableLocalizedString(), export_modes=(ExportModes.ClientBinary,)), 'icons': TunableList(description='\n            Icon for the UI tooltip, per intensity.\n            ', tunable=TunableResourceKey(None, resource_types=sims4.resources.CompoundTypes.IMAGE), export_modes=(ExportModes.ClientBinary,)), 'descriptions_age_override': TunableMapping(description='\n            Mapping of age to descriptions text for mood.  If age does not\n            exist in mapping will use default description text.\n            ', key_type=TunableEnumEntry(sim_info_types.Age, sim_info_types.Age.CHILD), value_type=TunableList(description='\n                Description for the UI tooltip, per intensity.\n                ', tunable=TunableLocalizedString()), key_name='Age', value_name='description_text', tuple_name='DescriptionsAgeOverrideMappingTuple', export_modes=(ExportModes.ClientBinary,)), 'descriptions_trait_override': TunableMoodDescriptionTraitOverride(description='\n            Trait override for mood descriptions.  If a Sim has this trait\n            and there is not a valid age override for the Sim, this\n            description text will be used.\n            ', export_modes=(ExportModes.ClientBinary,)), 'audio_stings_on_add': TunableList(description="\n            The audio to play when a mood or it's intensity changes. Tune one\n            for each intensity on the mood\n            ", tunable=TunableResourceKey(description='\n                The sound to play.\n                ', default=None, resource_types=(sims4.resources.Types.PROPX,), export_modes=ExportModes.ClientBinary)), 'mood_colors': TunableList(description='\n            A list of the colors displayed on the steel series mouse when the\n            active Sim has this mood.  The first item is applied for the\n            initial intensity, and each  subsequent item replaces the color as\n            the intensity levels up.\n            ', tunable=TunableVector3(description='\n                Color.\n                ', default=sims4.math.Vector3.ZERO(), export_modes=ExportModes.ClientBinary)), 'mood_frequencies': TunableList(description='\n            A list of the flash frequencies on the steel series mouse when the\n            active Sim has this mood.   The first item is applied for the\n            initial intensity, and each  subsequent item replaces the value as\n            the intensity levels up.  0 => solid color, otherwise, value =>\n            value hertz.\n            ', tunable=Tunable(tunable_type=float, default=0.0, description='\n                Hertz.\n                ', export_modes=ExportModes.ClientBinary)), 'buff_polarity': TunableEnumEntry(description='\n            Setting the polarity will determine how up/down arrows\n            appear for any buff that provides this mood.\n            ', tunable_type=BuffPolarity, default=BuffPolarity.NEUTRAL, tuning_group=GroupNames.UI, export_modes=ExportModes.All), 'is_changeable': Tunable(description='\n            If this is checked, any buff with this mood will change to\n            the highest current mood of the same polarity.  If there is no mood\n            with the same polarity it will default to use this mood type\n            ', tunable_type=bool, default=False), 'base_color': TunableColor.TunableColorRGBA(description='\n            The base color for the ghost shader.\n            ', tuning_group=GroupNames.GHOSTS, export_modes=ExportModes.ClientBinary), 'edge_color': TunableColor.TunableColorRGBA(description='\n            The edge color for the ghost shader.\n            ', tuning_group=GroupNames.GHOSTS, export_modes=ExportModes.ClientBinary), 'noise_texture': TunableResourceKey(description='\n            Optional texture used to apply noise effects to the ghost.\n            ', resource_types=(Types.DDS,), default=None, allow_none=True, tuning_group=GroupNames.GHOSTS, export_modes=ExportModes.ClientBinary), 'filter_param_desaturation': TunableRange(description='\n            0 - 1. Controls the amount of color retained by objects behind the ghost.\n            0 = all color retained, 1 = no color retained.\n            ', tunable_type=float, default=0.0, minimum=0.0, maximum=1.0, tuning_group=GroupNames.GHOSTS, export_modes=ExportModes.ClientBinary), 'filter_param_opacity_offset': Tunable(description="\n            Controls the ghost's opacity.  Higher value = more opacity.\n            ", tunable_type=float, default=0.0, tuning_group=GroupNames.GHOSTS, export_modes=ExportModes.ClientBinary), 'filter_param_lens_distortion': Tunable(description='\n            Controls lens distortion effect on the ghost.\n            0 = no effect, higher value = more distortion\n            ', tunable_type=float, default=0.0, tuning_group=GroupNames.GHOSTS, export_modes=ExportModes.ClientBinary), 'filter_param_noise_distortion': Tunable(description='\n            Controls the amount of distortion obtained from the noise texture.\n            0 = no effect, Higher value = more distortion\n            ', tunable_type=float, default=0.0, tuning_group=GroupNames.GHOSTS, export_modes=ExportModes.ClientBinary), 'filter_param_noise_scale_x': Tunable(description='\n            Scales the input from the noise texture horizontally.\n            ', tunable_type=float, default=1.0, tuning_group=GroupNames.GHOSTS, export_modes=ExportModes.ClientBinary), 'filter_param_noise_scale_y': Tunable(description='\n            Scales the input from the noise texture vertically.\n            ', tunable_type=float, default=1.0, tuning_group=GroupNames.GHOSTS, export_modes=ExportModes.ClientBinary), 'filter_param_noise_scroll_y': Tunable(description='\n            Controls the rate at which the input from the noise texture scrolls vertically.\n            0 = no scrolling, Negative value = scrolls up, Positive value = scrolls down.\n            ', tunable_type=float, default=0.0, tuning_group=GroupNames.GHOSTS, export_modes=ExportModes.ClientBinary), 'filter_param_noise_jumpiness': Tunable(description='\n            Controls the rate at which the input from the noise texture jumps around at random.\n            0 = no jumpiness, Higher value = more jumpiness\n            ', tunable_type=float, default=0.0, tuning_group=GroupNames.GHOSTS, export_modes=ExportModes.ClientBinary), 'whim_set': OptionalTunable(description='\n            If enabled then this mood will offer a whim set to the Sim when it\n            is active.\n            ', tunable=TunableReference(description='\n                A whim set that is active when this mood is active.\n                ', manager=services.get_instance_manager(sims4.resources.Types.ASPIRATION), class_restrictions=('ObjectivelessWhimSet',))), 'thumbnail_vfx_list': TunableList(description='\n            List of effects that will be rendered for a Robot Sims thumbnail\n            for this mood.\n            ', tunable=TunableTuple(description='\n                The name of the effect to play and the joint name it should be\n                attached to.\n                ', effect_name=Tunable(description='\n                    The name of the effect to play.\n                    ', tunable_type=str, default=''), joint_name=Tunable(description='\n                    The joint name this effect is attached to.\n                    ', tunable_type=str, default=''), export_class_name='MoodVFXInfoTuple'), tuning_group=GroupNames.ROBOTS, export_modes=ExportModes.ClientBinary)}
    _asm_param_name = None
    excluding_traits = None

    @classmethod
    def _tuning_loaded_callback(cls):
        cls._asm_param_name = cls.mood_asm_param
        if cls._asm_param_name is not None:
            if not cls._asm_param_name:
                name_list = cls.__name__.split('_', 1)
                if len(name_list) <= 1:
                    logger.error("Mood {} has an invalid name for asm parameter, please either set 'mood_asm_param' or change the tuning file name to match the format 'mood_xxx'.", cls.__name__)
                cls._asm_param_name = name_list[1]
            cls._asm_param_name = cls._asm_param_name.lower()
        for buff_ref in cls.buffs:
            my_buff = buff_ref.buff_type
            if my_buff is not None:
                if my_buff.mood_type is not None:
                    logger.error('Mood {} will apply a buff ({}) that affects mood. This can cause mood calculation errors. Please select a different buff or remove the mood change.', cls.__name__, my_buff.mood_type.__name__)
                my_buff.is_mood_buff = True
        prev_threshold = 0
        for threshold in cls.intensity_thresholds:
            if threshold <= prev_threshold:
                logger.error('Mood {} has Intensity Thresholds in non-ascending order.')
                break
            prev_threshold = threshold

    @classmethod
    def _verify_tuning_callback(cls):
        num_thresholds = len(cls.intensity_thresholds) + 1
        if len(cls.buffs) != num_thresholds:
            logger.error('Mood {} does not have the correct number of Buffs tuned. It has {} thresholds, but {} buffs.', cls.__name__, num_thresholds, len(cls.buffs))
        if len(cls.mood_names) != num_thresholds:
            logger.error('Mood {} does not have the correct number of Mood Names tuned. It has {} thresholds, but {} names.', cls.__name__, num_thresholds, len(cls.mood_names))
        if len(cls.portrait_pose_indexes) != num_thresholds:
            logger.error('Mood {} does not have the correct number of Portrait Pose Indexes tuned. It has {} thresholds, but {} poses.', cls.__name__, num_thresholds, len(cls.portrait_pose_indexes))
        if len(cls.portrait_frames) != num_thresholds:
            logger.error('Mood {} does not have the correct number of Portrait Frames tuned. It has {} thresholds, but {} frames.', cls.__name__, num_thresholds, len(cls.portrait_frames))
        for (age, descriptions) in cls.descriptions_age_override.items():
            if len(descriptions) != num_thresholds:
                logger.error('Mood {} does not have the correct number of descriptions age override tuned. For age:({}) It has {} thresholds, but {} descriptions.', cls.__name__, age, num_thresholds, len(descriptions))
        if cls.descriptions_trait_override.trait is not None and len(cls.descriptions_trait_override.descriptions) != num_thresholds:
            logger.error('Mood {} does not have the correct number of trait override descriptions tuned. For trait:({}) It has {} thresholds, but {} descriptions.', cls.__name__, cls.descriptions_trait_override.trait.__name__, num_thresholds, len(cls.descriptions_trait_override.descriptions))

    @classproperty
    def asm_param_name(cls):
        return cls._asm_param_name
