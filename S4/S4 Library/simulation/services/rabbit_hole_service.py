from protocolbuffers import GameplaySaveData_pb2
from date_and_time import TimeSpan
from distributor.rollback import ProtocolBufferRollback
from event_testing.test_events import TestEvent
from filters.sim_filter_service import SimFilterGlobalBlacklistReason
from interactions import ParticipantTypeSingle
from interactions.context import InteractionContext, QueueInsertStrategy
from interactions.priority import Priority
from interactions.utils.exit_condition_manager import ConditionalActionManager
from interactions.utils.interaction_elements import XevtTriggeredElement
from objects import ALL_HIDDEN_REASONS
from sims.sim_spawner import SimSpawner
from sims4 import random
from sims4.callback_utils import CallableList
from sims4.service_manager import Service
from sims4.tuning.tunable import TunablePackSafeReference, TunableEnumEntry, HasTunableFactory, AutoFactoryInit, TunableReference
from sims4.utils import classproperty
import alarms
import date_and_time
import persistence_error_types
import services
import sims4
logger = sims4.log.Logger('Rabbit Hole Service', default_owner='rrodgers')

class RabbitHoleElement(XevtTriggeredElement, HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'rabbit_holed_participant': TunableEnumEntry(description='\n            The participant to place in the rabbit hole.\n            ', tunable_type=ParticipantTypeSingle, default=ParticipantTypeSingle.Actor), 'rabbit_hole': TunablePackSafeReference(description='\n            Rabbit hole to create\n            ', manager=services.get_instance_manager(sims4.resources.Types.RABBIT_HOLE))}

    def _do_behavior(self):
        if self.rabbit_hole is None:
            return
        sim_or_sim_info = self.interaction.get_participant(self.rabbit_holed_participant)
        services.get_rabbit_hole_service().put_sim_in_managed_rabbithole(sim_or_sim_info.sim_info, self.rabbit_hole)

