from _math import Vector3
from protocolbuffers import DistributorOps_pb2
from animation.object_animation import ObjectPose
from crafting.crafting_tunable import CraftingTuning
from crafting.photography_enums import PhotoStyleType, PhotoSize, PhotoOrientation, ZoomCapability, CameraQuality, CameraMode
from distributor.ops import GenericProtocolBufferOp
from distributor.rollback import ProtocolBufferRollback
from distributor.system import Distributor
from event_testing.resolver import SingleSimResolver, DoubleSimResolver
from interactions import ParticipantTypeSingle, ParticipantType
from interactions.utils.interaction_elements import XevtTriggeredElement
from interactions.utils.success_chance import SuccessChance
from objects import PaintingState
from objects.components.state import TunableStateValueReference
from objects.components.types import STORED_SIM_INFO_COMPONENT
from objects.system import create_object
from sims.sim_info_types import SpeciesExtended
from sims4.resources import get_protobuff_for_key
from sims4.tuning.tunable import TunableEnumEntry, Tunable, OptionalTunable, HasTunableSingletonFactory, AutoFactoryInit, TunableVariant, TunablePackSafeReference, TunableList, TunableMapping, TunableInterval, TunableReference, HasTunableFactory, TunableTuple
from statistics.skill import Skill
from tunable_multiplier import TunableStatisticModifierCurve
from ui.ui_dialog_notification import UiDialogNotification
import services
import sims4
import tag
logger = sims4.log.Logger('Photography')

