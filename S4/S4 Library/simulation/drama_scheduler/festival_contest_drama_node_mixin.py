# uncompyle6 version 3.4.0
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.4 (tags/v3.7.4:e09359112e, Jul  8 2019, 20:34:20) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\drama_scheduler\festival_contest_drama_node_mixin.py
# Size of source mod 2**32: 18260 bytes
from dataclasses import dataclass
from date_and_time import create_time_span
from event_testing.resolver import SingleSimResolver
from sims4 import random
from sims4.tuning.tunable import TunableReference, TunableSimMinute, TunableRange, TunableInterval, TunableList, OptionalTunable, TunableTuple, Tunable, HasTunableSingletonFactory, AutoFactoryInit, TunableVariant
from sims4.tuning.tunable_base import GroupNames
from ui.ui_dialog_notification import UiDialogNotification, TunableUiDialogNotificationSnippet
import alarms, services, sims4
logger = sims4.log.Logger('DramaNode', default_owner='msundaram')

@dataclass
class ContestScore:
    __annotations__['score'] = float
    __annotations__['sim_id'] = int
    __annotations__['object_id'] = int

    def __init__(self, score, sim_id=0, object_id=0):
        self.score = score
        self.sim_id = sim_id
        self.object_id = object_id


class _FestivalContestWinnerSelectionMethod(HasTunableSingletonFactory, AutoFactoryInit):

    def get_winners(self, contest):
        raise NotImplementedError

    def max_scores_to_consider(self):
        pass

    def uses_ranking(self):
        return True


class _FestivalContestWinnerSelectionMethod_Ranked(_FestivalContestWinnerSelectionMethod):
    FACTORY_TUNABLES = {'_scores_to_consider': TunableRange(description='\n            How many scores should be considered for the prizes.\n            ',
                              tunable_type=int,
                              default=3,
                              minimum=1,
                              tuning_group=(GroupNames.FESTIVAL_CONTEST))}

    def get_winners(self, contest):
        return contest._scores

    def max_scores_to_consider(self):
        return self._scores_to_consider


class _FestivalContestWinnerSelectionMethod_WeightedRandom(_FestivalContestWinnerSelectionMethod):
    FACTORY_TUNABLES = {}

    def get_winners(self, contest):
        num_rewards = len(contest.festival_contest_tuning._win_rewards)
        scores = [(contest_score.score, contest_score) for contest_score in contest._scores]
        winners = []
        while scores:
            if len(winners) < num_rewards:
                winner = random.pop_weighted(scores)
                winners.append(winner)

        return winners

    def uses_ranking(self):
        return False


