import careers.career_tuning
import interactions
import services
import sims4.log
from animation.arb_accumulator import with_skippable_animation_time
from autonomy.content_sets import ContentSet, ContentSetWithOverrides
from balloon.tunable_balloon import TunableBalloon
from broadcasters.broadcaster_request import BroadcasterRequest
from buffs.buff_element import BuffFireAndForgetElement
from buffs.tunable import TunableBuffElement
from business.business_elements import BusinessBuyLot, BusinessEmployeeAction
from call_to_action.call_to_action_elements import TurnOffCallToAction
from carry.carry_elements import EnterCarryWhileHolding, TransferCarryWhileHolding, TunableExitCarryWhileHolding
from crafting.create_photo_memory import CreatePhotoMemory
from crafting.set_photo_filter import SetPhotoFilter
from crafting.take_photo import TakePhoto
from drama_scheduler.festival_contest_ops import FestivalContestSubmitElement
from ensemble.ensemble_ops import AddToEnsemble, DestroyEnsemble, RemoveFromEnsemble
from familiars.familiar_elments import BindFamiliarElement, DismissFamiliarElement
from interactions import ParticipantType
from interactions.payment.payment_element import PaymentElement
from interactions.push_affordance_on_parent import PushAffordanceOnRandomParent
from interactions.push_npc_leave_lot_now import PushNpcLeaveLotNowInteraction
from interactions.utils.adventure import Adventure
from interactions.utils.animation_reference import TunableAnimationReference
from interactions.utils.audio import TunableAudioModificationElement, TunableAudioSting, TunablePlayStoredAudioFromSource
from interactions.utils.camera import CameraFocusElement, SetWallsUpOverrideElement
from interactions.utils.creation import ObjectCreationElement, SimCreationElement
from interactions.utils.destruction import ObjectDestructionElement
from interactions.utils.filter_elements import InviteSimElement
from interactions.utils.interaction_elements import AddToHouseholdElement, FadeChildrenElement, ParentObjectElement, PutNearElement, ReplaceObject, SaveParticipantElement, SetVisibilityStateElement, UpdateDisplayNumber, UpdatePhysique
from interactions.utils.life_event import TunableLifeEventElement
from interactions.utils.loot_element import LootElement
from interactions.utils.notification import NotificationElement
from interactions.utils.plumbbob import TunableReslotPlumbbob
from interactions.utils.reactions import ReactionTriggerElement
from interactions.utils.routing_elements import RouteToLocationElement
from interactions.utils.sim_focus import TunableFocusElement
from interactions.utils.statistic_element import ConditionalActionRestriction, ConditionalInteractionAction, PeriodicStatisticChangeElement, TunableExitConditionSnippet, TunableProgressiveStatisticChangeElement, TunableStatisticDecayByCategory, TunableStatisticIncrementDecrement, TunableStatisticTransferRemove
from interactions.utils.tunable import DoCommand, ServiceNpcRequest, SetGoodbyeNotificationElement, TunableSetClockSpeed, TunableSetSimSleeping
from interactions.utils.visual_effect import PlayVisualEffectElement
from lot_decoration.lot_decoration_elements import LotDecorationElement
from notebook.notebook_entry_elements import NotebookDisplayElement
from objects.components.autonomy import TunableParameterizedAutonomy
from objects.components.canvas_component import PaintingStateTransfer, UpdateFamilyPortrait, UpdateObjectValue
from objects.components.footprint_component import TunableFootprintToggleElement
from objects.components.game.game_element_join import GameElementJoin
from objects.components.game_component import TunableSetGameTarget
from objects.components.inventory_elements import DeliverBill, DestroySpecifiedObjectsFromTargetInventory, InventoryTransfer, PutObjectInMail
from objects.components.name_component import NameTransfer
from objects.components.object_relationship_social import ObjectRelationshipSocialTrigger
from objects.components.state import TunableStateChange, TunableTransienceChange
from objects.components.stolen_component import MarkObjectAsStolen, ReturnStolenObject
from objects.components.stored_audio_component import TransferStoredAudioComponent
from objects.components.stored_sim_info_component import StoreSimElement
from objects.household_inventory_management import SendToInventory
from objects.parenting_utils import SetAsHeadElement
from objects.slot_elements import SlotItemTransfer, SlotObjectsFromInventory
from open_street_director.open_street_director_element import ManipulateConditionalLayer
from postures.set_posture_element import SetPosture
from rabbit_hole.rabbit_hole_element import RabbitHoleElement
from relationships.relationship_bit_change import TunableRelationshipBitElement
from retail.retail_elements import RetailCustomerAction
from routing.formation.formation_element import RoutingFormationElement
from routing.route_events.route_event_provider import RouteEventProviderRequest
from sickness.sickness_elements import TrackDiagnosticAction
from sims.aging.aging_element import ChangeAgeElement
from sims.occult.switch_occult_element import SwitchOccultElement
from sims.outfits.outfit_change_element import ChangeOutfitElement
from sims.pregnancy.pregnancy_element import PregnancyElement
from sims.royalty_tracker import TunableRoyaltyPayment
from sims.university.university_elements import UniversityEnrollmentElement
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory, OptionalTunable, Tunable, TunableEnumEntry, TunableFactory, TunableList, TunableReference, TunableTuple, TunableVariant
from sims4.tuning.tunable_base import FilterTag
from singletons import DEFAULT
from situations.tunable import CreateSituationElement, DestroySituationsByTagsElement, JoinSituationElement, LeaveSituationElement, TunableMakeNPCLeaveMustRun, TunableSummonNpc, TunableUserAskNPCToLeave
from trends.trend_recording import RecordTrendsElement
from world.dynamic_spawn_point import DynamicSpawnPointElement
from world.travel_group_elements import TravelGroupAdd, TravelGroupEnd, TravelGroupExtend, TravelGroupRemove

