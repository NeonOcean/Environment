from clubs.club_tests import ClubTest
from crafting.photography_tests import TookPhotoTest
from event_testing.results import TestResult
from interactions import ParticipantType, ParticipantTypeSim
from sims4.tuning.tunable import TunableVariant, Tunable
from sims4.tuning.tunable_base import GroupNames
from situations.situation_goal import SituationGoal
import event_testing.test_variants
import objects.object_tests
import services
import sims.sim_info_tests
import sims4.tuning.tunable
import statistics.skill_tests
import world.world_tests
import zone_tests

class TunableSituationGoalActorPostTestVariant(TunableVariant):

    def __init__(self, description='A single tunable test.', **kwargs):
        super().__init__(statistic=event_testing.statistic_tests.StatThresholdTest.TunableFactory(locked_args={'who': ParticipantType.Actor, 'tooltip': None}), ranked_statistic=event_testing.statistic_tests.RankedStatThresholdTest.TunableFactory(locked_args={'who': ParticipantType.Actor, 'tooltip': None}), skill_tag=statistics.skill_tests.SkillTagThresholdTest.TunableFactory(locked_args={'who': ParticipantType.Actor, 'tooltip': None}), mood=sims.sim_info_tests.MoodTest.TunableFactory(locked_args={'who': ParticipantTypeSim.Actor, 'tooltip': None}), sim_info=sims.sim_info_tests.SimInfoTest.TunableFactory(locked_args={'who': ParticipantType.Actor, 'tooltip': None}), location=world.world_tests.LocationTest.TunableFactory(locked_args={'subject': ParticipantType.Actor, 'tooltip': None}), lot_owner=event_testing.test_variants.LotOwnerTest.TunableFactory(locked_args={'subject': ParticipantType.Actor, 'tooltip': None}), sim_filter=sims.sim_info_tests.FilterTest.TunableFactory(locked_args={'filter_target': ParticipantType.Actor, 'tooltip': None}), trait=sims.sim_info_tests.TraitTest.TunableFactory(locked_args={'subject': ParticipantType.Actor, 'tooltip': None}), buff=sims.sim_info_tests.BuffTest.TunableFactory(locked_args={'subject': ParticipantType.Actor, 'tooltip': None}), motive=event_testing.statistic_tests.MotiveThresholdTest.TunableFactory(locked_args={'who': ParticipantType.Actor, 'tooltip': None}), skill_test=statistics.skill_tests.SkillRangeTest.TunableFactory(locked_args={'tooltip': None}), situation_job=event_testing.test_variants.TunableSituationJobTest(locked_args={'participant': ParticipantType.Actor, 'tooltip': None}), career=event_testing.test_variants.TunableCareerTest.TunableFactory(locked_args={'subjects': ParticipantType.Actor, 'tooltip': None}), collection=event_testing.test_variants.TunableCollectionThresholdTest(locked_args={'who': ParticipantType.Actor, 'tooltip': None}), club=ClubTest.TunableFactory(locked_args={'subject': ParticipantType.Actor, 'club': ClubTest.CLUB_USE_ANY, 'tooltip': None}), zone=zone_tests.ZoneTest.TunableFactory(locked_args={'tooltip': None}), description=description, **kwargs)

class TunableSituationGoalActorPostTestSet(event_testing.tests.TestListLoadingMixin):
    DEFAULT_LIST = event_testing.tests.TestList()

    def __init__(self, description=None, **kwargs):
        if description is None:
            description = 'A list of tests.  All tests must succeed to pass the TestSet.'
        super().__init__(description=description, tunable=TunableSituationGoalActorPostTestVariant(), **kwargs)

class SituationGoalActor(SituationGoal):
    INSTANCE_TUNABLES = {'_goal_test': sims4.tuning.tunable.TunableVariant(buff=sims.sim_info_tests.BuffTest.TunableFactory(locked_args={'subject': ParticipantType.Actor, 'blacklist': None, 'tooltip': None}), mood=sims.sim_info_tests.MoodTest.TunableFactory(locked_args={'who': ParticipantTypeSim.Actor}, description='A test to run to determine if the player has attained a specific mood.'), skill_tag=statistics.skill_tests.SkillTagThresholdTest.TunableFactory(locked_args={'who': ParticipantType.Actor, 'tooltip': None}), statistic=event_testing.statistic_tests.StatThresholdTest.TunableFactory(stat_class_restriction_override=(('Statistic', 'Skill'),), locked_args={'who': ParticipantType.Actor, 'tooltip': None}), ranked_statistic=event_testing.statistic_tests.RankedStatThresholdTest.TunableFactory(locked_args={'who': ParticipantType.Actor, 'tooltip': None}), career=event_testing.test_variants.TunableCareerTest.TunableFactory(locked_args={'tooltip': None}), collection=event_testing.test_variants.TunableCollectionThresholdTest(locked_args={'who': ParticipantType.Actor, 'tooltip': None}), inventory=objects.object_tests.InventoryTest.TunableFactory(locked_args={'tooltip': None}), collected_single_item=event_testing.test_variants.CollectedItemTest.TunableFactory(locked_args={'tooltip': None}), club=ClubTest.TunableFactory(locked_args={'subject': ParticipantType.Actor, 'club': ClubTest.CLUB_USE_ANY, 'tooltip': None}), situation_running=event_testing.test_variants.TunableSituationRunningTest(), took_photo=TookPhotoTest.TunableFactory(), default='buff', description='Primary test which triggers evaluation of goal completion.', tuning_group=GroupNames.TESTS), '_post_tests': TunableSituationGoalActorPostTestSet(description='\n               A set of tests that must all pass when the player satisfies the goal_test \n               for the goal to be consider completed.\nThese test can only consider the \n               actor and the environment. \ne.g. Practice in front of mirror while drunk.\n               ', tuning_group=GroupNames.TESTS), 'ignore_goal_precheck': Tunable(description='\n            Checking this box will skip the normal goal pre-check in the case that other tuning makes the goal\n            continue to be valid. For example, for a collection test, we may want to give the goal to collect\n            an additional object even though the test that we have collected this object before will already\n            pass. This allows us to tune a more specific pre-test to check for the amount we want to collect.', tunable_type=bool, default=False)}

    @classmethod
    def can_be_given_as_goal(cls, actor, situation, **kwargs):
        result = super(SituationGoalActor, cls).can_be_given_as_goal(actor, situation)
        if not result:
            return result
        if actor is not None and not cls.ignore_goal_precheck:
            resolver = event_testing.resolver.DataResolver(actor.sim_info)
            result = resolver(cls._goal_test)
            if result:
                return TestResult(False, 'Goal test already passes and so cannot be given as goal.')
        return TestResult.TRUE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self):
        super().setup()
        services.get_event_manager().register_tests(self, (self._goal_test,))

    def _decommision(self):
        services.get_event_manager().unregister_tests(self, (self._goal_test,))
        super()._decommision()

    def _run_goal_completion_tests(self, sim_info, event, resolver):
        if not resolver(self._goal_test):
            return False
        return super()._run_goal_completion_tests(sim_info, event, resolver)