class FestivalContestDramaNodeMixin:
    SIM_ID_SAVE_TOKEN = 'sim_ids'
    OBJECT_ID_SAVE_TOKEN = 'object_ids'
    SCORE_SAVE_TOKEN = 'scores'
    WINNERS_AWARDED_TOKEN = 'awarded'
    USER_SUBMITTED_TOKEN = 'submitted'
    INSTANCE_TUNABLES = {'festival_contest_tuning': OptionalTunable(description='\n            Optional contest tuning\n            ',
                                  tunable=TunableTuple(_score_update_frequency=TunableSimMinute(description='\n                    How often a fake new score should be submitted to the tournament.\n                    ',
                                  default=30,
                                  minimum=0,
                                  tuning_group=(GroupNames.FESTIVAL_CONTEST)),
                                  _score_update_value_interval=TunableInterval(description='\n                    When a fake new score is submitted, the interval determining what the value should be.\n                    ',
                                  tunable_type=float,
                                  default_lower=0,
                                  default_upper=10,
                                  minimum=0,
                                  tuning_group=(GroupNames.FESTIVAL_CONTEST)),
                                  _win_rewards=TunableList(description='\n                    List of Loots applied to the winners of the contest. Index refers to the \n                    winner who receives that loot. 1st, 2nd, 3rd, etc.\n                    ',
                                  tunable=TunableReference(description='\n                        A reference to a loot that will be applied to one of the winners.\n                        ',
                                  manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
                                  class_restrictions=('LootActions', )),
                                  tuning_group=(GroupNames.FESTIVAL_CONTEST)),
                                  _win_notifications=TunableList(description='\n                    List of notifications applied to the winners of the contest. These display regardless of whether\n                    the rewards have already been given out. Index refers to the winners of that rank. 1st, 2nd, 3rd, etc.\n                    ',
                                  tunable=(UiDialogNotification.TunableFactory()),
                                  tuning_group=(GroupNames.FESTIVAL_CONTEST)),
                                  _lose_notification=TunableUiDialogNotificationSnippet(description='\n                    Notification displayed if there are no player sim winners of the contest. Only displayed if the \n                    winners are requested, not at the end of the festival.\n                    ',
                                  tuning_group=(GroupNames.FESTIVAL_CONTEST)),
                                  _contest_duration=TunableSimMinute(description='\n                    The amount of time in sim minutes that we should allow scores to be\n                    submitted to the contest and that we should submit fake scores.\n                    ',
                                  default=60,
                                  minimum=0,
                                  tuning_group=(GroupNames.FESTIVAL_CONTEST)),
                                  _weight_statistic=TunableReference(description="\n                    Statistic that describes the weight of the object for the contest. The \n                    value of the statistic is used as the sim's score in the contest\n                    ",
                                  manager=(services.statistic_manager())),
                                  _allow_multiple_entries_per_sim=Tunable(description='\n                    If checked, the same sim can have more than one object in\n                    the scores list. If false (default) only the highest scoring\n                    submission per sim is maintained.\n                    ',
                                  tunable_type=bool,
                                  default=False,
                                  tuning_group=(GroupNames.FESTIVAL_CONTEST)),
                                  _destroy_object_on_submit=Tunable(description='\n                    If checked, the submitted object will be destroyed when it\n                    is submitted for the contest.\n                    ',
                                  tunable_type=bool,
                                  default=True,
                                  tuning_group=(GroupNames.FESTIVAL_CONTEST)),
                                  _winner_selection_method=TunableVariant(description='\n                    Which method to use for choosing a winner (or winners) of the contest.\n                    ',
                                  ranked=(_FestivalContestWinnerSelectionMethod_Ranked.TunableFactory()),
                                  weighted_random=(_FestivalContestWinnerSelectionMethod_WeightedRandom.TunableFactory()),
                                  default='ranked',
                                  tuning_group=(GroupNames.FESTIVAL_CONTEST))))}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        if self.festival_contest_tuning is None:
            return
        self._scores = []
        self._score_alarm = None
        self._has_awarded_winners = False

    def _try_and_start_festival(self):
        super()._try_and_start_festival()
        if self.festival_contest_tuning is None:
            return
        self._setup_score_add_alarm()

    def _setup_score_add_alarm(self):
        if self.festival_contest_tuning._score_update_frequency > 0:
            duration = create_time_span(minutes=(self.festival_contest_tuning._score_update_frequency))
            self._score_alarm = alarms.add_alarm(self, duration, self._score_add_callback, True)
        elif self.festival_contest_tuning._score_update_value_interval.upper_bound > 0:
            self._add_fake_score()

    def _score_add_callback(self, _):
        if self._get_remaining_contest_time().in_minutes() <= 0:
            if self._score_alarm is not None:
                alarms.cancel_alarm(self._score_alarm)
                self._score_alarm = None
            return
        self._add_fake_score()

    def _get_remaining_contest_time(self):
        now = services.time_service().sim_now
        time_since_started = now - self._selected_time
        duration = create_time_span(minutes=(self.festival_contest_tuning._contest_duration + self.pre_festival_duration))
        time_left_to_go = duration - time_since_started
        return time_left_to_go

    def _add_fake_score(self):
        score = self.festival_contest_tuning._score_update_value_interval.random_float()
        self.add_score(sim_id=0, object_id=0, score=score)

    def add_score(self, sim_id, object_id, score):
        scores = self._scores
        if sim_id == 0:
            scores.append(ContestScore(score, sim_id=sim_id, object_id=object_id))
        else:
            found_score = False
            for current_score_obj in scores:
                if current_score_obj.sim_id == sim_id:
                    if self.festival_contest_tuning._allow_multiple_entries_per_sim:
                        if current_score_obj.object_id != object_id:
                            continue
                        current_score = current_score_obj.score
                        if current_score >= score:
                            return
                        current_score_obj.score = score
                        found_score = True
                        break

            if not found_score:
                scores.append(ContestScore(score, sim_id=sim_id, object_id=object_id))
            scores.sort(key=(lambda item: item.score), reverse=True)
            scores_to_consider = self.festival_contest_tuning._winner_selection_method.max_scores_to_consider()
            if scores_to_consider is not None:
                if len(scores) > scores_to_consider:
                    scores = scores[:scores_to_consider]
                    self._scores = scores
                if not self.festival_contest_tuning._winner_selection_method.uses_ranking():
                    return
                for rank, obj in enumerate(scores):
                    if obj.sim_id == sim_id:
                        return rank
                else:
                    return

    def get_scores_gen(self):
        self._scores.sort(key=(lambda item: item.score), reverse=False)
        yield from self._scores

    def is_during_contest(self):
        if self.is_during_pre_festival():
            return False
        else:
            remaining_time = self._get_remaining_contest_time()
            return remaining_time.in_minutes() > 0

    def award_winners(self, show_fallback_dialog=False):
        valid_sim_won = False
        winners = self.festival_contest_tuning._winner_selection_method.get_winners(self)
        sim_info_manager = services.sim_info_manager()
        for contest_score, award in zip(winners, self.festival_contest_tuning._win_rewards):
            if not contest_score.sim_id is None:
                if contest_score.sim_id is 0:
                    pass
                elif not sim_info_manager.is_sim_id_valid(contest_score.sim_id):
                    pass
                else:
                    valid_sim_won = True
                    sim = sim_info_manager.get(contest_score.sim_id)
                    resolver = SingleSimResolver(sim)
                    if not self._has_awarded_winners:
                        award.apply_to_resolver(resolver)
                    rank = winners.index(contest_score)
                    if rank >= len(self.festival_contest_tuning._win_notifications):
                        pass
                    else:
                        notification = self.festival_contest_tuning._win_notifications[rank]
                        dialog = notification(sim, target_sim_id=(contest_score.sim_id),
                          resolver=resolver)
                        dialog.show_dialog()

        if show_fallback_dialog:
            if not valid_sim_won:
                active_sim = services.get_active_sim()
                resolver = SingleSimResolver(active_sim)
                dialog = self.festival_contest_tuning._lose_notification(active_sim, target_sim_id=(active_sim.id if active_sim is not None else None),
                  resolver=resolver)
                dialog.show_dialog()
            self._has_awarded_winners = True

    def cleanup(self, from_service_stop=False):
        super().cleanup(from_service_stop=from_service_stop)
        if self.festival_contest_tuning is None:
            return
        if self._score_alarm is not None:
            alarms.cancel_alarm(self._score_alarm)
            self._score_alarm = None

    def complete(self, **kwargs):
        (super().complete)(**kwargs)
        if self.festival_contest_tuning is None:
            return
        if self.is_during_pre_festival():
            return
        if self.is_during_contest():
            return
        if self._has_awarded_winners:
            return
        self.award_winners(show_fallback_dialog=(self.has_user_submitted_entry()))

    def _save_custom_data(self, writer):
        super()._save_custom_data(writer)
        if self.festival_contest_tuning is None:
            return
        if self._scores and len(self._scores) == 0:
            return
        scores = []
        sim_ids = []
        object_ids = []
        for score in self.get_scores_gen():
            scores.append(score.score)
            sim_ids.append(score.sim_id)
            object_ids.append(score.object_id)

        writer.write_floats(self.SCORE_SAVE_TOKEN, scores)
        writer.write_uint64s(self.SIM_ID_SAVE_TOKEN, sim_ids)
        writer.write_uint64s(self.OBJECT_ID_SAVE_TOKEN, object_ids)
        writer.write_bool(self.WINNERS_AWARDED_TOKEN, self._has_awarded_winners)

    def _load_custom_data(self, reader):
        super_success = super()._load_custom_data(reader)
        if self.festival_contest_tuning is None:
            return
        elif not super_success:
            return False
        else:
            self._scores = []
            scores = reader.read_floats(self.SCORE_SAVE_TOKEN, ())
            sim_ids = reader.read_uint64s(self.SIM_ID_SAVE_TOKEN, ())
            object_ids = reader.read_uint64s(self.OBJECT_ID_SAVE_TOKEN, None)
            if object_ids is None:
                object_ids = (0, ) * len(sim_ids)
            for score, sim_id, object_id in zip(scores, sim_ids, object_ids):
                self._scores.append(ContestScore(score, sim_id, object_id))

            self._has_awarded_winners = reader.read_bool(self.WINNERS_AWARDED_TOKEN, False)
            return True

    def has_user_submitted_entry(self):
        if self._scores:
            active_sim = services.get_active_sim()
            if active_sim is not None:
                sim_id = active_sim.sim_id
                for current_score_obj in self._scores:
                    if current_score_obj.sim_id == sim_id:
                        return True

            return False