logger = sims4.log.Logger('Basic')
AFFORDANCE_LOADED_CALLBACK_STR = 'on_affordance_loaded_callback'

class _BasicContent(HasTunableSingletonFactory, AutoFactoryInit):
	animation_ref = None
	periodic_stat_change = None
	progressive_stat_change = None
	statistic_reduction_by_category = None
	conditional_actions = None
	start_autonomous_inertial = False
	start_user_directed_inertial = False
	staging = False
	sleeping = False
	content_set = None
	FACTORY_TUNABLES = {
		'allow_holster': OptionalTunable(description = '\n            If enabled, specify an override as to whether or not this\n            interaction allows holstering. If left unspecified, then only\n            staging interactions will allow holstering.\n            \n            For example: a one-shot interaction where the Grim Reaper dooms a\n            Sim disallows carry. Normally, the Grim Reaper would be unable to\n            holster his scythe. We override holstering to be allowed such that\n            the scythe can indeed be holstered.\n            ', tunable = Tunable(description = '\n                Whether or not holstering is explicitly allowed or not.\n                ', tunable_type = bool, default = True), disabled_name = 'use_default', enabled_name = 'override'),
		'route_to_location': OptionalTunable(description = "\n            If enabled, this will force the Sim to route to a particular set of\n            constraints. This will occur between the animation's begin and end\n            states.\n            ", tunable = RouteToLocationElement.TunableFactory()),
		'allow_with_unholsterable_object': OptionalTunable(
			description = '\n            If enabled, specify an override to the default behavior for this\n            interaction when carrying an object that is tuned to be\n            unholsterable (e.g. a toddler or a puppy).\n            \n            By default:\n             * Mixer interactions have this set to True. So, unless overridden,\n             a mixer is allowed to execute normally when carrying an\n             unholsterable object. The Sim will continue the carry and execute\n             the mixer. If unchecked, the Sim will put the object down before\n             running the mixer.\n             \n             * Super interactions have this set to False. So, unless overridden,\n             a super interaction is not allowed to execute (or will cancel the\n             carry) when carrying an unholsterable object.\n             \n            e.g.\n             * Warm Hands at Fireplace. This is a super interaction. When\n             carrying a toddler, for example, we want to the Sim to execute the\n             interaction and mask the animation. So we override this value and\n             set it to True.\n              \n             * Tell Joke about Fashion. This is a mixer interaction whose\n             animation does not read if unable to use the hands. We override\n             this so Sims put down toddlers before running it.\n            ',
			tunable = Tunable(description = '\n                Whether or not this interaction is allowed to execute when\n                carrying an incompatible, unholsterable object.\n                ', tunable_type = bool, default = True), disabled_name = 'use_default', enabled_name = 'override')
	}

	def __call__ (self, interaction, sequence = (), **kwargs):
		if self.route_to_location is not None:
			sequence = self.route_to_location(interaction, sequence = sequence)
		actor_or_object_target = interaction.target_type & interactions.TargetType.ACTOR or interaction.target_type & interactions.TargetType.OBJECT
		last_affordance_is_affordance = not interaction.simless and interaction.sim.last_affordance is interaction.affordance
		if self.animation_ref is not None:
			animation_sequence = self.animation_ref(interaction, sequence = sequence, **kwargs)
			last_affordance_is_affordance = interaction.sim.last_animation_factory == self.animation_ref.factory
		if actor_or_object_target and (last_affordance_is_affordance and not interaction.is_super) and not not (self.sleeping == True and self.animation_ref is not None and animation_sequence.repeat):
			skip_animation = interaction.sim.asm_auto_exit.asm is not None
		else:
			skip_animation = False
		if self.animation_ref is not None and not skip_animation:
			sequence = animation_sequence
		if self.periodic_stat_change is not None:
			sequence = self.periodic_stat_change(interaction, sequence = sequence)
		if self.progressive_stat_change is not None:
			sequence = self.progressive_stat_change(interaction, sequence = sequence)
		if self.statistic_reduction_by_category is not None:
			sequence = self.statistic_reduction_by_category(interaction, sequence = sequence)
		if self.sleeping:
			if self.animation_ref is not None:
				if not animation_sequence.repeat:
					sequence = with_skippable_animation_time((interaction.sim,), sequence = sequence)
		return sequence

	def validate_tuning (self, interaction):
		pass