class Photography:
    SMALL_PORTRAIT_OBJ_DEF = TunablePackSafeReference(description='\n        Object definition for a small portrait photo.\n        ', manager=services.definition_manager())
    SMALL_LANDSCAPE_OBJ_DEF = TunablePackSafeReference(description='\n        Object definition for a small landscape photo.\n        ', manager=services.definition_manager())
    MEDIUM_PORTRAIT_OBJ_DEF = TunablePackSafeReference(description='\n        Object definition for a medium portrait photo.\n        ', manager=services.definition_manager())
    MEDIUM_LANDSCAPE_OBJ_DEF = TunablePackSafeReference(description='\n        Object definition for a medium landscape photo.\n        ', manager=services.definition_manager())
    LARGE_PORTRAIT_OBJ_DEF = TunablePackSafeReference(description='\n        Object definition for a large portrait photo.\n        ', manager=services.definition_manager())
    LARGE_LANDSCAPE_OBJ_DEF = TunablePackSafeReference(description='\n        Object definition for a large landscape photo.\n        ', manager=services.definition_manager())
    PAINTING_INTERACTION_TAG = TunableEnumEntry(description='\n        Tag to specify a painting interaction.\n        ', tunable_type=tag.Tag, default=tag.Tag.INVALID)
    PHOTOGRAPHY_LOOT_LIST = TunableList(description='\n        A list of loot operations to apply to the photographer when photo mode exits.\n        ', tunable=TunableReference(manager=services.get_instance_manager(sims4.resources.Types.ACTION), class_restrictions=('LootActions',), pack_safe=True))
    FAIL_PHOTO_QUALITY_RANGE = TunableInterval(description='\n        The random quality statistic value that a failure photo will be\n        given between the min and max tuned values.\n        ', tunable_type=int, default_lower=0, default_upper=100)
    BASE_PHOTO_QUALITY_MAP = TunableMapping(description='\n        The mapping of CameraQuality value to an interval of quality values\n        that will be used to asign a random base quality value to a photo\n        as it is created.\n        ', key_type=TunableEnumEntry(description='\n            The CameraQuality value. If this photo has this CameraQuality,\n            value, then a random quality between the min value and max value\n            will be assigned to the photo.\n            ', tunable_type=CameraQuality, default=CameraQuality.CHEAP), value_type=TunableInterval(description='\n            The range of base quality values from which a random value will be\n            given to the photo.\n            ', tunable_type=int, default_lower=1, default_upper=100))
    QUALITY_MODIFIER_PER_SKILL_LEVEL = Tunable(description='\n        For each level of skill in Photography, this amount will be added to\n        the quality statistic.\n        ', tunable_type=float, default=0)
    PHOTO_VALUE_MODIFIER_MAP = TunableMapping(description='\n        The mapping of state values to Simoleon value modifiers.\n        The final value of a photo is decided based on its\n        current value multiplied by the sum of all modifiers for\n        states that apply to the photo. All modifiers are\n        added together first, then the sum will be multiplied by\n        the current price.\n        ', key_type=TunableStateValueReference(description='\n            The quality state values. If this photo has this state,\n            then a random modifier between min_value and max_value\n            will be multiplied to the current price.'), value_type=TunableInterval(description='\n            The maximum modifier multiplied to the current price based on the provided state value\n            ', tunable_type=float, default_lower=1, default_upper=1))
    PHOTO_VALUE_SKILL_CURVE = TunableStatisticModifierCurve.TunableFactory(description="\n        Allows you to adjust the final value of the photo based on the Sim's\n        level of a given skill.\n        ", axis_name_overrides=('Skill Level', 'Simoleon Multiplier'), locked_args={'subject': ParticipantType.Actor})
    PHOTOGRAPHY_SKILL = Skill.TunablePackSafeReference(description='\n        A reference to the photography skill.\n        ')
    EMOTION_STATE_MAP = TunableMapping(description="\n        The mapping of moods to states, used to give photo objects a mood\n        based state. These states are then used by the tooltip component to\n        display emotional content on the photo's tooltip.\n        ", key_type=TunableReference(description='\n            The mood to associate with a state.\n            ', manager=services.mood_manager()), value_type=TunableStateValueReference(description='\n            The state that represents the mood for the purpose of displaying\n            emotional content in a tooltip.\n            '))
    PHOTO_STUDIO_RIGHT_SLOT_TAG = TunableEnumEntry(description='\n        Tag to specify the photo studio interaction that the right-side photo\n        target sim will run.\n        ', tunable_type=tag.Tag, default=tag.Tag.INVALID)
    PHOTO_STUDIO_LEFT_SLOT_TAG = TunableEnumEntry(description='\n        Tag to specify the photo studio interaction that the left-side photo\n        target sim will run.\n        ', tunable_type=tag.Tag, default=tag.Tag.INVALID)
    NUM_PHOTOS_PER_SESSION = Tunable(description='\n        Max possible photos that can be taken during one photo session. Once\n        this number has been reached, the photo session will exit.\n        ', tunable_type=int, default=5)

    @classmethod
    def _is_fail_photo(cls, photo_style_type):
        if photo_style_type == PhotoStyleType.EFFECT_GRAINY or (photo_style_type == PhotoStyleType.EFFECT_OVERSATURATED or (photo_style_type == PhotoStyleType.EFFECT_UNDERSATURATED or (photo_style_type == PhotoStyleType.PHOTO_FAIL_BLURRY or (photo_style_type == PhotoStyleType.PHOTO_FAIL_FINGER or photo_style_type == PhotoStyleType.PHOTO_FAIL_GNOME)))) or photo_style_type == PhotoStyleType.PHOTO_FAIL_NOISE:
            return True
        return False

    @classmethod
    def _apply_quality_and_value_to_photo(cls, photographer_sim, photo_obj, photo_style, camera_quality):
        quality_stat = CraftingTuning.QUALITY_STATISTIC
        quality_stat_tracker = photo_obj.get_tracker(quality_stat)
        if cls._is_fail_photo(photo_style):
            final_quality = cls.FAIL_PHOTO_QUALITY_RANGE.random_int()
        else:
            quality_range = cls.BASE_PHOTO_QUALITY_MAP.get(camera_quality, None)
            if quality_range is None:
                logger.error('Photography tuning BASE_PHOTO_QUALITY_MAP does not have an expected quality value: []', str(camera_quality), owner='jwilkinson')
                return
            base_quality = quality_range.random_int()
            skill_quality_modifier = 0
            if cls.PHOTOGRAPHY_SKILL is not None:
                effective_skill_level = photographer_sim.get_effective_skill_level(cls.PHOTOGRAPHY_SKILL)
                if effective_skill_level:
                    skill_quality_modifier = effective_skill_level*cls.QUALITY_MODIFIER_PER_SKILL_LEVEL
            final_quality = base_quality + skill_quality_modifier
        quality_stat_tracker.set_value(quality_stat, final_quality)
        value_multiplier = 1
        for (state_value, value_mods) in cls.PHOTO_VALUE_MODIFIER_MAP.items():
            if photo_obj.has_state(state_value.state):
                actual_state_value = photo_obj.get_state(state_value.state)
                if state_value is actual_state_value:
                    value_multiplier *= value_mods.random_float()
                    break
        value_multiplier *= cls.PHOTO_VALUE_SKILL_CURVE.get_multiplier(SingleSimResolver(photographer_sim), photographer_sim)
        photo_obj.base_value = int(photo_obj.base_value*value_multiplier)

    @classmethod
    def _get_mood_sim_info_if_exists(cls, photographer_sim_info, target_sim_ids, camera_mode):
        if camera_mode is CameraMode.SELFIE_PHOTO:
            return photographer_sim_info
        else:
            num_target_sims = len(target_sim_ids)
            if num_target_sims == 1:
                sim_info_manager = services.sim_info_manager()
                target_sim_info = sim_info_manager.get(target_sim_ids[0])
                return target_sim_info

    @classmethod
    def _apply_mood_state_if_appropriate(cls, photographer_sim_info, target_sim_ids, camera_mode, photo_object):
        mood_sim_info = cls._get_mood_sim_info_if_exists(photographer_sim_info, target_sim_ids, camera_mode)
        if mood_sim_info:
            mood = mood_sim_info.get_mood()
            mood_state = cls.EMOTION_STATE_MAP.get(mood, None)
            if mood_state:
                photo_object.set_state(mood_state.state, mood_state)

    @classmethod
    def create_photo_from_photo_data(cls, camera_mode, camera_quality, photographer_sim_id, target_obj_id, target_sim_ids, res_key, photo_style, photo_size, photo_orientation, photographer_sim_info, photographer_sim, time_stamp):
        photo_object = None
        is_paint_by_reference = camera_mode is CameraMode.PAINT_BY_REFERENCE
        if is_paint_by_reference:
            current_zone = services.current_zone()
            photo_object = current_zone.object_manager.get(target_obj_id)
            if photo_object is None:
                photo_object = current_zone.inventory_manager.get(target_obj_id)
        else:
            if photo_orientation == PhotoOrientation.LANDSCAPE:
                if photo_size == PhotoSize.LARGE:
                    photo_object_def = cls.LARGE_LANDSCAPE_OBJ_DEF
                elif photo_size == PhotoSize.MEDIUM:
                    photo_object_def = cls.MEDIUM_LANDSCAPE_OBJ_DEF
                elif photo_size == PhotoSize.SMALL:
                    photo_object_def = cls.SMALL_LANDSCAPE_OBJ_DEF
            elif photo_orientation == PhotoOrientation.PORTRAIT:
                if photo_size == PhotoSize.LARGE:
                    photo_object_def = cls.LARGE_PORTRAIT_OBJ_DEF
                elif photo_size == PhotoSize.MEDIUM:
                    photo_object_def = cls.MEDIUM_PORTRAIT_OBJ_DEF
                elif photo_size == PhotoSize.SMALL:
                    photo_object_def = cls.SMALL_PORTRAIT_OBJ_DEF
                else:
                    photo_object_def = cls.SMALL_LANDSCAPE_OBJ_DEF
            if photo_object_def is None:
                return
            photo_object = create_object(photo_object_def)
        if photo_object is None:
            logger.error('photo object could not be found.', owner='jwilkinson')
            return
        photography_service = services.get_photography_service()
        loots = photography_service.get_loots_for_photo()
        for photoloot in loots:
            if photoloot._AUTO_FACTORY.FACTORY_TYPE is RotateTargetPhotoLoot:
                photographer_sim = photoloot.photographer
                photographer_sim_info = photographer_sim.sim_info
                break
        reveal_level = PaintingState.REVEAL_LEVEL_MIN if is_paint_by_reference else PaintingState.REVEAL_LEVEL_MAX
        painting_state = PaintingState.from_key(res_key, reveal_level, False, photo_style)
        photo_object.canvas_component.painting_state = painting_state
        photo_object.canvas_component.time_stamp = time_stamp
        photo_object.set_household_owner_id(photographer_sim.household_id)
        if not is_paint_by_reference:
            cls._apply_quality_and_value_to_photo(photographer_sim, photo_object, photo_style, camera_quality)
            cls._apply_mood_state_if_appropriate(photographer_sim_info, target_sim_ids, camera_mode, photo_object)
            photo_object.add_dynamic_component(STORED_SIM_INFO_COMPONENT, sim_id=photographer_sim.id)
            photo_object.update_object_tooltip()
            if photographer_sim.inventory_component.can_add(photo_object) and photographer_sim.inventory_component.player_try_add_object(photo_object):
                return
            logger.error("photo object could not be put in the sim's inventory, deleting photo.", owner='jwilkinson')
            photo_object.destroy()

