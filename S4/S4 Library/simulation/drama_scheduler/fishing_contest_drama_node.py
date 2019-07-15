# uncompyle6 version 3.3.5
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.1 (v3.7.1:260ec2c36a, Oct 20 2018, 14:57:15) [MSC v.1915 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\drama_scheduler\fishing_contest_drama_node.py
# Size of source mod 2**32: 11612 bytes
from dataclasses import dataclass
from date_and_time import create_time_span
from drama_scheduler.festival_drama_node import FestivalDramaNode
from event_testing.resolver import SingleSimResolver
from sims4.tuning.tunable import TunableReference, TunableSimMinute, TunableRange, TunableInterval, TunableList
from ui.ui_dialog_notification import UiDialogNotification, TunableUiDialogNotificationSnippet
import alarms, services, sims4
logger = sims4.log.Logger('DramaNode', default_owner='msundaram')

@dataclass
class FishingContestScore:
    __annotations__['score'] = float
    __annotations__['sim_id'] = int

    def __init__(self, score, sim_id=0):
        self.score = score
        self.sim_id = sim_id


class FishingContestDramaNode(FestivalDramaNode):
    SIM_ID_SAVE_TOKEN = 'sim_ids'
    SCORE_SAVE_TOKEN = 'scores'
    WINNERS_AWARDED_TOKEN = 'awarded'
    USER_SUBMITTED_TOKEN = 'submitted'
    INSTANCE_TUNABLES = {'_score_update_frequency':TunableSimMinute(description='\n            How often a fake new score should be submitted to the fishing tournament.\n            ',
       default=30,
       minimum=0), 
     '_score_update_value_interval':TunableInterval(description='\n            When a fake new score is submitted, the interval determining what the value should be.\n            ',
       tunable_type=float,
       default_lower=0,
       default_upper=10,
       minimum=0), 
     '_scores_to_consider':TunableRange(description='\n            How many scores should be considered for the prizes.\n            ',
       tunable_type=int,
       default=3,
       minimum=1), 
     '_win_rewards':TunableList(description='\n            List of Loots applied to the winners of the contest. Index refers to the \n            winner who receives that loot. 1st, 2nd, 3rd, etc.\n            ',
       tunable=TunableReference(description='\n                A reference to a loot that will be applied to one of the winners.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', ))), 
     '_win_notifications':TunableList(description='\n            List of notifications applied to the winners of the contest. These display regardless of whether\n            the rewards have already been given out. Index refers to the winners of that rank. 1st, 2nd, 3rd, etc.\n            ',
       tunable=UiDialogNotification.TunableFactory()), 
     '_lose_notification':TunableUiDialogNotificationSnippet(description='\n            Notification displayed if there are no player sim winners of the contest. Only displayed if the \n            winners are requested, not at the end of the festival.\n            '), 
     '_contest_duration':TunableSimMinute(description='\n            The amount of time in sim minutes that we should allow scores to be\n            submitted to the contest and that we should submit fake scores.\n            ',
       default=60,
       minimum=0)}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._scores = []
        self._score_alarm = None
        self._has_awarded_winners = False
        self._has_user_submitted_fish = False

    def _try_and_start_festival(self):
        super()._try_and_start_festival()
        self._setup_score_add_alarm()

    def _setup_score_add_alarm(self):
        duration = create_time_span(minutes=(self._score_update_frequency))
        self._score_alarm = alarms.add_alarm(self, duration, self._score_add_callback, True)

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
        duration = create_time_span(minutes=(self._contest_duration + self.pre_festival_duration))
        time_left_to_go = duration - time_since_started
        return time_left_to_go

    def _add_fake_score(self):
        score = self._score_update_value_interval.random_float()
        self.add_score(sim_id=0, score=score)

    def add_score(self, sim_id, score):
        scores = self._scores
        if sim_id == 0:
            scores.append(FishingContestScore(score, sim_id))
        else:
            self._has_user_submitted_fish = True
            found_score = False
            for current_score_obj in scores:
                if current_score_obj.sim_id == sim_id:
                    current_score = current_score_obj.score
                    if current_score >= score:
                        return
                    current_score_obj.score = score
                    found_score = True
                    break

            if not found_score:
                scores.append(FishingContestScore(score, sim_id))
            scores.sort(key=(lambda item: item.score), reverse=True)
            if len(scores) > self._scores_to_consider:
                scores = scores[:self._scores_to_consider]
                self._scores = scores
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

    def award_winners(self, sim_info, resolver, show_fallback_dialog=False):
        valid_sim_won = False
        sim_info_manager = services.sim_info_manager()
        for score, award in zip(self._scores, self._win_rewards):
            if not score.sim_id is None:
                if score.sim_id is 0:
                    pass
                elif not sim_info_manager.is_sim_id_valid(score.sim_id):
                    pass
                else:
                    valid_sim_won = True
                    sim = sim_info_manager.get(score.sim_id)
                    resolver = SingleSimResolver(sim)
                    if not self._has_awarded_winners:
                        award.apply_to_resolver(resolver)
                    rank = self._scores.index(score)
                    if rank >= len(self._win_notifications):
                        pass
                    else:
                        notification = self._win_notifications[rank]
                        dialog = notification(sim, target_sim_id=(score.sim_id),
                          resolver=resolver)
                        dialog.show_dialog()

        if show_fallback_dialog:
            if not valid_sim_won:
                dialog = self._lose_notification(sim_info, target_sim_id=(sim_info.id if sim_info is not None else None),
                  resolver=resolver)
                dialog.show_dialog()
            self._has_awarded_winners = True

    def cleanup(self, from_service_stop=False):
        super().cleanup(from_service_stop=from_service_stop)
        if self._score_alarm is not None:
            alarms.cancel_alarm(self._score_alarm)
            self._score_alarm = None

    def complete(self):
        super().complete()
        if self.is_during_pre_festival():
            return
        if self.is_during_contest():
            return
        if self._has_awarded_winners:
            return
        self.award_winners(None, None, show_fallback_dialog=(self._has_user_submitted_fish))

    def _save_custom_data(self, writer):
        super()._save_custom_data(writer)
        if self._scores and len(self._scores) == 0:
            return
        scores = []
        sim_ids = []
        for score in self.get_scores_gen():
            scores.append(score.score)
            sim_ids.append(score.sim_id)

        writer.write_floats(self.SCORE_SAVE_TOKEN, scores)
        writer.write_uint64s(self.SIM_ID_SAVE_TOKEN, sim_ids)
        writer.write_bool(self.WINNERS_AWARDED_TOKEN, self._has_awarded_winners)
        writer.write_bool(self.USER_SUBMITTED_TOKEN, self._has_user_submitted_fish)

    def _load_custom_data(self, reader):
        super_success = super()._load_custom_data(reader)
        if not super_success:
            return False
        else:
            self._scores = []
            scores = reader.read_floats(self.SCORE_SAVE_TOKEN, None)
            sim_ids = reader.read_uint64s(self.SIM_ID_SAVE_TOKEN, None)
            for score, sim_id in zip(scores, sim_ids):
                self._scores.append(FishingContestScore(score, sim_id))

            self._has_awarded_winners = reader.read_bool(self.WINNERS_AWARDED_TOKEN, False)
            self._has_user_submitted_fish = reader.read_bool(self.USER_SUBMITTED_TOKEN, False)
            return True