class NoContent(_BasicContent):
	start_autonomous_inertial = True
	start_user_directed_inertial = True

class OneShotContent(_BasicContent):

	@TunableFactory.factory_option
	def animation_callback (callback = DEFAULT):
		return {
			'animation_ref': TunableAnimationReference(description = ' \n                A non-looping animation reference.\n                ', callback = callback, allow_none = True),
			'periodic_stat_change': OptionalTunable(description = '\n                Statistic changes tuned to occur every specified interval.\n                ', tunable = PeriodicStatisticChangeElement.TunableFactory())
		}

class _FlexibleLengthContent(_BasicContent):
	FACTORY_TUNABLES = {
		'progressive_stat_change': OptionalTunable(description = '\n            Statistic changes tuned to change a certain amount over the course\n            of an interaction.\n            ', tunable = TunableProgressiveStatisticChangeElement()),
		'periodic_stat_change': OptionalTunable(description = '\n            Statistic changes tuned to occur every specified interval.\n            ', tunable = PeriodicStatisticChangeElement.TunableFactory()),
		'statistic_reduction_by_category': OptionalTunable(description = '\n            Increase the decay of some commodities over time.\n            Useful for removing a category of buffs from a Sim.', tunable = TunableStatisticDecayByCategory()),
		'conditional_actions': TunableList(description = '\n            A list of conditional actions for this interaction. Conditional\n            actions are behavior, such as giving loot and canceling interaction,\n            that trigger based upon a condition or list of conditions, e.g. \n            time or a commodity hitting a set number.\n            \n            Example behavior that can be accomplished with this:\n            - Guarantee a Sim will play with a doll for 30 minutes.\n            - Stop the interaction when the object breaks.\n            ', tunable = TunableExitConditionSnippet(pack_safe = True)),
		'start_autonomous_inertial': Tunable(bool, True, needs_tuning = True,
											 description = '\n            Inertial interactions will run only for as long autonomy fails to\n            find another interaction that outscores it. As soon as a higher-\n            scoring interaction is found, the inertial interaction is canceled\n            and the other interaction runs.\n            \n            The opposite of inertial is guaranteed. A guaranteed interaction\n            will never be displaced by autonomy, even if there are higher\n            scoring interactions available to the Sim.\n\n            This option controls which mode the interaction starts in if\n            autonomy starts it. If started guaranteed, this interaction can be\n            set back to inertial with a conditional action.\n            \n            Please use this with care. If an interaction starts guaranteed but\n            nothing ever sets the interaction back to inertial or otherwise end\n            the interaction, this interaction will never end without direct\n            user intervention.\n            '),
		'start_user_directed_inertial': Tunable(bool, False, needs_tuning = True,
												description = '\n            Inertial interactions will run only for as long autonomy fails to\n            find another interaction that outscores it. As soon as a higher-\n            scoring interaction is found, the inertial interaction is canceled\n            and the other interaction runs.\n            \n            The opposite of inertial is guaranteed. A guaranteed interaction\n            will never be displaced by autonomy, even if there are higher\n            scoring interactions available to the Sim.\n\n            This option controls which mode the interaction starts in if the\n            user starts it. If started guaranteed, this interaction can be\n            set back to inertial with a conditional action.\n            \n            Please use this with care. If an interaction starts guaranteed but\n            nothing ever sets the interaction back to inertial or otherwise end\n            the interaction, this interaction will never end without direct\n            user intervention.\n            ')
	}