class RabbitHoleService(Service):
    LEAVE_EARLY_INTERACTION = TunableReference(description='\n        The interaction that causes a sim to leave their rabbit hole early\n        ', manager=services.get_instance_manager(sims4.resources.Types.INTERACTION), class_restrictions='RabbitHoleLeaveEarlyInteraction')

    def __init__(self):
        self._rabbit_holes = {}
        self._conditional_actions_manager = ConditionalActionManager()

    @classproperty
    def save_error_code(cls):
        return persistence_error_types.ErrorCodes.SERVICE_SAVE_FAILED_RABBIT_HOLE_SERVICE

    def put_sim_in_managed_rabbithole(self, sim_info, rabbit_hole_type):
        rabbit_hole_affordance = rabbit_hole_type.affordance
        go_home_affordance = rabbit_hole_type.go_home_and_attend
        away_action = rabbit_hole_type.away_action
        if sim_info.is_instanced(allow_hidden_flags=ALL_HIDDEN_REASONS):
            if sim_info.is_at_home:
                result = self._push_affordance(sim_info.id, rabbit_hole_affordance)
                if not result:
                    return
                self._register_callback_for_cancel(sim_info, rabbit_hole_affordance)
                self._register_for_away_action_at_start_of_interaction(rabbit_hole_affordance)
            else:
                result = self._push_affordance(sim_info.id, go_home_affordance)
                self._register_callback_for_cancel(sim_info, go_home_affordance, is_travel_affordance=True)
                if not result:
                    return
                self._register_for_away_action_at_end_of_interaction(sim_info, go_home_affordance, away_action)
        elif not sim_info.is_at_home:
            self._move_sim_home_and_setup(sim_info, rabbit_hole_affordance, away_action)
        else:
            self._set_up_away_action(sim_info, away_action)
        tuned_minutes = 0
        for conditional_action in rabbit_hole_affordance.basic_content.conditional_actions:
            for condition in conditional_action.conditions:
                min_time = condition._tuned_values.min_time
                max_time = condition._tuned_values.max_time
                tuned_minutes = random.uniform(min_time, max_time)
        time = date_and_time.create_time_span(minutes=tuned_minutes)
        self._store_rabbit_hole(sim_info.id, rabbit_hole_type, time)
        self._add_sim_to_blacklist(sim_info.id)
        self._attach_exit_conditions(sim_info.id)
        return True

    def set_rabbit_hole_expiration_callback(self, sim_info, callback):
        sim_id = sim_info.id
        if sim_id in self._rabbit_holes:
            self._rabbit_holes[sim_id].callbacks.register(callback)
        else:
            logger.error('Tried to setup a callback: {} for an invalid sim_id: {} in rabbit hole service.', callback, sim_id)

    def remove_rabbit_hole_expiration_callback(self, sim_info, callback):
        sim_id = sim_info.id
        if sim_id not in self._rabbit_holes:
            logger.error('Trying to remove a callback: {} that does not exist for sim: {} in rabbit hole service.', callback, sim_id)
            return
        self._rabbit_holes[sim_id].callbacks.unregister(callback)

    def set_ignore_travel_cancel_for_sim_id_in_rabbit_hole(self, sim_id):
        self._rabbit_holes[sim_id].ignore_travel_cancel_callbacks = True

    def should_override_selector_visual_type(self, sim_info):
        return self.is_in_rabbit_hole(sim_info.id)

    def is_rabbit_hole_user_cancelable(self, sim_id):
        return self._rabbit_holes[sim_id].affordance.never_user_cancelable

    def will_override_spin_up_action(self, sim_info):
        return self.is_in_rabbit_hole(sim_info.id)

    def get_time_for_rabbit_hole(self, interaction):
        sim_id = interaction.sim.sim_info.id
        if sim_id in self._rabbit_holes:
            return self._rabbit_holes[sim_id].alarm_handle.get_remaining_time()

    def restore_rabbit_hole_state(self):
        for (sim_id, rabbit_hole) in self._rabbit_holes.items():
            sim_info = services.sim_info_manager().get(sim_id)
            if sim_info is None:
                self._rabbit_holes[sim_id].alarm_handle.cancel()
                del self._rabbit_holes[sim_id]
            elif sim_info.is_instanced(allow_hidden_flags=ALL_HIDDEN_REASONS):
                result = self._push_affordance(sim_id, rabbit_hole.affordance)
                if not result:
                    continue
                self._register_callback_for_cancel(sim_info, rabbit_hole.affordance)
                self._set_up_away_action(sim_info, rabbit_hole.away_action)
            elif not sim_info.is_at_home:
                self._move_sim_home_and_setup(sim_info, rabbit_hole.affordance, rabbit_hole.away_action)
            else:
                self._set_up_away_action(sim_info, rabbit_hole.away_action)
            self._add_sim_to_blacklist(sim_id)
            self._attach_exit_conditions(sim_info.id)

    def save(self, save_slot_data=None, **kwargs):
        rabbit_hole_service_proto = GameplaySaveData_pb2.PersistableRabbitHoleService()
        for (sim_id, rabbit_hole) in self._rabbit_holes.items():
            with ProtocolBufferRollback(rabbit_hole_service_proto.rabbit_holes) as entry:
                entry.sim_id = sim_id
                entry.rabbit_hole_id = rabbit_hole.guid64
                entry.time_remaining = rabbit_hole.alarm_handle.get_remaining_time().in_ticks()
        save_slot_data.gameplay_data.rabbit_hole_service = rabbit_hole_service_proto

    def load(self, **_):
        save_slot_data = services.get_persistence_service().get_save_slot_proto_buff()
        for entry in save_slot_data.gameplay_data.rabbit_hole_service.rabbit_holes:
            sim_id = entry.sim_id
            rabbit_hole_id = entry.rabbit_hole_id
            rabbit_hole_type = services.get_instance_manager(sims4.resources.Types.RABBIT_HOLE).get(rabbit_hole_id)
            if rabbit_hole_type is None:
                continue
            ticks = entry.time_remaining
            time = TimeSpan(ticks)
            self._store_rabbit_hole(sim_id, rabbit_hole_type, time)

    def _add_sim_to_blacklist(self, sim_id):
        sim_filter_service = services.sim_filter_service()
        sim_filter_service.add_sim_id_to_global_blacklist(sim_id, SimFilterGlobalBlacklistReason.RABBIT_HOLE)

    def _remove_sim_from_blacklist(self, sim_id):
        sim_filter_service = services.sim_filter_service()
        if sim_id in sim_filter_service.get_global_blacklist():
            sim_filter_service.remove_sim_id_from_global_blacklist(sim_id, SimFilterGlobalBlacklistReason.RABBIT_HOLE)

    def is_in_rabbit_hole(self, sim_id):
        return sim_id in self._rabbit_holes

    def _push_affordance(self, sim_id, affordance):
        sim = services.sim_info_manager().get(sim_id).get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
        context = InteractionContext(sim, InteractionContext.SOURCE_SCRIPT, Priority.High, insert_strategy=QueueInsertStrategy.NEXT)
        return sim.push_super_affordance(affordance, sim, context)

    def sim_skewer_rabbit_hole_affordances_gen(self, sim_info, context, **kwargs):
        for aop in self.LEAVE_EARLY_INTERACTION.potential_interactions(None, context, sim_info=sim_info, **kwargs):
            yield aop

    def remove_sim_from_rabbit_hole(self, sim_id, canceled=False):
        self._remove_rabbit_hole(sim_id, canceled=canceled)

    def _set_up_away_action(self, sim_info, away_action):
        sim_info.away_action_tracker.create_and_apply_away_action(away_action)

    def _set_up_expiration_alarm(self, sim_id, time):
        time_expired_callback = lambda _, sim_id=sim_id: self._remove_rabbit_hole(sim_id)
        return alarms.add_alarm(self, time, time_expired_callback, cross_zone=True)

    def _on_sim_moved_home(self, sim_info, rabbit_hole_affordance, away_action):
        push_success = self._push_affordance(sim_info.id, rabbit_hole_affordance)
        if not push_success:
            self._remove_rabbit_hole(sim_info.id, canceled=True)
            return
        self._set_up_away_action(sim_info, away_action)

    def _move_sim_home_and_setup(self, sim_info, rabbit_hole_affordance, away_action):
        if sim_info.is_instanced(allow_hidden_flags=ALL_HIDDEN_REASONS):
            return
        if sim_info.is_at_home:
            return
        home_zone_id = sim_info.household.home_zone_id
        if services.current_zone_id() != home_zone_id:
            sim_info.inject_into_inactive_zone(home_zone_id)
        else:
            SimSpawner.spawn_sim(sim_info, spawn_action=lambda _: self._on_sim_moved_home(sim_info, rabbit_hole_affordance, away_action), update_skewer=False)

    def _store_rabbit_hole(self, sim_id, rabbit_hole_type, time):
        alarm_handle = self._set_up_expiration_alarm(sim_id, time)
        self._rabbit_holes[sim_id] = rabbit_hole_type(sim_id, alarm_handle, CallableList())

    def _register_for_away_action_at_end_of_interaction(self, sim_info, affordance, away_action):
        sim_id = sim_info.id
        sim = sim_info.get_sim_instance()
        interaction = sim.find_interaction_by_affordance(affordance)
        away_action_callback = lambda _, sim_id=sim_id: self._set_up_away_action(sim_info, away_action)
        interaction.register_on_finishing_callback(away_action_callback)

    def _register_for_away_action_at_start_of_interaction(self, affordance):
        custom_key = affordance
        services.get_event_manager().register_with_custom_key(self, TestEvent.InteractionStart, custom_key)

    def _attach_exit_conditions(self, sim_id):
        rabbit_hole = self._rabbit_holes[sim_id]
        exit_condition_callback = lambda _, sim_id=sim_id: self._remove_rabbit_hole(sim_id, canceled=True)
        self._conditional_actions_manager.attach_conditions(rabbit_hole, rabbit_hole.exit_conditions, exit_condition_callback)

    def _detach_exit_conditions(self, rabbit_hole):
        self._conditional_actions_manager.detach_conditions(rabbit_hole)

    def handle_event(self, sim_info, *_):
        sim_id = sim_info.id
        away_action = self._rabbit_holes[sim_id].away_action
        self._set_up_away_action(sim_info, away_action)
        affordance = self._rabbit_holes[sim_id].affordance
        services.get_event_manager().unregister_with_custom_key(self, TestEvent.InteractionStart, affordance)

    def _register_callback_for_cancel(self, sim_info, affordance, is_travel_affordance=False):
        sim_id = sim_info.id
        sim = sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
        interaction = sim.find_interaction_by_affordance(affordance)

        def _on_cancel(interaction, sim_id=sim_id):
            if services.current_zone().is_zone_shutting_down:
                return
            if is_travel_affordance and self._rabbit_holes[sim_id].ignore_travel_cancel_callbacks:
                return
            if interaction.is_finishing_naturally:
                return
            self._remove_rabbit_hole(sim_id, canceled=True)

        interaction.register_on_cancelled_callback(_on_cancel)

    def _remove_rabbit_hole(self, sim_id, canceled=False):
        if sim_id not in self._rabbit_holes:
            return
        rabbit_hole = self._rabbit_holes.pop(sim_id)
        sim_info = services.sim_info_manager().get(sim_id)
        if sim_info.is_instanced(allow_hidden_flags=ALL_HIDDEN_REASONS):
            affordance = rabbit_hole.affordance
            sim = sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
            interaction = sim.find_interaction_by_affordance(affordance)
            if interaction is not None:
                interaction.cancel_user(cancel_reason_msg='Interaction canceled by the rabbit hole service')
        if not canceled:
            resolver = sim_info.get_resolver()
            for loot_action in rabbit_hole.loot_list:
                loot_action.apply_to_resolver(resolver)
        rabbit_hole.callbacks(canceled=canceled)
        self._detach_exit_conditions(rabbit_hole)
        if sim_info.away_action_tracker is not None:
            sim_info.away_action_tracker.reset_to_default_away_action()
        self._remove_sim_from_blacklist(sim_id)
