import random
from audio.primitive import TunablePlayAudio, play_tunable_audio
from clock import interval_in_real_seconds
from event_testing.resolver import SingleSimResolver
from event_testing.results import TestResult
from event_testing.tests import TunableTestSet
from event_testing.tests_with_data import TunableParticipantRanInteractionTest
from interactions import ParticipantType
from interactions.utils.camera import TunableCameraShake
from interactions.utils.loot import LootActions
from scheduler import WeeklySchedule, ScheduleEntry
from sims4.resources import Types
from sims4.tuning.tunable import TunableSet, TunableEnumEntry, TunableList, AutoFactoryInit, TunableReference, HasTunableSingletonFactory, TunableFactory, TunableVariant, TunablePercent, TunablePackSafeReference, TunableThreshold, TunableRealSecond, Tunable
from situations.service_npcs.modify_lot_items_tuning import ModifyAllLotItems
from tunable_utils.tunable_blacklist import TunableBlacklist
import alarms
import enum
import event_testing
import services
import sims4
logger = sims4.log.Logger('ZoneModifierAction', default_owner='jdimailig')

class ZoneModifierActionBehavior(enum.Int):
    ONCE = 0
    ONCE_IF_SIMS_EXIST = 1
    ONCE_IF_ACTIVE_SIM_ON_LOT = 2

class ZoneModifierActionVariants(TunableVariant):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, loot=ZoneModifierBroadcastLoot.TunableFactory(), quake=ZoneModifierTriggerQuake.TunableFactory(), modify_lot_items=ZoneModifierModifyLotItems.TunableFactory(), service_npc_request=ZoneModifierRequestServiceNPC.TunableFactory(), play_sound=ZoneModifierPlaySound.TunableFactory(), default='loot', **kwargs)

class TunableSimsThreshold(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'tests': TunableTestSet(description='\n            Tests to be performed on active Sims\n            '), 'threshold': TunableThreshold(description='\n            Checks against the number of Sims, Needs to \n            pass for the TunableSimsThreshold test to pass\n            ')}

    def test_sim_requirements(self, sims):
        count = 0
        for sim in sims:
            resolver = SingleSimResolver(sim.sim_info)
            if self.tests.run_tests(resolver):
                count += 1
        return self.threshold.compare(count)

class ZoneModifierAction(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'behavior': TunableEnumEntry(description='\n            Under what conditions the action should be applied.\n            \n            May be one of the following:\n            - Always applied.\n            - Applied only if there are Sims on the lot.\n            - Applied only if the active Sim is on the lot.\n            ', tunable_type=ZoneModifierActionBehavior, default=ZoneModifierActionBehavior.ONCE), 'threshold_requirements': TunableList(description='\n            Number of Sims required on active lot in order for the \n            action to be applied\n            ', tunable=TunableSimsThreshold.TunableFactory())}

    def perform(self):
        if self._can_perform_action():
            self._perform_action()

    def _can_perform_action(self):
        if self.behavior == ZoneModifierActionBehavior.ONCE:
            return self._check_threshold_requirements()
        if self.behavior == ZoneModifierActionBehavior.ONCE_IF_ACTIVE_SIM_ON_LOT:
            active_sim = services.get_active_sim()
            if active_sim is not None and active_sim.is_on_active_lot() and self._check_threshold_requirements():
                return True
        elif self.behavior == ZoneModifierActionBehavior.ONCE_IF_SIMS_EXIST:
            sims = list(services.sim_info_manager().instanced_sims_on_active_lot_gen())
            if any(sims) and self._check_threshold_requirements(sims):
                return True
        return False

    def _check_threshold_requirements(self, sims=None):
        if not self.threshold_requirements:
            return True
        if sims is None:
            sims = list(services.sim_info_manager().instanced_sims_on_active_lot_gen())
        return all(requirement.test_sim_requirements(sims) for requirement in self.threshold_requirements)

    def _perform_action(self):
        raise NotImplementedError

    @property
    def _additional_resolver_participants(self):
        return {ParticipantType.PickedZoneId: frozenset()}

    def sim_resolver(self, sim_info):
        return SingleSimResolver(sim_info, additional_participants=self._additional_resolver_participants)