class _LoopingContentBase(HasTunableSingletonFactory, AutoFactoryInit):
	sleeping = True

	@TunableFactory.factory_option
	def animation_callback (callback = DEFAULT):
		return {
			'animation_ref': TunableAnimationReference(description = ' \n                A looping animation reference.\n                ', callback = callback, allow_none = True, reload_dependent = True)
		}

class LoopingContent(_LoopingContentBase, _FlexibleLengthContent):

	def validate_tuning (self, interaction):
		if not self.start_autonomous_inertial:
			for conditional_action in self.conditional_actions:
				if conditional_action.restrictions != ConditionalActionRestriction.USER_DIRECTED_ONLY:
					if conditional_action.interaction_action != ConditionalInteractionAction.NO_ACTION:
						break
			else:
				logger.error("Interaction {} has looping content that has no way to end. Autonomously, it doesn't start inertial, and it has no conditional action for exiting or going inertial.", interaction, owner = 'tingyul')
		if not self.start_user_directed_inertial:
			for conditional_action in self.conditional_actions:
				if conditional_action.restrictions != ConditionalActionRestriction.AUTONOMOUS_ONLY:
					if conditional_action.interaction_action != ConditionalInteractionAction.NO_ACTION:
						break
			else:
				logger.error("Interaction {} has looping content that has no way to end. User directed, it doesn't start inertial, and it has no conditional action for exiting or going inertial.", interaction, owner = 'tingyul')

class _StagingContentBase(HasTunableSingletonFactory, AutoFactoryInit):
	staging = True

	@TunableFactory.factory_option
	def animation_callback (callback = DEFAULT):
		return {
			'animation_ref': OptionalTunable(TunableAnimationReference(description = ' \n                A non-looping animation reference.\n                ', callback = callback, allow_none = True, reload_dependent = True))
		}

	FACTORY_TUNABLES = {
		'content_set': lambda: ContentSetWithOverrides.TunableFactory(),
		'push_affordance_on_run': OptionalTunable(TunableTuple(actor = TunableEnumEntry(description = '\n                        The participant of this interaction that is going to have\n                        the specified affordance pushed upon them.\n                        ', tunable_type = ParticipantType, default = ParticipantType.Actor), target = OptionalTunable(description = "\n                        If enabled, specify a participant to be used as the\n                        interaction's target.\n                        ", tunable = TunableEnumEntry(description = "\n                            The participant to be used as the interaction's\n                            target.\n                            ", tunable_type = ParticipantType, default = ParticipantType.Object), enabled_by_default = True),
															   carry_target = OptionalTunable(description = "\n                        If enabled, specify a participant to be used as the\n                        interaction's carry target.\n                        If disabled carry_target will be set to None.\n                        ", tunable = TunableEnumEntry(description = "\n                            The participant to be used as the interaction's\n                            carry target.\n                            ", tunable_type = ParticipantType, default = ParticipantType.Object), disabled_name = 'No_carry_target'),
															   affordance = TunableReference(description = '\n                        When this interaction is run, the tuned affordance will be\n                        pushed if possible. \n                        \n                        e.g: when Stereo dance is run, we also push the listen to\n                        music interaction\n                        ', manager = services.get_instance_manager(sims4.resources.Types.INTERACTION)), link_cancelling_to_affordance = Tunable(description = '\n                        If True, when the above tuned affordance is cancelled, This\n                        interaction will cancel too. \n                        \n                        e.g.: When sim is dancing and listening to music, if the\n                        listen to music interaction is cancelled, the dance will\n                        cancel too.\n                        ', tunable_type = bool, default = True))),
		'post_stage_autonomy_commodities': TunableList(description = '\n                An ordered list of parameterized autonomy requests to run when\n                this interaction has staged.\n                ', tunable = TunableParameterizedAutonomy()),
		'only_use_mixers_from_SI': Tunable(description = '\n                If checked then sub-action autonomy will only use mixers from\n                this SI.\n                ', tunable_type = bool, default = False)
	}

