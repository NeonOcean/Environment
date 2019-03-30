from collections import namedtuple
import random
from animation import AnimationContext, get_throwaway_animation_context
from animation.animation_constants import InteractionAsmType, AUTO_EXIT_REF_TAG, MAX_ZERO_LENGTH_ASM_CALLS_FOR_RESET
from animation.animation_utils import get_actors_for_arb_sequence, create_run_animation, get_auto_exit, mark_auto_exit, flush_all_animations, AnimationOverrides
from animation.awareness.awareness_elements import with_audio_awareness
from animation.posture_manifest import PostureManifestOverrideValue, PostureManifestOverrideKey, PostureManifest, MATCH_ANY, MATCH_NONE, AnimationParticipant
from balloon.tunable_balloon import TunableBalloon
from element_utils import build_critical_section, build_critical_section_with_finally, build_element, do_all
from event_testing.results import TestResult
from interactions import ParticipantTypeReactionlet, ParticipantType
from interactions.utils.animation_selector import TunableAnimationSelector
from objects.props.prop_share_override import PropShareOverride
from sims4.collections import frozendict
from sims4.tuning.instances import TunedInstanceMetaclass
from sims4.tuning.tunable import TunableFactory, Tunable, TunableList, TunableTuple, TunableReference, TunableResourceKey, TunableVariant, OptionalTunable, TunableMapping, TunableSingletonFactory, HasTunableReference, TunableInteractionAsmResourceKey
from sims4.tuning.tunable_base import SourceQueries, SourceSubQueries, FilterTag
from sims4.tuning.tunable_hash import TunableStringHash32
from sims4.utils import classproperty, flexmethod
from singletons import DEFAULT, UNSET
from tunable_utils.tunable_offset import TunableOffset
import animation
import animation.arb
import animation.asm
import animation.posture_manifest
import element_utils
import elements
import gsi_handlers.interaction_archive_handlers
import services
import sims4.log
logger = sims4.log.Logger('Animation')
dump_logger = sims4.log.LoggerClass('Animation')

class TunableParameterMapping(TunableMapping):

    def __init__(self, **kwargs):
        super().__init__(key_name='name', value_type=TunableVariant(default='string', boolean=Tunable(bool, False), string=Tunable(str, 'value'), integral=Tunable(int, 0)), **kwargs)

class TunablePostureManifestCellValue(TunableVariant):
    __slots__ = ()

    def __init__(self, allow_none, string_name, string_default=None, asm_source=None, source_query=None):
        if asm_source is not None:
            asm_source = '../' + asm_source
        else:
            source_query = None
        locked_args = {'match_none': animation.posture_manifest.MATCH_NONE, 'match_any': animation.posture_manifest.MATCH_ANY}
        default = 'match_any'
        kwargs = {string_name: Tunable(str, string_default, source_location=asm_source, source_query=source_query)}
        if allow_none:
            locked_args['leave_unchanged'] = None
            default = 'leave_unchanged'
        super().__init__(default=default, locked_args=locked_args, **kwargs)

class TunablePostureManifestOverrideKey(TunableSingletonFactory):
    FACTORY_TYPE = PostureManifestOverrideKey

    def __init__(self, asm_source=None):
        if asm_source is not None:
            asm_source = '../' + asm_source
            source_query = SourceQueries.ASMActorSim
        else:
            source_query = None
        super().__init__(actor=TunablePostureManifestCellValue(False, 'actor_name', asm_source=asm_source, source_query=source_query), specific=TunablePostureManifestCellValue(False, 'posture_name', 'stand'), family=TunablePostureManifestCellValue(False, 'posture_name', 'stand'), level=TunablePostureManifestCellValue(False, 'overlay_level', 'FullBody'))

class TunablePostureManifestOverrideValue(TunableSingletonFactory):
    FACTORY_TYPE = PostureManifestOverrideValue

    def __init__(self, asm_source=None):
        if asm_source is not None:
            asm_source = '../' + asm_source
            source_query = SourceQueries.ASMActorObject
        else:
            source_query = None
        super().__init__(left=TunablePostureManifestCellValue(True, 'actor_name', asm_source=asm_source, source_query=source_query), right=TunablePostureManifestCellValue(True, 'actor_name', asm_source=asm_source, source_query=source_query), surface=TunablePostureManifestCellValue(True, 'actor_name', 'surface', asm_source=asm_source, source_query=source_query))

RequiredSlotOverride = namedtuple('RequiredSlotOverride', ('actor_name', 'parent_name', 'slot_type'))

class TunableRequiredSlotOverride(TunableSingletonFactory):
    __slots__ = ()
    FACTORY_TYPE = RequiredSlotOverride

    def __init__(self, asm_source=None):
        if asm_source is not None:
            source_query = SourceQueries.ASMActorObject
        else:
            source_query = None
        super().__init__(actor_name=Tunable(str, None, source_location=asm_source, source_query=source_query), parent_name=Tunable(str, 'surface', source_location=asm_source, source_query=source_query), slot_type=TunableReference(services.get_instance_manager(sims4.resources.Types.SLOT_TYPE)))