class DefaultTakePhotoLoot(HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'photographer_loot': TunableReference(description='\n            Loot to apply to the Photographer.          \n            ', manager=services.get_instance_manager(sims4.resources.Types.ACTION), class_restrictions=('LootActions',), pack_safe=True)}

    def __init__(self, photographer, interaction, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def apply_loot(self, sim):
        photographer_info = services.sim_info_manager().get(sim.id)
        photographer_resolver = SingleSimResolver(photographer_info)
        if photographer_resolver is not None:
            self.photographer_loot.apply_to_resolver(photographer_resolver)

class RotateTargetPhotoLoot(HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'photographer_loot': TunableReference(description='\n            Loot to apply to the Photographer.\n            ', manager=services.get_instance_manager(sims4.resources.Types.ACTION), class_restrictions=('LootActions',), pack_safe=True), 'target_loot': TunableReference(description='\n            Loot to give to the Rotate Selfie Target.\n            ', manager=services.get_instance_manager(sims4.resources.Types.ACTION), class_restrictions=('LootActions',), pack_safe=True), 'notification': OptionalTunable(description='\n            If enabled, this notification will show after the photo is\n            taken.\n            ', tunable=UiDialogNotification.TunableFactory()), 'statistic_info': OptionalTunable(description="\n            Statistic to be passed in as an additional token available. The\n            token will be the difference between the tuned statistics value\n            before the interaction and after the loot is applied.\n            \n            Use Case: Simstagram Pet interaction gives to the pet's simstagram\n            account, and the player sees a notification with the amount of followers\n            gained.\n            \n            IMPORTANT: The tuned statistic is expected to have a default value of\n            0. If not, the resulting difference token will not be accurate. \n            ", tunable=TunableTuple(description=' \n                Specify the value of a specific statistic from the selected participant.\n                ', participant=TunableEnumEntry(description="\n                    The participant from whom we will fetch the specified\n                    statistic's value.\n                    ", tunable_type=ParticipantType, default=ParticipantType.Actor), statistic=TunableReference(description="\n                    The statistic's whose value we want to fetch.\n                    ", manager=services.statistic_manager())))}

    def __init__(self, photographer, interaction, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.photographer = photographer
        self.stored_statistic_value = 0
        if self.statistic_info is None:
            return
        participant = self.statistic_info.participant
        sim = interaction.get_participant(participant)
        if participant is not None:
            tracker = sim.get_tracker(self.statistic_info.statistic)
            if tracker is not None:
                self.stored_statistic_value = tracker.get_value(self.statistic_info.statistic)

    def apply_loot(self, sim):
        target_info = services.sim_info_manager().get(sim.id)
        target_resolver = SingleSimResolver(target_info)
        self.target_loot.apply_to_resolver(target_resolver)
        photographer_info = services.sim_info_manager().get(self.photographer.id)
        photographer_resolver = SingleSimResolver(photographer_info)
        self.photographer_loot.apply_to_resolver(photographer_resolver)
        tracker = target_info.get_tracker(self.statistic_info.statistic)
        current_statvalue = tracker.get_value(self.statistic_info.statistic)
        change_amount = abs(current_statvalue - self.stored_statistic_value)
        if self.photographer is None:
            logger.error('Got a None Sim {} while applying loot to the photographer.', self.photographer, owner='shipark')
        if self.notification is None:
            return
        notification = self.notification(self.photographer, resolver=DoubleSimResolver(photographer_info, target_info), target_sim_id=sim.id)
        if change_amount > 0:
            notification.show_dialog(additional_tokens=(change_amount,))
        else:
            notification.show_dialog()

class TakePhoto(XevtTriggeredElement):

    class _BasePhotoMode(HasTunableSingletonFactory, AutoFactoryInit):

        def create_take_photo_op(self, sims, interaction):
            take_photo_proto = DistributorOps_pb2.TakePhoto()
            take_photo_proto.camera_mode = self._get_camera_mode()
            take_photo_proto.zoom_capability = self.zoom_capability
            take_photo_proto.camera_quality = self.camera_quality
            take_photo_proto.hide_photographer = self.hide_photographer
            take_photo_proto.success_chance = self.success_chance.get_chance(interaction.get_resolver())
            take_photo_proto.camera_position_bone_name = self.camera_position_bone_name
            offset = self._get_offset(interaction)
            take_photo_proto.camera_position_offset.x = offset.x
            take_photo_proto.camera_position_offset.y = offset.y
            take_photo_proto.camera_position_offset.z = offset.z
            take_photo_proto.rotate_target = self.enable_rotate_target(interaction)
            if self._get_camera_mode() is CameraMode.PAINT_BY_REFERENCE:
                painting = interaction.get_participant(ParticipantType.CreatedObject)
                if painting is not None:
                    take_photo_proto.target_object = painting.id
            for (index, sim) in enumerate(sims):
                with ProtocolBufferRollback(take_photo_proto.sim_photo_infos) as entry:
                    entry.participant_sim_id = sim.sim_id
                    entry.participant_sim_position.x = sim.position.x
                    entry.participant_sim_position.y = sim.position.y
                    entry.participant_sim_position.z = sim.position.z
                    if self.photo_pose is not None:
                        if self.photo_pose.asm is not None:
                            entry.animation_pose.asm = get_protobuff_for_key(self.photo_pose.asm)
                            entry.animation_pose.state_name = self.photo_pose.state_name
                            actor_name = self._get_actor_name(index)
                            if actor_name is not None:
                                entry.animation_pose.actor_name = actor_name
            take_photo_proto.filters_disabled = self.filters_disabled
            take_photo_proto.single_shot_mode = self.single_shot_mode
            take_photo_proto.painting_size = self._get_photo_size()
            if self._get_camera_mode() == CameraMode.SIM_PHOTO or self._get_camera_mode() == CameraMode.PHOTO_STUDIO_PHOTO:
                mood_target_sim = sims[1] if len(sims) > 1 else None
            else:
                mood_target_sim = sims[0]
            if mood_target_sim is not None:
                take_photo_proto.sim_mood_asm_param_name = mood_target_sim.get_mood_animation_param_name()
            bone_object = interaction.get_participant(self.camera_position_bone_object)
            if bone_object is not None:
                take_photo_proto.camera_position_bone_object = bone_object.id
            take_photo_proto.num_photos_per_session = Photography.NUM_PHOTOS_PER_SESSION
            take_photo_op = GenericProtocolBufferOp(DistributorOps_pb2.Operation.TAKE_PHOTO, take_photo_proto)
            return take_photo_op

        def _get_camera_mode(self):
            raise NotImplementedError('Attempting to call _get_camera_mode() on the base class, use sub-classes instead.')

        def _get_actor_name(self, index):
            return 'x'

        def _get_photo_size(self):
            return PhotoSize.LARGE

        def _get_offset(self, interaction):
            return Vector3.ZERO()

        def enable_rotate_target(self, interaction):
            return True

        FACTORY_TUNABLES = {'zoom_capability': TunableEnumEntry(description='\n                The zoom capability of the camera.\n                ', tunable_type=ZoomCapability, default=ZoomCapability.NO_ZOOM), 'camera_quality': TunableEnumEntry(description='\n                The quality of the camera.\n                ', tunable_type=CameraQuality, default=CameraQuality.CHEAP), 'hide_photographer': Tunable(description='\n                Whether or not to hide the photographer during the photo session.\n                ', tunable_type=bool, default=False), 'success_chance': SuccessChance.TunableFactory(description='\n                Percent chance that a photo will be successful.\n                '), 'camera_position_bone_name': Tunable(description='\n                Which bone on the photographer to use for the camera position.\n                ', tunable_type=str, default='', allow_empty=True), 'camera_position_bone_object': TunableEnumEntry(description='\n                The object that has the bone from which the camera position is\n                obtained. This is usually the photographer sim.\n                ', tunable_type=ParticipantTypeSingle, default=ParticipantType.Actor), 'filters_disabled': Tunable(description='\n                Whether or not to disable photo filters.\n                ', tunable_type=bool, default=False), 'single_shot_mode': Tunable(description='\n                Whether or not to only allow the photographer to take one photo\n                per session.\n                ', tunable_type=bool, default=False), 'photo_pose': ObjectPose.TunableReference(description='\n                The pose the sims in the photo will use.\n                '), 'photographer_sim': TunableEnumEntry(description='\n                The participant Sim that is the photographer.\n                ', tunable_type=ParticipantTypeSingle, default=ParticipantType.Actor), 'photo_target_sims': OptionalTunable(TunableEnumEntry(description='\n                The participant Sims that are the target of the photograph.\n                ', tunable_type=ParticipantType, default=ParticipantType.TargetSim))}

    class _FreeFormPhotoMode(_BasePhotoMode):
        FACTORY_TUNABLES = {'locked_args': {'photo_target_sims': None, 'photo_pose': None}}

        def _get_camera_mode(self):
            return CameraMode.FREE_FORM_PHOTO

    class _SimPhotoMode(_BasePhotoMode):

        def _get_camera_mode(self):
            return CameraMode.SIM_PHOTO

    class _SelfiePhotoMode(_BasePhotoMode):
        FACTORY_TUNABLES = {'locked_args': {'photo_target_sims': None}}

        def _get_camera_mode(self):
            return CameraMode.SELFIE_PHOTO

    class _TwoSimSelfiePhotoMode(_BasePhotoMode):

        def _get_camera_mode(self):
            return CameraMode.TWO_SIM_SELFIE_PHOTO

        def _get_actor_name(self, index):
            if index == 0:
                return 'x'
            elif index == 1:
                return 'y'

    class _PhotoStudioPhotoMode(_BasePhotoMode):

        def _get_camera_mode(self):
            return CameraMode.PHOTO_STUDIO_PHOTO

        def _get_actor_name(self, index):
            if index == 0:
                return
            if index == 1:
                return 'x'
            elif index == 2:
                return 'y'

    class _PaintByReferenceMode(_BasePhotoMode):
        FACTORY_TUNABLES = {'canvas_size': TunableEnumEntry(description='\n                The size of the canvas.\n                ', tunable_type=PhotoSize, default=PhotoSize.LARGE), 'locked_args': {'photo_target_sims': None, 'photo_pose': None}}

        def _get_camera_mode(self):
            return CameraMode.PAINT_BY_REFERENCE

        def _get_photo_size(self):
            return self.canvas_size

    class _RotateTargetSelfieMode(_BasePhotoMode):
        FACTORY_TUNABLES = {'rotate_target_sim': TunableEnumEntry(description='\n                The participant used as the rotate selfie subject.\n                ', tunable_type=ParticipantTypeSingle, default=ParticipantType.TargetSim), 'forward_distance_multiplier_map': TunableMapping(description='\n                Mapping between species and forward distance the camera will be\n                set from the rotate selfie subject. \n                ', key_type=TunableEnumEntry(description='\n                    Species these values are intended for.\n                    ', tunable_type=SpeciesExtended, default=SpeciesExtended.HUMAN, invalid_enums=(SpeciesExtended.INVALID,)), value_type=Tunable(description='\n                    The the forward distance from the rotation target that the\n                    camera will be placed. \n                    ', tunable_type=float, default=1.2)), 'locked_args': {'photo_target_sims': None, 'photo_pose': None}}

        def _get_camera_mode(self):
            return CameraMode.SELFIE_PHOTO

        def _get_offset(self, interaction):
            rotate_target = interaction.get_participant(self.rotate_target_sim)
            multiplier = self.forward_distance_multiplier_map.get(rotate_target.extended_species)
            offset = rotate_target.forward*multiplier
            return offset

        def enable_rotate_target(self, interaction):
            rotate_target = interaction.get_participant(self.rotate_target_sim)
            if rotate_target is None:
                logger.error('Got a None Sim {} trying to run interaction {}.', self.rotate_target_sim, interaction, owner='shipark')
                return True
            return False

    FACTORY_TUNABLES = {'photo_mode': TunableVariant(description='\n            The photo mode to use for this photo session.\n            ', free_form_photo=_FreeFormPhotoMode.TunableFactory(), sim_photo=_SimPhotoMode.TunableFactory(), selfie_photo=_SelfiePhotoMode.TunableFactory(), two_sim_selfie_photo=_TwoSimSelfiePhotoMode.TunableFactory(), photo_studio_photo=_PhotoStudioPhotoMode.TunableFactory(), paint_by_reference=_PaintByReferenceMode.TunableFactory(), rotate_target_selfie=_RotateTargetSelfieMode.TunableFactory(), default='free_form_photo'), 'loot_to_apply': TunableList(description='\n            Loot defined here will be applied to the participants of the photography\n            interaction after the systems photography call is finished.\n            ', tunable=TunableVariant(description='\n            Select Default Take Photo Loot for most Camera Modes.\n            Select Rotate Target Photo Loot for Rotate Target Selfie Mode.\n            ', photoLoot=DefaultTakePhotoLoot.TunableFactory(), targetPhotoLoot=RotateTargetPhotoLoot.TunableFactory(), default='photoLoot'), set_default_as_first_entry=True)}

    def _find_sim_with_interaction_tag(self, photo_target_sims, interaction_tag):
        for sim in photo_target_sims:
            if sim.get_running_and_queued_interactions_by_tag({interaction_tag}):
                return sim

    def _order_group_photo_sims(self, photo_target_sims):
        left_sim = self._find_sim_with_interaction_tag(photo_target_sims, Photography.PHOTO_STUDIO_LEFT_SLOT_TAG)
        right_sim = self._find_sim_with_interaction_tag(photo_target_sims, Photography.PHOTO_STUDIO_RIGHT_SLOT_TAG)
        if left_sim is None or right_sim is None:
            return
        return [left_sim, right_sim]

    def _do_behavior(self):
        photographer_sim = self.interaction.get_participant(self.photo_mode.photographer_sim)
        if photographer_sim is None:
            logger.error('take_photo basic extra could not find a photographer {}', owner='jwilkinson')
            return False
        sims = []
        sims.append(photographer_sim)
        if self.photo_mode.photo_target_sims:
            photo_target_sims = self.interaction.get_participants(self.photo_mode.photo_target_sims)
            num_target_sims = len(photo_target_sims)
            if num_target_sims > 2:
                logger.error('take_photo basic extra found more than two photo                               target participants. This is not supported - will                               use the first two photo participants instead.', owner='jwilkinson')
                del photo_target_sims[2:]
            if photographer_sim in photo_target_sims:
                logger.error('take_photo basic extra found the photographer sim                               in the set of tuned photo target sims. Please                               choose a participant type that does not include                               the photographer.', owner='jwilkinson')
                return False
            if num_target_sims > 1:
                photo_target_sims = self._order_group_photo_sims(photo_target_sims)
                if photo_target_sims is None:
                    logger.error('Could not properly order the sims for the group photo.', owner='jwilkinson')
                    return False
            sims.extend(photo_target_sims)
        is_rotate_selfie_mode = self.photo_mode.enable_rotate_target(self.interaction)
        if not is_rotate_selfie_mode:
            sims = self.interaction.get_participants(self.photo_mode.rotate_target_sim)
        photography_service = services.get_photography_service()
        for photoloot in self.loot_to_apply:
            loot = photoloot(self.interaction.sim, self.interaction)
            photography_service.add_loot_for_next_photo_taken(loot)
        op = self.photo_mode.create_take_photo_op(sims, self.interaction)
        Distributor.instance().add_op(photographer_sim, op)
        return True

class SetPhotoFilter(XevtTriggeredElement):
    FACTORY_TUNABLES = {'participant': TunableEnumEntry(description='\n            The participant object that is the photo.\n            ', tunable_type=ParticipantTypeSingle, default=ParticipantType.Object), 'photo_filter': TunableEnumEntry(description='\n            The photo filter that you want this photo to use.\n            ', tunable_type=PhotoStyleType, default=PhotoStyleType.NORMAL)}

    def _do_behavior(self):
        photo_obj = self.interaction.get_participant(self.participant)
        if photo_obj is None:
            logger.error('set_photo_filter basic extra tuned participant does not exist.', owner='jwilkinson')
            return False
        canvas_component = photo_obj.canvas_component
        if canvas_component is None:
            logger.error('set_photo_filter basic extra tuned participant does not have a canvas component.', owner='jwilkinson')
            return False
        canvas_component.painting_effect = self.photo_filter
        return True

class CreatePhotoMemory(XevtTriggeredElement):
    FACTORY_TUNABLES = {'photo_object': TunableEnumEntry(description='\n            The participant object that is the photo.\n            ', tunable_type=ParticipantTypeSingle, default=ParticipantType.Object), 'memory_sim': TunableEnumEntry(description='\n            The participant Sim that is the Sim making the memory.\n            ', tunable_type=ParticipantTypeSingle, default=ParticipantType.Actor)}

    def _create_make_memory_from_photo_op(self, memory_sim, canvas_component):
        make_memory_proto = DistributorOps_pb2.MakeMemoryFromPhoto()
        make_memory_proto.household_id = memory_sim.sim_info.household_id
        for sim in self.interaction.get_participants(participant_type=ParticipantType.PickedSim):
            make_memory_proto.sim_ids.append(sim.sim_id)
        make_memory_proto.texture_id = canvas_component.painting_state.texture_id
        make_memory_proto.filter_style = canvas_component.painting_effect
        make_memory_proto.time_stamp = canvas_component.time_stamp
        return GenericProtocolBufferOp(DistributorOps_pb2.Operation.MAKE_MEMORY_FROM_PHOTO, make_memory_proto)

    def _do_behavior(self):
        memory_sim = self.interaction.get_participant(self.memory_sim)
        if memory_sim is None:
            logger.error('create_photo_memory basic extra could not find a sim {}', owner='jwilkinson')
            return False
        photo_obj = self.interaction.get_participant(self.photo_object)
        if photo_obj is None:
            logger.error('create_photo_memory basic extra tuned photo_object participant does not exist.', owner='jwilkinson')
            return False
        canvas_component = photo_obj.canvas_component
        if canvas_component is None:
            logger.error('create_photo_memory basic extra tuned photo_object participant does not have a canvas component.', owner='jwilkinson')
            return False
        op = self._create_make_memory_from_photo_op(memory_sim, canvas_component)
        Distributor.instance().add_op(memory_sim, op)
        return True