class StagingContent(_StagingContentBase, _FlexibleLengthContent):
	EMPTY = _StagingContentBase(animation_ref = None, content_set = ContentSet.EMPTY_LINKS, push_affordance_on_run = None, post_stage_autonomy_commodities = (), only_use_mixers_from_SI = False)

class FlexibleLengthContent(_FlexibleLengthContent):

	@TunableFactory.factory_option
	def animation_callback (callback = DEFAULT):
		return {
			'content': TunableVariant(staging_content = _StagingContentBase.TunableFactory(animation_callback = callback), looping_content = _LoopingContentBase.TunableFactory(animation_callback = callback), default = 'staging_content')
		}

	CONTENT_OVERRIDES = ('animation_ref', 'push_affordance_on_run', 'post_stage_autonomy_commodities', 'only_use_mixers_from_SI', 'staging', 'sleeping', 'content_set')

	def __getattribute__ (self, name):
		if name in FlexibleLengthContent.CONTENT_OVERRIDES:
			content = object.__getattribute__(self, 'content')
			try:
				return object.__getattribute__(content, name)
			except AttributeError:
				return object.__getattribute__(self, name)
		return object.__getattribute__(self, name)

class TunableBasicContentSet(TunableVariant):

	def __init__ (self, default = None, no_content = False, one_shot = False, looping_animation = False, flexible_length = False, animation_callback = DEFAULT, description = None, **kwargs):
		options = { }
		if one_shot is True:
			options['one_shot'] = OneShotContent.TunableFactory(animation_callback = (animation_callback,))
		if looping_animation is True:
			options['looping_animation'] = LoopingContent.TunableFactory(animation_callback = (animation_callback,), locked_args = {
				'start_autonomous_inertial': False,
				'start_user_directed_inertial': False
			}, tuning_filter = FilterTag.EXPERT_MODE)
		if flexible_length is True:
			options['flexible_length'] = FlexibleLengthContent.TunableFactory(animation_callback = (animation_callback,))
		if no_content is True:
			options['no_content'] = NoContent.TunableFactory()
		if default is not None:
			options['default'] = default
		kwargs.update(options)
		super().__init__(description = description, **kwargs)