class ZoneModifierSimLootMixin:
    FACTORY_TUNABLES = {'loots': TunableSet(description='\n            Loot(s) to apply.  Loot applied to Sims must be configured\n            against Actor participant type.\n            \n            This loot op does not occur in an interaction context,\n            so other participant types may not be supported.\n            ', tunable=TunableReference(manager=services.get_instance_manager(sims4.resources.Types.ACTION), pack_safe=True))}

    def apply_loots_to_sims_on_active_lot(self):
        self.apply_loots_to_sims(services.sim_info_manager().instanced_sims_on_active_lot_gen())

    def apply_loots_to_sims(self, sims):
        for sim in sims:
            self.apply_loots_to_sim(sim)

    def apply_loots_to_sim(self, sim):
        resolver = self.sim_resolver(sim.sim_info)
        for loot_action in self.loots:
            loot_action.apply_to_resolver(resolver)

    def apply_loots_to_random_sim_on_active_lot(self):
        sims = list(services.sim_info_manager().instanced_sims_on_active_lot_gen())
        if len(sims) == 0:
            return
        chosen_sim = random.choice(sims)
        self.apply_loots_to_sim(chosen_sim)

class ZoneModifierPlaySound(ZoneModifierAction):
    FACTORY_TUNABLES = {'sound_effect': TunablePlayAudio(description='\n            Sound to play.\n            '), 'duration': TunableRealSecond(description='\n            How long the sound should play for, in seconds.\n            After this duration, the sound will be stopped.\n            ', default=5, minimum=1)}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stop_sound_handle = None

    def _perform_action(self):
        if self._stop_sound_handle is not None:
            return
        self._sound = play_tunable_audio(self.sound_effect)
        self._stop_sound_handle = alarms.add_alarm(services.get_active_sim(), interval_in_real_seconds(self.duration), self._stop_sound)

    def _stop_sound(self, *args):
        if self._sound is None:
            return
        self._sound.stop()
        self._sound = None
        self._stop_sound_handle.cancel()
        self._stop_sound_handle = None

class ZoneModifierTriggerQuake(ZoneModifierSimLootMixin, ZoneModifierAction):
    FACTORY_TUNABLES = {'shake_effect': TunableCameraShake.TunableFactory(description='\n            Tunable camera shake effect which will occur at the given trigger time.\n            '), 'play_sound': ZoneModifierPlaySound.TunableFactory(description='\n            Sound to play when a quake occurs\n            ', locked_args={'behavior': ZoneModifierActionBehavior.ONCE, 'threshold_requirements': ()}), 'chance': TunablePercent(description='\n            Chance that the quake will occur.\n            ', default=100)}

    def _perform_action(self):
        if random.random() < self.chance:
            self.play_sound.perform()
            self.shake_effect.shake_camera()
            self.apply_loots_to_sims_on_active_lot()

class ZoneModifierRequestServiceNPC(ZoneModifierAction):
    FACTORY_TUNABLES = {'service_npc': TunablePackSafeReference(services.get_instance_manager(Types.SERVICE_NPC))}

    def _perform_action(self):
        if self.service_npc is None:
            return
        household = services.owning_household_of_active_lot()
        if household is None:
            return
        services.current_zone().service_npc_service.request_service(household, self.service_npc, user_specified_data_id=None, is_recurring=False)

class ZoneModifierBroadcastLoot(ZoneModifierSimLootMixin, ZoneModifierAction):
    ALL_SIMS_ON_LOT = 'AllSimsOnLot'
    ACTIVE_SIM_ONLY = 'ActiveSimOnly'
    RANDOM_SIM_ON_LOT = 'RandomSimOnLot'
    FACTORY_TUNABLES = {'loot_distribution': TunableVariant(description='\n            How to distribute the loot.  By default, distributes the loots\n            to all the Sims on the active lot.\n            \n            Another behavior is to only distribute to the active Sim. This\n            option could be used for things like TNS or global situations.\n            ', locked_args={'all_sims_on_lot': ALL_SIMS_ON_LOT, 'active_sim_only': ACTIVE_SIM_ONLY, 'random_sim_on_lot': RANDOM_SIM_ON_LOT}, default='all_sims_on_lot')}

    def _perform_action(self):
        distribution_type = self.loot_distribution
        if distribution_type == self.ACTIVE_SIM_ONLY:
            active_sim = services.get_active_sim()
            if active_sim is None:
                return
            self.apply_loots_to_sims([active_sim])
        elif distribution_type == self.ALL_SIMS_ON_LOT:
            self.apply_loots_to_sims_on_active_lot()
        elif distribution_type == self.RANDOM_SIM_ON_LOT:
            self.apply_loots_to_random_sim_on_active_lot()