class TunableAnimationOverrides(TunableFactory):

    @staticmethod
    def _factory(*args, manifests, **kwargs):
        if manifests is not None:
            key_name = 'key'
            value_name = 'value'
            manifests_dict = {}
            for item in manifests:
                key = getattr(item, key_name)
                if key in manifests_dict:
                    import sims4.tuning.tunable
                    sims4.tuning.tunable.logger.error('Multiple values specified for {} in manifests in an animation overrides block.', key)
                else:
                    manifests_dict[key] = getattr(item, value_name)
        else:
            manifests_dict = None
        return AnimationOverrides(*args, manifests=manifests_dict, **kwargs)

    FACTORY_TYPE = _factory

    def __init__(self, asm_source=None, state_source=None, allow_reactionlets=True, override_animation_context=False, participant_enum_override=DEFAULT, description='Overrides to apply to the animation request.', **kwargs):
        if asm_source is not None:
            asm_source = '../../../' + asm_source
            clip_actor_asm_source = asm_source
            vfx_sub_query = SourceSubQueries.ClipEffectName
            sound_sub_query = SourceSubQueries.ClipSoundName
            if state_source is not None:
                last_slash_index = clip_actor_asm_source.rfind('/')
                clip_actor_state_source = clip_actor_asm_source[:last_slash_index + 1] + state_source
                clip_actor_state_source = '../' + clip_actor_state_source
                clip_actor_state_source = SourceQueries.ASMClip.format(clip_actor_state_source)
        else:
            clip_actor_asm_source = None
            clip_actor_state_source = None
            vfx_sub_query = None
            sound_sub_query = None
        if participant_enum_override is DEFAULT:
            participant_enum_override = (ParticipantTypeReactionlet, ParticipantTypeReactionlet.Invalid)
        if allow_reactionlets:
            kwargs['reactionlet'] = OptionalTunable(TunableAnimationSelector(description='\n                Reactionlets are short, one-shot animations that are triggered \n                via x-event.\n                X-events are markers in clips that can trigger an in-game \n                effect that is timed perfectly with the clip. Ex: This is how \n                we trigger laughter at the exact moment of the punchline of a \n                Joke\n                It is EXTREMELY important that only content authored and \n                configured by animators to be used as a Reactionlet gets \n                hooked up as Reactionlet content. If this rule is violated, \n                crazy things will happen including the client and server losing \n                time sync. \n                ', interaction_asm_type=InteractionAsmType.Reactionlet, override_animation_context=True, participant_enum_override=participant_enum_override))
        super().__init__(params=TunableParameterMapping(description='\n                This tuning is used for overriding parameters on the ASM to \n                specific values.\n                These will take precedence over those same settings coming from \n                runtime so be careful!\n                You can enter a number of overrides as key/value pairs:\n                Name is the name of the parameter as it appears in the ASM.\n                Value is the value to set on the ASM.\n                Make sure to get the type right. Parameters are either \n                booleans, enums, or strings.\n                Ex: The most common usage of this field is when tuning the \n                custom parameters on specific objects, such as the objectName \n                parameter. \n                '), vfx=TunableMapping(description="\n                VFX overrides for this animation. The key is the effect's actor\n                name. Please note, this is not the name of the vfx that would\n                normally play. This is the name of the actor in the ASM that is\n                associated to a specific effect.\n                ", key_name='original_effect', value_name='replacement_effect', value_type=TunableTuple(description='\n                    Override data for the specified effect actor.\n                    ', effect=OptionalTunable(description='\n                        Override the actual effect that is meant to be played.\n                        It can be left None to stop the effect from playing\n                        ', disabled_name='no_effect', enabled_name='play_effect', tunable=Tunable(tunable_type=str, default='')), mirrored_effect=OptionalTunable(description="\n                        If enabled and the is_mirrored parameter comes through\n                        as True, we will play this effect instead of the tuned\n                        override. NOTE: if you tune this, the non-mirrored\n                        version must also be tuned in the regular effect\n                        override for it to play. For example, the Bubble Bottle\n                        needs to play mirrored effects for left handed Sims,\n                        but if we don't override the effect and still want to\n                        play a mirrored version, we need to specify the\n                        original effect so we don't play nothing.\n                        ", tunable=Tunable(description='\n                            The name of the mirrored effect.\n                            ', tunable_type=str, default='')), effect_joint=OptionalTunable(description='\n                        Overrides the effect joint of the VFX.  Use this\n                        specify a different joint name to attach the effect to.\n                        ', disabled_name='no_override', enabled_name='override_joint', tunable=TunableStringHash32()), target_joint=OptionalTunable(description='\n                        Overrides the target joint of the VFX.  This is used in\n                        case of attractors where we want the effect to target a\n                        different place per object on the same animation\n                        ', disabled_name='no_override', enabled_name='override_joint', tunable=TunableStringHash32()), target_joint_offset=OptionalTunable(description='\n                        Overrides the target joint offset of the VFX.  \n                        This is used in case of point to point VFX where\n                        we want the effect to reach a destination\n                        offset from the target joint.\n                        ', disabled_name='no_override', enabled_name='override_offset', tunable=TunableOffset()), callback_event_id=OptionalTunable(description='\n                        Specifies a callback xevt id we want the vfx to trigger\n                        when it fulfills a contracted duty.\n                        \n                        For example, it can call this xevt on point-to-point vfx\n                        if the effect reaches the target event.\n                        ', tunable=Tunable(int, 0))), key_type=Tunable(str, None, source_location=clip_actor_asm_source, source_query=clip_actor_state_source, source_sub_query=vfx_sub_query), allow_none=True), sounds=TunableMapping(description='The sound overrides.', key_name='original_sound', value_name='replacement_sound', value_type=OptionalTunable(disabled_name='no_sound', enabled_name='play_sound', disabled_value=UNSET, tunable=TunableResourceKey(None, (sims4.resources.Types.PROPX,), description='The sound to play.')), key_type=Tunable(str, None, source_location=clip_actor_asm_source, source_query=clip_actor_state_source, source_sub_query=sound_sub_query)), props=TunableMapping(description='\n                The props overrides.\n                ', value_type=TunableTuple(definition=TunableReference(description='\n                        The object to create to replace the prop\n                        ', manager=services.definition_manager()), from_actor=Tunable(description='\n                        The actor name inside the asm to copy the state over.\n                        ', tunable_type=str, default=None), states_to_override=TunableList(description='\n                        A list of states that will be transferred from\n                        the specified actor to the overridden prop.\n                        ', tunable=TunableReference(description='\n                            The state to apply on the props from the actor listed above.\n                            ', manager=services.get_instance_manager(sims4.resources.Types.OBJECT_STATE), class_restrictions='ObjectState', pack_safe=True)), sharing=OptionalTunable(description='\n                        If enabled, this prop may be shared across ASMs.\n                        ', tunable=PropShareOverride.TunableFactory()), set_as_actor=OptionalTunable(description='\n                        If enabled the prop defined by override will be set\n                        as an actor of the ASM.\n                        This is used in cases like setting the chopsticks prop\n                        on the eat ASM.  In this ASM the chopsticks are set as \n                        an Object actor so they can animate. Currently we do\n                        not support props playing their own animations.  \n                        ', tunable=Tunable(description='\n                            Actor name that will be used on the ASM for the \n                            prop animation.\n                            ', tunable_type=str, default=None), enabled_name='actor_name'))), prop_state_values=TunableMapping(description='\n                Tunable mapping from a prop actor name to a list of state\n                values to set. If conflicting data is tuned both here and in\n                the "props" field, the data inside "props" will override the\n                data tuned here.\n                ', value_type=TunableList(description='\n                    A list of state values that will be set on the specified\n                    actor.\n                    ', tunable=TunableReference(description='\n                        A new state value to apply to prop_actor.\n                        ', manager=services.get_instance_manager(sims4.resources.Types.OBJECT_STATE), class_restrictions='ObjectStateValue'))), manifests=TunableList(description='\n                Manifests is a complex and seldom used override that lets you \n                change entries in the posture manifest from the ASM.\n                You can see how the fields, Actor, Family, Level, Specific, \n                Left, Right, and Surface, match the manifest entries in the \n                ASM. \n                ', tunable=TunableTuple(key=TunablePostureManifestOverrideKey(asm_source=asm_source), value=TunablePostureManifestOverrideValue(asm_source=asm_source))), required_slots=TunableList(TunableRequiredSlotOverride(asm_source=asm_source), description='Required slot overrides'), balloons=OptionalTunable(TunableList(description='\n                Balloons lets you add thought and talk balloons to animations. \n                This is a great way to put extra flavor into animations and \n                helps us stretch our content by creating combinations.\n                Balloon Animation Target is the participant who should display \n                the balloon.\n                Balloon Choices is a reference to the balloon to display, which \n                is its own tunable type.\n                Balloon Delay (and Random Offset) is how long, in real seconds, \n                to delay this balloon after the animation starts.  Note: for \n                looping animations, the balloon will always play immediately \n                due to a code limitation.\n                Balloon Target is for showing a balloon of a Sim or Object. \n                Set this to the participant type to show. This setting \n                overrides Balloon Choices. \n                ', tunable=TunableBalloon())), animation_context=Tunable(description="\n                Animation Context - If checked, this animation will get a fresh \n                animation context instead of reusing the animation context of \n                its Interaction.\n                Normally, animation contexts are shared across an entire Super \n                Interaction. This allows mixers to use a fresh animation \n                context.\n                Ex: If a mixer creates a prop, using a fresh animation context \n                will cause that prop to be destroyed when the mixer finishes, \n                whereas re-using an existing animation context will cause the \n                prop to stick around until the mixer's SI is done. \n                ", tunable_type=bool, default=override_animation_context), description=description, **kwargs)