class BasicExtraVariantCore(TunableVariant):

	def __init__ (self, **kwargs):
		super().__init__(add_to_ensemble = AddToEnsemble.TunableFactory(),
						 add_to_household = AddToHouseholdElement.TunableFactory(),
						 add_to_travel_group = TravelGroupAdd.TunableFactory(),
						 adventure = Adventure.TunableFactory(),
						 audio_modification = TunableAudioModificationElement(),
						 audio_sting = TunableAudioSting.TunableFactory(),
						 balloon = TunableBalloon(),
						 broadcaster = BroadcasterRequest.TunableFactory(),
						 buff = TunableBuffElement(),
						 buff_fire_and_forget = BuffFireAndForgetElement.TunableFactory(),
						 business_buy_lot = BusinessBuyLot.TunableFactory(),
						 business_employee_action = BusinessEmployeeAction.TunableFactory(),
						 call_to_action_turn_off = TurnOffCallToAction.TunableFactory(),
						 camera_focus = CameraFocusElement.TunableFactory(),
						 career_selection = careers.career_tuning.CareerSelectElement.TunableFactory(),
						 change_age = ChangeAgeElement.TunableFactory(),
						 change_outfit = ChangeOutfitElement.TunableFactory(),
						 conditional_layer = ManipulateConditionalLayer.TunableFactory(),
						 create_object = ObjectCreationElement.TunableFactory(),
						 create_photo_memory = CreatePhotoMemory.TunableFactory(),
						 create_sim = SimCreationElement.TunableFactory(),
						 create_situation = CreateSituationElement.TunableFactory(),
						 deliver_bill = DeliverBill.TunableFactory(),
						 destroy_ensemble = DestroyEnsemble.TunableFactory(),
						 destroy_object = ObjectDestructionElement.TunableFactory(),
						 destroy_situations_by_tags = DestroySituationsByTagsElement.TunableFactory(),
						 destroy_specified_objects_from_target_inventory = DestroySpecifiedObjectsFromTargetInventory.TunableFactory(),
						 display_notebook_ui = NotebookDisplayElement.TunableFactory(),
						 do_command = DoCommand.TunableFactory(),
						 dynamic_spawn_point = DynamicSpawnPointElement.TunableFactory(),
						 end_vacation = TravelGroupEnd.TunableFactory(),
						 exit_carry_while_holding = TunableExitCarryWhileHolding(),
						 extend_vacation = TravelGroupExtend.TunableFactory(),
						 enter_carry_while_holding = EnterCarryWhileHolding.TunableFactory(),

						 fade_children = FadeChildrenElement.TunableFactory(),
						 familiar_bind = BindFamiliarElement.TunableFactory(),
						 familiar_dismiss = DismissFamiliarElement.TunableFactory(),
						 focus = TunableFocusElement(),
						 inventory_transfer = InventoryTransfer.TunableFactory(),
						 invite = InviteSimElement.TunableFactory(),
						 join_situation = JoinSituationElement.TunableFactory(),
						 leave_situation = LeaveSituationElement.TunableFactory(),
						 loot = LootElement.TunableFactory(),
						 lot_decoration = LotDecorationElement.TunableFactory(),
						 life_event = TunableLifeEventElement(),
						 mark_object_as_stolen = MarkObjectAsStolen.TunableFactory(),
						 notification = NotificationElement.TunableFactory(),
						 npc_summon = TunableSummonNpc(),
						 object_relationship_social = ObjectRelationshipSocialTrigger.TunableFactory(),
						 painting_state_transfer = PaintingStateTransfer.TunableFactory(),
						 parent_object = ParentObjectElement.TunableFactory(),
						 payment = PaymentElement.TunableFactory(),

						 play_stored_audio_from_source = TunablePlayStoredAudioFromSource.TunableFactory(),
						 pregnancy = PregnancyElement.TunableFactory(),
						 put_near = PutNearElement.TunableFactory(),
						 put_object_in_mail = PutObjectInMail.TunableFactory(),
						 put_sim_in_rabbit_hole = RabbitHoleElement.TunableFactory(),
						 record_trends = RecordTrendsElement.TunableFactory(),
						 remove_from_ensemble = RemoveFromEnsemble.TunableFactory(),
						 remove_from_travel_group = TravelGroupRemove.TunableFactory(),
						 replace_object = ReplaceObject.TunableFactory(),
						 retail_customer_action = RetailCustomerAction.TunableFactory(),
						 return_stolen_object = ReturnStolenObject.TunableFactory(),
						 route_events = RouteEventProviderRequest.TunableFactory(),
						 routing_formation = RoutingFormationElement.TunableFactory(),
						 royalty_payment = TunableRoyaltyPayment.TunableFactory(),
						 save_participant = SaveParticipantElement.TunableFactory(),
						 send_to_inventory = SendToInventory.TunableFactory(),

						 service_npc_request = ServiceNpcRequest.TunableFactory(),
						 set_as_head = SetAsHeadElement.TunableFactory(),
						 set_game_speed = TunableSetClockSpeed.TunableFactory(),
						 set_goodbye_notification = SetGoodbyeNotificationElement.TunableFactory(),
						 set_photo_filter = SetPhotoFilter.TunableFactory(),
						 set_posture = SetPosture.TunableFactory(),
						 set_visibility_state = SetVisibilityStateElement.TunableFactory(),
						 slot_objects_from_inventory = SlotObjectsFromInventory.TunableFactory(),
						 slot_item_transfer = SlotItemTransfer.TunableFactory(),
						 stat_transfer_remove = TunableStatisticTransferRemove(),
						 state_change = TunableStateChange(),
						 store_sim = StoreSimElement.TunableFactory(),
						 submit_to_festival_contest = FestivalContestSubmitElement.TunableFactory(),
						 switch_occult = SwitchOccultElement.TunableFactory(),
						 take_photo = TakePhoto.TunableFactory(),
						 track_diagnostic_action = TrackDiagnosticAction.TunableFactory(),

						 transfer_carry_while_holding = TransferCarryWhileHolding.TunableFactory(),
						 transfer_name = NameTransfer.TunableFactory(),
						 transfer_stored_audio_component = TransferStoredAudioComponent.TunableFactory(),
						 transience_change = TunableTransienceChange(),
						 trigger_reaction = ReactionTriggerElement.TunableFactory(),
						 university_enrollment_ui = UniversityEnrollmentElement.TunableFactory(),
						 update_family_portrait = UpdateFamilyPortrait.TunableFactory(),
						 update_object_value = UpdateObjectValue.TunableFactory(),
						 update_physique = UpdatePhysique.TunableFactory(),
						 update_display_number = UpdateDisplayNumber.TunableFactory(),
						 walls_up_override = SetWallsUpOverrideElement.TunableFactory(),
						 vfx = PlayVisualEffectElement.TunableFactory(),
						 **kwargs)

