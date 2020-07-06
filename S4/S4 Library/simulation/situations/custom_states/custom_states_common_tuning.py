import services
from aspirations.aspiration_tests import SelectedAspirationTest, SelectedAspirationTrackTest
from clubs.club_tests import ClubTest
from crafting.photography_tests import TookPhotoTest
from drama_scheduler.drama_node_tests import FestivalRunningTest
from event_testing.objective_tuning import ParticipantTypeTargetAllRelationships, ParticipantTypeActorHousehold
from event_testing.resolver import GlobalResolver
from event_testing.statistic_tests import StatThresholdTest, RankedStatThresholdTest
from event_testing.test_variants import AtWorkTest, BucksPerkTest, CareerPromotedTest, TunableCareerTest, CollectedItemTest, TunableCollectionThresholdTest, EventRanSuccessfullyTest, HouseholdSizeTest, PurchasePerkTest, TunableSimoleonsTest, TunableSituationRunningTest, TunableUnlockedTest
from event_testing.tests_with_data import GenerationTest, OffspringCreatedTest, TunableParticipantRanAwayActionTest, TunableParticipantRanInteractionTest, TunableSimoleonsEarnedTest, WhimCompletedTest
from interactions import ParticipantType, ParticipantTypeSim, ParticipantTypeActorTargetSim, ParticipantTypeSingleSim
from objects.object_tests import CraftedItemTest, InventoryTest, ObjectCriteriaTest, ObjectPurchasedTest
from relationships.relationship_tests import TunableRelationshipTest, RelationshipBitTest
from seasons.season_tests import SeasonTest
from sims.sim_info_tests import BuffAddedTest, BuffTest, MoodTest, TraitTest
from sims.unlock_tracker_tests import UnlockTrackerAmountTest
from sims4.random import weighted_random_item
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableList, TunableTuple, Tunable, TunableVariant
from statistics.skill_tests import SkillTagThresholdTest
from tunable_multiplier import TunableMultiplier
from tunable_time import TunableTimeOfDay
from world.world_tests import LocationTest
from zone_tests import ZoneTest

class RandomWeightedSituationStateKey(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'possible_state_keys': TunableList(description='\n            The possible situation state keys.\n            ', tunable=TunableTuple(situation_key=Tunable(description='\n                    The key of the situation state.\n                    ', tunable_type=str, default=None), weight=TunableMultiplier.TunableFactory(description='\n                    A weight with testable multipliers that is used to \n                    determine how likely this entry is to be picked when \n                    selecting randomly.\n                    ')), minlength=1)}

    def __call__(self):
        resolver = GlobalResolver()
        return weighted_random_item(tuple((possible_state.weight.get_multiplier(resolver), possible_state.situation_key) for possible_state in self.possible_state_keys))

class TimeBasedSituationStateKey(HasTunableSingletonFactory):
    FACTORY_TUNABLES = {'situation_key_schedule': TunableList(description='\n            The schedule of situation starting keys.\n            ', tunable=TunableTuple(description='\n                A time block for a situation key.\n                ', possible_situation_keys=RandomWeightedSituationStateKey.TunableFactory(), time=TunableTimeOfDay(description='\n                    The time of this situation key.  This time block will exist until the next time block tuned.\n                    ', default_hour=9)), minlength=1)}

    def __init__(self, situation_key_schedule):
        self._situation_key_schedule = list(situation_key_schedule)
        self._situation_key_schedule.sort(key=lambda situation_time_block: situation_time_block.time)

    def __call__(self):
        now = services.game_clock_service().now()
        for (time_block_index, next_time_block) in enumerate(self._situation_key_schedule, start=-1):
            time_block = self._situation_key_schedule[time_block_index]
            if now.time_between_day_times(time_block.time, next_time_block.time):
                return time_block.possible_situation_keys()