class TunableAnimationObjectOverrides(TunableAnimationOverrides):
    LOCKED_ARGS = {'manifests': None, 'required_slots': None, 'balloons': None, 'reactionlet': None}

    def __init__(self, description='Animation overrides to apply to every ASM to which this object is added.', **kwargs):
        super().__init__(locked_args=TunableAnimationObjectOverrides.LOCKED_ARGS, **kwargs)

logged_missing_interaction_callstack = False

def _create_balloon_request_callback(balloon_request=None):

    def balloon_handler_callback(_):
        balloon_request.distribute()

    return balloon_handler_callback

def _register_balloon_requests(asm, interaction, overrides, balloon_requests, repeat=False):
    if not balloon_requests:
        return
    remaining_balloons = list(balloon_requests)
    for balloon_request in balloon_requests:
        balloon_delay = balloon_request.delay or 0
        if balloon_request.delay_randomization > 0:
            balloon_delay += random.random()*balloon_request.delay_randomization
        if asm.context.register_custom_event_handler(_create_balloon_request_callback(balloon_request=balloon_request), None, balloon_delay, allow_stub_creation=True):
            remaining_balloons.remove(balloon_request)
        if repeat:
            break
    if remaining_balloons and not repeat:
        logger.error('Failed to schedule all requested balloons for {}', asm)
    elif repeat:
        balloon_requests = TunableBalloon.get_balloon_requests(interaction, overrides)
    return balloon_requests