class BasicExtraVariant(BasicExtraVariantCore):

	def __init__ (self, **kwargs):
		super().__init__(footprint_toggle = TunableFootprintToggleElement(), join_game = GameElementJoin.TunableFactory(), put_npc_in_leave_now_must_run_situation = TunableMakeNPCLeaveMustRun(), relationship_bit = TunableRelationshipBitElement(), reslot_plumbbob = TunableReslotPlumbbob(), set_game_target = TunableSetGameTarget(), set_sim_sleeping = TunableSetSimSleeping(), stat_increment_decrement = TunableStatisticIncrementDecrement(), user_ask_npc_to_leave = TunableUserAskNPCToLeave(), push_affordance_on_random_parent = PushAffordanceOnRandomParent.TunableFactory(), push_leave_lot_interaction = PushNpcLeaveLotNowInteraction.TunableFactory(), **kwargs)

BASIC_EXTRA_DESCRIPTION = "\n    Basic extras add additional non-periodic behavior to an interaction.\n    Elements in this list come in two kinds: ones that act once and ones\n    that do something at the beginning and end of an interaction.\n    \n    The first kind generally causes a discrete change in the world at a\n    specified moment. Most of these tunables give you the option of\n    specifying the moment in time when the behavior should trigger,\n    usually at the beginning of the interaction, the end of the\n    interaction, or on an xevent.\n    \n    The other kind of element is one that starts some modifying behavior\n    which ends at the end of the interaction.  These do things like\n    modify the Sim's focus or modify audio properties.\n    \n    The order of the elements you add to this list does matter: the\n    elements that come earlier in the list surround the behavior of\n    elements that come later.  In most cases this order isn't\n    significant, but it is possible that one element could depend on the\n    behavior of another having already occurred.  Consult a GPE if you\n    aren't sure.\n    \n    e.g. You want a sound modifier to be in effect while running this\n    interaction, and while the sound is playing, you want the Sim's\n    focus to be affected:\n     * add an 'audio_modification' element\n     * add a 'focus' element\n     \n    In this case, the audio_modification element will start before the\n    focus one, and it will end after the focus one.  (This example is\n    somewhat contrived since both the beginning and ending of both\n    elements will happen on the same frame so the order doesn't actually\n    matter.)\n         \n    e.g. You want an object state to change at a particular xevent, such\n    as a toilet becoming flushed when the Sim touches the handle:\n     * add a 'state' element, using the xevent id agreed on in the DR or\n       IR to fill in the timing.\n    "

class TunableBasicExtrasCore(TunableList):

	def __init__ (self, description = BASIC_EXTRA_DESCRIPTION, **kwargs):
		super().__init__(description = description, tunable = BasicExtraVariantCore(), **kwargs)

class TunableBasicExtras(TunableList):

	def __init__ (self, description = BASIC_EXTRA_DESCRIPTION, **kwargs):
		super().__init__(description = description, tunable = BasicExtraVariant(), **kwargs)