class ZoneModifierModifyLotItems(ZoneModifierAction):
    FACTORY_TUNABLES = {'actions': ModifyAllLotItems.TunableFactory(description='\n            Actions to apply to all lot objects on active lot.\n            ')}

    def criteria(self, obj):
        return obj.is_on_active_lot()

    def _perform_action(self):
        self.actions().modify_objects(object_criteria=self.criteria)

class ZoneModifierWeeklySchedule(WeeklySchedule):

    class ZoneModifierWeeklyScheduleEntry(ScheduleEntry):

        @staticmethod
        def _callback(instance_class, tunable_name, source, value, **kwargs):
            setattr(value, 'zone_modifier', instance_class)

        FACTORY_TUNABLES = {'execute_on_removal': Tunable(description='\n                If checked, this schedule entry is executed when the modifier is\n                removed while the zone is running.\n                ', tunable_type=bool, default=False), 'callback': _callback}

    @TunableFactory.factory_option
    def schedule_entry_data(pack_safe=True):
        return {'schedule_entries': TunableSet(description='\n                A list of event schedules. Each event is a mapping of days of the\n                week to a start_time and duration.\n                ', tunable=ZoneModifierWeeklySchedule.ZoneModifierWeeklyScheduleEntry.TunableFactory(schedule_entry_data={'tuning_name': 'actions', 'tuning_type': TunableList(tunable=ZoneModifierActionVariants(description='\n                                Action to perform during the schedule entry.\n                                '))}))}

class ZoneModifierTriggerInteractions(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'test': TunableParticipantRanInteractionTest(description='\n            Criteria for an interaction to be able to satisfy this trigger.\n            ', locked_args={'participant': ParticipantType.Actor, 'tooltip': None}), 'blacklist': TunableBlacklist(description='\n            A black list specifying any affordances that should never be included,\n            even if they match the trigger criteria.\n            ', tunable=TunableReference(manager=services.affordance_manager(), pack_safe=True))}
    expected_kwargs = (('sims', event_testing.test_constants.SIM_INSTANCE), ('interaction', event_testing.test_constants.FROM_EVENT_DATA))

    def get_expected_args(self):
        return dict(self.expected_kwargs)

    def __call__(self, interaction=None, sims=None):
        if interaction is None:
            return TestResult(False, 'interaction is null')
        if not self.blacklist.test_item(interaction.affordance):
            return TestResult(False, 'Failed affordance check: {} is in blacklist {}', interaction.affordance, self)
        return self.test(interaction=interaction, sims=sims)

    def applies_to_event(self, event):
        return event in self.test.test_events

class ZoneInteractionTriggers(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'trigger_conditions': TunableList(description='\n            Check the if a specified interaction(s) ran to see if it will\n            trigger the specified loot.\n            ', tunable=ZoneModifierTriggerInteractions.TunableFactory()), 'on_interaction_loot': TunableSet(description='\n            Loot applied to the Sim when the actor participant performs\n            an interaction that matches the criteria.\n            ', tunable=LootActions.TunableReference(pack_safe=True))}

    def handle_interaction_event(self, sim_info, event, resolver):
        for test in self.trigger_conditions:
            if test.applies_to_event(event):
                if resolver(test):
                    for loot in self.on_interaction_loot:
                        loot.apply_to_resolver(resolver)
                    break

    def get_trigger_tests(self):
        tests = list()
        for trigger_conditions in self.trigger_conditions:
            tests.append(trigger_conditions.test)
        return tests