def get_asm_supported_posture(asm_key, actor_name, overrides):
    context = get_throwaway_animation_context()
    posture_manifest_overrides = None
    if overrides is not None:
        posture_manifest_overrides = overrides.manifests
    asm = animation.asm.create_asm(asm_key, context, posture_manifest_overrides=posture_manifest_overrides)
    return asm.get_supported_postures_for_actor(actor_name)

def animate_states(asm, begin_states, end_states=None, sequence=(), require_end=True, overrides=None, balloon_requests=None, setup_asm=None, cleanup_asm=None, enable_auto_exit=True, repeat_begin_states=False, interaction=None, additional_blockers=(), **kwargs):
    if asm is not None:
        requires_begin_flush = bool(sequence)
        all_actors = set()
        do_gsi_logging = interaction is not None and gsi_handlers.interaction_archive_handlers.is_archive_enabled(interaction)
        if interaction is not None:
            interaction.register_additional_event_handlers(asm.context)

        def do_begin(timeline):
            nonlocal balloon_requests, all_actors
            if overrides:
                overrides.override_asm(asm)
            if setup_asm is not None:
                result = setup_asm(asm)
                if not result:
                    logger.error('Animate States failed to setup ASM {}. {}', asm, result, owner='rmccord')
            if do_gsi_logging:
                for (actor_name, (actor, _, _)) in asm._actors.items():
                    actor = actor()
                    gsi_handlers.interaction_archive_handlers.add_asm_actor_data(interaction, asm, actor_name, actor)
            if begin_states:
                balloon_requests = _register_balloon_requests(asm, interaction, overrides, balloon_requests, repeat=repeat_begin_states)
                arb_begin = animation.arb.Arb(additional_blockers=additional_blockers)
                if do_gsi_logging:
                    gsi_archive_logs = []
                if asm.current_state == 'exit':
                    asm.set_current_state('entry')
                for state in begin_states:
                    if do_gsi_logging:
                        prev_state = asm.current_state
                        arb_buffer = arb_begin.get_contents_as_string()
                    asm.request(state, arb_begin, debug_context=interaction)
                    if do_gsi_logging:
                        arb_begin_str = arb_begin.get_contents_as_string()
                        current_arb_str = arb_begin_str[arb_begin_str.find(arb_buffer) + len(arb_buffer):]
                        gsi_archive_logs.append((prev_state, state, current_arb_str))
                actors_begin = get_actors_for_arb_sequence(arb_begin)
                all_actors = all_actors | actors_begin
                sequence = create_run_animation(arb_begin)
                if asm.current_state == 'exit':
                    auto_exit_releases = mark_auto_exit(actors_begin, asm)
                    if auto_exit_releases is not None:
                        sequence = build_critical_section_with_finally(sequence, auto_exit_releases)
                try:
                    auto_exit_element = get_auto_exit(actors_begin, asm=asm, interaction=interaction)
                except RuntimeError:
                    if do_gsi_logging:
                        for (prev_state, state, current_arb_str) in gsi_archive_logs:
                            gsi_handlers.interaction_archive_handlers.add_animation_data(interaction, asm, prev_state, state, current_arb_str)
                        for actor_to_log in actors_begin:
                            gsi_handlers.interaction_archive_handlers.archive_interaction(actor_to_log, interaction, 'RUNTIME ERROR')
                    raise
                if auto_exit_element is not None:
                    sequence = (auto_exit_element, sequence)
                if asm.current_state != 'exit':
                    auto_exit_actors = {actor for actor in all_actors if actor.is_sim and not actor.asm_auto_exit.locked}
                    for actor in auto_exit_actors:
                        if actor.asm_auto_exit.asm is None:
                            actor.asm_auto_exit.asm = (asm, auto_exit_actors, asm.context)
                            asm.context.add_ref(AUTO_EXIT_REF_TAG)
                        elif actor.asm_auto_exit.asm[0] != asm:
                            raise RuntimeError('Multiple ASMs in need of auto-exit simultaneously: {} and {}'.format(actor.asm_auto_exit.asm[0], asm))
                if enable_auto_exit and do_gsi_logging:
                    for (prev_state, state, current_arb_str) in gsi_archive_logs:
                        gsi_handlers.interaction_archive_handlers.add_animation_data(interaction, asm, prev_state, state, current_arb_str)
                if requires_begin_flush:
                    sequence = build_critical_section(sequence, flush_all_animations)
                sequence = build_element(sequence)
                if sequence is not None:
                    result = yield from element_utils.run_child(timeline, sequence)
                else:
                    result = True
                cur_ticks = services.time_service().sim_now.absolute_ticks()
                for (actor_name, (actor, _, _)) in asm._actors.items():
                    actor = actor()
                    if actor is None:
                        pass
                    else:
                        if actor.asm_last_call_time == cur_ticks:
                            actor.zero_length_asm_calls += 1
                        else:
                            actor.zero_length_asm_calls = 0
                        actor.asm_last_call_time = cur_ticks
                        if actor.is_sim and actor.zero_length_asm_calls >= MAX_ZERO_LENGTH_ASM_CALLS_FOR_RESET:
                            raise RuntimeError('ASM {} is being called repeatedly with a zero-length duration.\nInteraction: {}\nPosture: {}\nStates: {} -> {}\n'.format(asm.name, interaction.get_interaction_type(), actor.posture.posture_type, begin_states, end_states))
                return result
            return True

        def do_end(timeline):
            nonlocal all_actors
            arb_end = animation.arb.Arb()
            if do_gsi_logging:
                gsi_archive_logs = []
            if end_states:
                for state in end_states:
                    if do_gsi_logging:
                        prev_state = asm.current_state
                        arb_buffer = arb_end.get_contents_as_string()
                    asm.request(state, arb_end, debug_context=interaction)
                    if do_gsi_logging:
                        arb_end_str = arb_end.get_contents_as_string()
                        current_arb_str = arb_end_str[arb_end_str.find(arb_buffer) + len(arb_buffer):]
                        gsi_archive_logs.append((prev_state, state, current_arb_str))
            actors_end = get_actors_for_arb_sequence(arb_end)
            all_actors = all_actors | actors_end
            if requires_begin_flush or not arb_end.empty:
                sequence = create_run_animation(arb_end)
            else:
                sequence = None
            if asm.current_state == 'exit':
                auto_exit_releases = mark_auto_exit(all_actors, asm)
                if auto_exit_releases is not None:
                    sequence = build_critical_section_with_finally(sequence, auto_exit_releases)
            if sequence:
                auto_exit_element = get_auto_exit(actors_end, asm=asm, interaction=interaction)
                if do_gsi_logging:
                    for (prev_state, state, current_arb_str) in gsi_archive_logs:
                        gsi_handlers.interaction_archive_handlers.add_animation_data(interaction, asm, prev_state, state, current_arb_str)
                if auto_exit_element is not None:
                    sequence = (auto_exit_element, sequence)
                result = yield from element_utils.run_child(timeline, sequence)
                return result
            return True

        if repeat_begin_states:

            def do_soft_stop(timeline):
                loop.trigger_soft_stop()

            loop = elements.RepeatElement(build_element(do_begin))
            sequence = do_all(loop, build_element([sequence, do_soft_stop]))
        sequence = build_element([do_begin, sequence])
        if require_end:
            sequence = build_critical_section(sequence, do_end)
        else:
            sequence = build_element([sequence, do_end])
        sequence = with_audio_awareness(*list(asm.actors_gen()), sequence=sequence)
    if cleanup_asm is not None:
        sequence = build_critical_section_with_finally(sequence, lambda _: cleanup_asm(asm))
    return sequence