class CustomStatesSituationTriggerDataTestVariant(TunableVariant):

    def __init__(self, *args, description='A tunable test supported for use as a situation trigger.', **kwargs):
        super().__init__(*args, at_work=AtWorkTest.TunableFactory(locked_args={'subject': ParticipantType.Actor, 'tooltip': None}), bucks_perk_unlocked=BucksPerkTest.TunableFactory(description='\n                A test for which kind of bucks perk is being unlocked\n                ', locked_args={'tooltip': None}), buff_added=BuffAddedTest.TunableFactory(locked_args={'tooltip': None}), career_promoted=CareerPromotedTest.TunableFactory(locked_args={'tooltip': None}), career_test=TunableCareerTest.TunableFactory(locked_args={'subjects': ParticipantType.Actor, 'tooltip': None}), club_tests=ClubTest.TunableFactory(locked_args={'tooltip': None, 'club': ClubTest.CLUB_FROM_EVENT_DATA, 'room_for_new_members': None, 'subject_passes_membership_criteria': None, 'subject_can_join_more_clubs': None}), collected_item_test=CollectedItemTest.TunableFactory(locked_args={'tooltip': None}), collection_test=TunableCollectionThresholdTest(locked_args={'who': ParticipantType.Actor, 'tooltip': None}), crafted_item=CraftedItemTest.TunableFactory(locked_args={'tooltip': None}), event_ran_successfully=EventRanSuccessfullyTest.TunableFactory(description='\n                This is a simple test that always returns true whenever one of\n                the tuned test events is processed.\n                ', locked_args={'tooltip': None}), festival_running=FestivalRunningTest.TunableFactory(description='\n                This is a test that triggers when the festival begins.\n                ', locked_args={'tooltip': None}), generation_created=GenerationTest.TunableFactory(locked_args={'tooltip': None}), has_buff=BuffTest.TunableFactory(locked_args={'subject': ParticipantType.Actor, 'tooltip': None}), household_size=HouseholdSizeTest.TunableFactory(locked_args={'participant': ParticipantType.Actor, 'tooltip': None}), inventory=InventoryTest.TunableFactory(locked_args={'tooltip': None}), location_test=LocationTest.TunableFactory(location_tests={'is_outside': False, 'is_natural_ground': False, 'is_in_slot': False, 'is_on_active_lot': False, 'is_on_level': False}), mood_test=MoodTest.TunableFactory(locked_args={'who': ParticipantTypeSim.Actor, 'tooltip': None}), object_criteria=ObjectCriteriaTest.TunableFactory(locked_args={'tooltip': None}), object_purchase_test=ObjectPurchasedTest.TunableFactory(locked_args={'tooltip': None}), offspring_created_test=OffspringCreatedTest.TunableFactory(locked_args={'tooltip': None}), purchase_perk_test=PurchasePerkTest.TunableFactory(description='\n                A test for which kind of perk is being purchased.\n                '), photo_taken=TookPhotoTest.TunableFactory(description='\n                A test for player taken photos.\n                '), ran_away_action_test=TunableParticipantRanAwayActionTest(locked_args={'participant': ParticipantTypeActorTargetSim.Actor, 'tooltip': None}), ran_interaction_test=TunableParticipantRanInteractionTest(locked_args={'participant': ParticipantType.Actor, 'tooltip': None}), relationship=TunableRelationshipTest(participant_type_override=(ParticipantTypeTargetAllRelationships, ParticipantTypeTargetAllRelationships.AllRelationships), locked_args={'tooltip': None}), relationship_bit=RelationshipBitTest.TunableFactory(locked_args={'subject': ParticipantType.Actor, 'target': ParticipantType.TargetSim, 'tooltip': None}), season_test=SeasonTest.TunableFactory(locked_args={'tooltip': None}), selected_aspiration_test=SelectedAspirationTest.TunableFactory(locked_args={'who': ParticipantTypeSingleSim.Actor, 'tooltip': None}), selected_aspiration_track_test=SelectedAspirationTrackTest.TunableFactory(locked_args={'who': ParticipantTypeSingleSim.Actor, 'tooltip': None}), simoleons_earned=TunableSimoleonsEarnedTest(locked_args={'tooltip': None}), simoleon_value=TunableSimoleonsTest(locked_args={'tooltip': None}), situation_running_test=TunableSituationRunningTest(locked_args={'tooltip': None}), skill_tag=SkillTagThresholdTest.TunableFactory(locked_args={'who': ParticipantType.Actor, 'tooltip': None}), statistic=StatThresholdTest.TunableFactory(locked_args={'who': ParticipantType.Actor, 'tooltip': None}), ranked_statistic=RankedStatThresholdTest.TunableFactory(locked_args={'who': ParticipantType.Actor, 'tooltip': None}), trait=TraitTest.TunableFactory(participant_type_override=(ParticipantTypeActorHousehold, ParticipantTypeActorHousehold.Actor), locked_args={'tooltip': None}), unlock_earned=TunableUnlockedTest(locked_args={'participant': ParticipantType.Actor, 'tooltip': None}), unlock_tracker_amount=UnlockTrackerAmountTest.TunableFactory(locked_args={'subject': ParticipantType.Actor, 'tooltip': None}), whim_completed_test=WhimCompletedTest.TunableFactory(locked_args={'tooltip': None}), zone=ZoneTest.TunableFactory(locked_args={'tooltip': None}), default='ran_interaction_test', description=description, **kwargs)