class AnimationElement(HasTunableReference, elements.ParentElement, metaclass=TunedInstanceMetaclass, manager=services.animation_manager()):
    ASM_SOURCE = 'asm_key'
    INSTANCE_TUNABLES = {'base_object_name': OptionalTunable(description='\n            ', tunable=Tunable(description='\n                If enabled this allows you to tune which actor is the base object\n                by  name. This is important if the posture target is not the\n                same as the target of the interaction.\n                \n                For example: The massage table has massage interactions that\n                target the other Sim but the massage therapist must route\n                and stand at the massage table. In this case you would need\n                to enable base_object_name and tune it to the name of the \n                actor you want to target with the posture, or in this case\n                massageTable. This is tuned in massageTable_SocialInteractions.\n                ', tunable_type=str, default=None, source_location='../' + ASM_SOURCE, source_query=SourceQueries.ASMActorAll)), 'repeat': Tunable(description='\n            If this is checked, then the begin_states will loop until the\n            controlling sequence (e.g. the interaction) ends. At that point,\n            end_states will play.\n            \n            This tunable allows you to create looping one-shot states. The\n            effects of this tunable on already looping states is undefined.\n            \n            This changes the interpretation of thought balloons. We will\n            trigger one balloon per loop of the animation. The delay on the\n            balloon is relative to the start of each loop rather than the start\n            of the entire sequence.\n            ', tunable_type=bool, default=False, tuning_filter=FilterTag.EXPERT_MODE), 'end_states': TunableList(description="\n             A list of states to run through at the end of this element. This \n             should generally be one of two values:\n             * empty (default), which means to do no requests. This is best if \n             you don't know what to use here, as auto-exit behavior, which \n             automatically requests the 'exit' state on any ASM that is still \n             active, should handle most cases for you. Note: this is not safe \n             for elements that are used as the staging content for SIs! \n             See below!\n             * 'exit', which requests the content on the way out of the \n             statemachine. This is important to set for SuperInteractions that \n             are set to use staging basic content, as auto-exit behavior is \n             disabled in that case. This means the content on the way to exit \n             will be requested as the SI is finishing. You can put additional \n             state requests here if the ASM is more complex, but that is very \n             rare.\n             ", tunable=str, source_location=ASM_SOURCE, source_query=SourceQueries.ASMState), '_overrides': TunableAnimationOverrides(description='\n            Overrides are for expert-level configuration of Animation Elements. \n            In 95% of cases, the animation element will work perfectly with no \n            overrides.\n            Overrides allow us to customize animations further using things \n            like vfx changes and also to account for some edge cases. \n            ', asm_source=ASM_SOURCE, state_source='begin_states'), 'begin_states': TunableList(description='\n             A list of states in the ASM to run through at the beginning of \n             this element. Generally-speaking, you should always use \n             begin_states for all your state requests. The only time you would \n             need end_states is when you are making a staging-SuperInteraction. \n             In that case, the content in begin_states happens when the SI \n             first runs, before it stages, and the content in end_states will \n             happen as the SI is exiting. When in doubt, put all of your state \n             requests here.\n             ', tunable=str, source_location=ASM_SOURCE, source_query=SourceQueries.ASMState), 'initial_state': OptionalTunable(description="\n             The name of the initial state in the ASM to use when begin_states \n             are requested. \n             If this is untuned, which should be the case almost all the time, \n             it will use the default initial state of 'entry'. Ask your \n             animation partner if you think you want to tune this because you \n             should not have to and it is probably best to just change the \n             structure of the ASM. Remember that ASMs are re-used within a \n             single interaction, so if you are defining an outcome animation, \n             you can rely on the state to persist from the basic content.\n             ", tunable=Tunable(tunable_type=str, default=None, source_location='../' + ASM_SOURCE, source_query=SourceQueries.ASMState), disabled_value=DEFAULT, disabled_name='use_default', enabled_name='custom_state_name'), 'create_target_name': Tunable(description="\n            Create Target Name is the actor name of an object that will be \n            created by this interaction. This is used frequently in the \n            crafting system but rarely elsewhere. If your interaction creates \n            an object in the Sim's hand, use this. \n            ", tunable_type=str, default=None, source_location=ASM_SOURCE, source_query=SourceQueries.ASMActorAll), 'carry_target_name': Tunable(description='\n            Carry Target Name is the actor name of the carried object in this \n            ASM. This is only relevant if the Target and Carry Target are \n            different. \n            ', tunable_type=str, default=None, source_location=ASM_SOURCE, source_query=SourceQueries.ASMActorAll), 'target_name': Tunable(description='\n            This determines which actor the target of the interaction will be. \n            In general, this should be the object that will be clicked on to \n            create interactions that use this content.\n            This helps the posture system understand what objects you already \n            know about and which to search for. Sit says its target name is \n            sitTemplate, which means you have to sit in the chair that was \n            clicked on, whereas Eat says its target name is consumable, which \n            means you can sit in any chair in the world to eat. This ends up \n            in the var_map in the runtime. \n            ', tunable_type=str, default=None, source_location=ASM_SOURCE, source_query=SourceQueries.ASMActorAll), 'actor_name': Tunable(description="\n            Actor Name is the name of the main actor for this animation. In \n            almost every case this will just be 'x', so please be absolutely \n            sure you know what you're doing when changing this value.\n            ", tunable_type=str, default='x', source_location=ASM_SOURCE, source_query=SourceQueries.ASMActorSim), ASM_SOURCE: TunableInteractionAsmResourceKey(description='\n            ASM Key is the Animation State Machine to use for this animation. \n            You are selecting from the ASMs that are in your \n            Assets/InGame/Statemachines folder, and several of the subsequent \n            fields are populated by information from this selection. \n            ', default=None, category='asm')}
    _child_animations = None
    _child_constraints = None

    def __init__(self, interaction=UNSET, setup_asm_additional=None, setup_asm_override=DEFAULT, overrides=None, use_asm_cache=True, **animate_kwargs):
        global logged_missing_interaction_callstack
        super().__init__()
        self.interaction = None if interaction is UNSET else interaction
        self.setup_asm_override = setup_asm_override
        self.setup_asm_additional = setup_asm_additional
        if overrides is not None:
            overrides = overrides()
        if interaction is not None:
            if interaction.anim_overrides is not None:
                overrides = interaction.anim_overrides(overrides=overrides)
            if not interaction.is_super:
                super_interaction = self.interaction.super_interaction
                if super_interaction.basic_content.content_set.balloon_overrides is not None:
                    balloons = super_interaction.basic_content.content_set.balloon_overrides
                    overrides = overrides(balloons=balloons)
        self.overrides = self._overrides(overrides=overrides)
        self.animate_kwargs = animate_kwargs
        self._use_asm_cache = use_asm_cache
        if not logged_missing_interaction_callstack:
            logger.callstack('Attempting to set up animation {} with interaction=None.', self, level=sims4.log.LEVEL_ERROR, owner='jpollak')
            logged_missing_interaction_callstack = True

    @classmethod
    def _verify_tuning_callback(cls):
        if cls.begin_states or not cls.end_states:
            logger.error('Animation {} specifies neither begin_states nor end_states. This is not supported.', cls)
        if cls.carry_target_name is not None and cls.create_target_name is not None:
            logger.error('Animation {} has specified both a carry target ({}) and a create target ({}).  This is not supported.', cls, cls.carry_target_name, cls.create_target_name, owner='tastle')

    @flexmethod
    def get_supported_postures(cls, inst):
        if inst is not None and inst.interaction is not None:
            asm = inst.get_asm()
            if asm is not None:
                return asm.get_supported_postures_for_actor(cls.actor_name)
        else:
            overrides = cls._overrides()
            return get_asm_supported_posture(cls.asm_key, cls.actor_name, overrides)
        return PostureManifest()

    @classproperty
    def name(cls):
        return get_asm_name(cls.asm_key)

    @classmethod
    def register_tuned_animation(cls, *args):
        if cls._child_animations is None:
            cls._child_animations = []
        cls._child_animations.append(args)

    @classmethod
    def add_auto_constraint(cls, *args, **kwargs):
        if cls._child_constraints is None:
            cls._child_constraints = []
        cls._child_constraints.append(args)

    def get_asm(self, use_cache=True, **kwargs):
        if not self._use_asm_cache:
            use_cache = False
        if self.overrides.animation_context:
            use_cache = False
        asm = self.interaction.get_asm(self.asm_key, self.actor_name, self.target_name, self.carry_target_name, setup_asm_override=self.setup_asm_override, posture_manifest_overrides=self.overrides.manifests, use_cache=use_cache, create_target_name=self.create_target_name, base_object_name=self.base_object_name, **kwargs)
        if asm is None:
            return
        if self.setup_asm_additional is not None:
            result = self.setup_asm_additional(asm)
            if not result:
                logger.warn('Failed to perform additional asm setup on asm {}. {}', asm, result, owner='rmccord')
        return asm

    @flexmethod
    def append_to_arb(cls, inst, asm, arb):
        if inst is not None:
            balloon_requests = TunableBalloon.get_balloon_requests(inst.interaction, inst.overrides)
            _register_balloon_requests(asm, inst.interaction, inst.overrides, balloon_requests)
        for state_name in cls.begin_states:
            asm.request(state_name, arb)

    @classmethod
    def append_exit_to_arb(cls, asm, arb):
        for state_name in cls.end_states:
            asm.request(state_name, arb)

    def get_constraint(self, participant_type=ParticipantType.Actor):
        from interactions.constraints import Anywhere, create_animation_constraint
        if participant_type == ParticipantType.Actor:
            actor_name = self.actor_name
            target_name = self.target_name
        elif participant_type == ParticipantType.TargetSim:
            actor_name = self.target_name
            target_name = self.actor_name
        else:
            return Anywhere()
        return create_animation_constraint(self.asm_key, actor_name, target_name, self.carry_target_name, self.create_target_name, self.initial_state, self.begin_states, self.end_states, self.overrides)

    @property
    def reactionlet(self):
        if self.overrides is not None:
            return self.overrides.reactionlet

    @classproperty
    def run_in_sequence(cls):
        return True

    @classmethod
    def animation_element_gen(cls):
        yield cls

    def _run(self, timeline):
        global logged_missing_interaction_callstack
        if self.interaction is None:
            if not logged_missing_interaction_callstack:
                logger.callstack('Attempting to run an animation {} without a corresponding interaction.', self, level=sims4.log.LEVEL_ERROR)
                logged_missing_interaction_callstack = True
            return False
        if self.asm_key is None:
            return True
        asm = self.get_asm()
        if asm is None:
            return False
        if self.overrides.balloons:
            balloon_requests = TunableBalloon.get_balloon_requests(self.interaction, self.overrides)
        else:
            balloon_requests = None
        success = timeline.run_child(animate_states(asm, self.begin_states, self.end_states, overrides=self.overrides, balloon_requests=balloon_requests, repeat_begin_states=self.repeat, interaction=self.interaction, **self.animate_kwargs))
        return success

def get_asm_name(asm_key):
    return asm_key

class AnimationElementSet(metaclass=TunedInstanceMetaclass, manager=services.animation_manager()):
    INSTANCE_TUNABLES = {'_animation_and_overrides': TunableList(description='\n            The list of the animations which get played in sequence\n            ', tunable=TunableTuple(anim_element=AnimationElement.TunableReference(pack_safe=True), overrides=TunableAnimationOverrides(), carry_requirements=TunableTuple(description='\n                    Specify whether the Sim must be carrying objects with\n                    specific animation properties in order to animate this\n                    particular element.\n                    ', params=TunableParameterMapping(description='\n                        A carried object must override and match these animation\n                        parameters in order for it to be valid.\n                        '), actor=Tunable(description='\n                        The carried object that fulfills the param requirements\n                        will be set as this actor on the selected element.\n                        ', tunable_type=str, default=None))))}

    def __new__(cls, interaction=None, setup_asm_additional=None, setup_asm_override=DEFAULT, overrides=None, sim=DEFAULT, **animate_kwargs):
        best_supported_posture = None
        best_anim_element_type = None
        best_carry_actor_and_object = None
        for animation_and_overrides in cls._animation_and_overrides:
            if overrides is not None:
                if callable(overrides):
                    overrides = overrides()
                overrides = animation_and_overrides.overrides(overrides=overrides)
            else:
                overrides = animation_and_overrides.overrides()
            anim_element_type = animation_and_overrides.anim_element
            if best_anim_element_type is None:
                best_anim_element_type = anim_element_type
            if interaction is None:
                logger.warn('Attempting to initiate AnimationElementSet {} without interaction, it will just construct the first AnimationElement {}.', cls.name, anim_element_type.name)
                break
            sim = sim if sim is not DEFAULT else interaction.sim
            carry_actor_name = animation_and_overrides.carry_requirements.actor
            if carry_actor_name:
                from carry.carry_utils import get_carried_objects_gen
                for (_, _, carry_object) in get_carried_objects_gen(sim):
                    carry_object_params = carry_object.get_anim_overrides(carry_actor_name).params
                    if all(carry_object_params[k] == v for (k, v) in animation_and_overrides.carry_requirements.params.items()):
                        break
            else:
                postures = anim_element_type.get_supported_postures()
                sim_posture_state = sim.posture_state
                from postures import get_best_supported_posture
                surface_target = MATCH_ANY if sim_posture_state.surface_target is not None else MATCH_NONE
                provided_postures = sim_posture_state.body.get_provided_postures(surface_target=surface_target)
                best_element_supported_posture = get_best_supported_posture(provided_postures, postures, sim_posture_state.get_carry_state(), ignore_carry=False)
                if not best_supported_posture is None:
                    if best_element_supported_posture < best_supported_posture:
                        best_supported_posture = best_element_supported_posture
                        best_anim_element_type = anim_element_type
                        if carry_actor_name:
                            best_carry_actor_and_object = (carry_actor_name, carry_object)
                        else:
                            best_carry_actor_and_object = None
                best_supported_posture = best_element_supported_posture
                best_anim_element_type = anim_element_type
                if carry_actor_name:
                    best_carry_actor_and_object = (carry_actor_name, carry_object)
                else:
                    best_carry_actor_and_object = None
        if best_carry_actor_and_object is not None:
            setup_asm_additional_override = setup_asm_additional

            def setup_asm_additional(asm):
                if not asm.set_actor(best_carry_actor_and_object[0], best_carry_actor_and_object[1], actor_participant=AnimationParticipant.CREATE_TARGET):
                    return TestResult(False, 'Failed to set actor {} for actor name {} on asm {}'.format(best_carry_actor_and_object[0], best_carry_actor_and_object[1], asm))
                else:
                    from carry.carry_utils import set_carry_track_param_if_needed
                    set_carry_track_param_if_needed(asm, sim, best_carry_actor_and_object[0], best_carry_actor_and_object[1])
                    if setup_asm_additional_override is not None:
                        return setup_asm_additional_override(asm)
                return True

        best_anim_element = best_anim_element_type(interaction=interaction, setup_asm_additional=setup_asm_additional, setup_asm_override=setup_asm_override, overrides=overrides, **animate_kwargs)
        return best_anim_element

    @classproperty
    def run_in_sequence(cls):
        return False

    @classmethod
    def animation_element_gen(cls):
        for animation_and_overrides in cls._animation_and_overrides:
            yield animation_and_overrides.anim_element

    @flexmethod
    def get_supported_postures(cls, inst):
        if inst is not None and inst.interaction is not None:
            asm = inst.get_asm()
            if asm is not None:
                return asm.get_supported_postures_for_actor(cls.actor_name)
        supported_postures = PostureManifest()
        for animation_and_overrides in cls._animation_and_overrides:
            supported_postures.update(animation_and_overrides.anim_element.get_supported_postures())
        return supported_postures

    @classproperty
    def name(cls):
        return cls.__name__
