from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as c,
    currency_range,
)

import json
import math, statistics, numpy as np

author = 'Christian König gen. Kersting'

doc = """
Implementation of Prelec's (2004) Baysean Truth Serum (BTS) for a likert scale
"""

# helper functions
def _geomean(xs):
    return math.exp(math.fsum(math.log(x) for x in xs) / len(xs))

def _likert_to_indicators(choice, likert_choice_options):
    return [choice == option for option in likert_choice_options]

class Constants(BaseConstants):
    name_in_url = 'bts'
    players_per_group = None
    num_rounds = 1

    # define choice options and alpha
    alpha = 1
    likert_choices = [1, 2, 3, 4]


class Subsession(BaseSubsession):
    faith_based = models.BooleanField()

    def creating_session(self):
        self.faith_based = self.session.config.get('faith_based', False)

    def calculate_scores(self):
        # helper function that is required for the new oTree format that only allows you to name a function
        # to be called from the wait page (after_all_players_arrive was a method in earlier versions).

        # The function requires string name of question field, list of string names of prediction fields,
        # and a list of choices the participants could select from
        self.calculate_prelec('x1', ['p1_1', 'p1_2', 'p1_3', 'p1_4'], Constants.likert_choices)


    def calculate_prelec(self, belief_field: str, prediction_fields: list, choices: list, alpha=1):
        players = self.get_players()
        if len(choices) != len(prediction_fields):
            raise KeyError('There should be an equaly number of possible answer choices and prediction fields')

        # population endorsement frequencies
        x_bar = []
        for i, c in enumerate(choices):
            indicators = []
            for p in players:
                field = getattr(p, belief_field)
                indicators.append(_likert_to_indicators(field, choices)[i])

            x_bar.append(statistics.mean(indicators))

        # geometric averages of predicted frequency
        y_bar = []
        for pf in prediction_fields:
            y_bar.append(_geomean([getattr(p, pf) for p in players])) # predictions must be >0 otherwise geo mean breaks

        # information scores per choice
        information_scores = []
        for i, c in enumerate(choices):
            if x_bar[i] == 0 or y_bar[i] == 0:
                information_scores.append(0)
            else:
                information_scores.append(math.log(x_bar[i] / y_bar[i]))


        # individual scores
        for p in players:
            field = getattr(p, belief_field)
            indicators = _likert_to_indicators(field, choices)
            p.information_score = np.dot(indicators, information_scores)

            pf = [getattr(p, f) for f in prediction_fields]

            # prediction score
            ps = []
            for i, c in enumerate(choices):
                if x_bar[i] != 0:
                    res = x_bar[i] * math.log(pf[i] / x_bar[i])
                else:
                    res = 0
                ps.append(res)

            p.prediction_score = sum(ps)
            p.respondent_score = p.information_score + alpha * p.prediction_score


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # needed for prelec results.
    information_score = models.FloatField()
    prediction_score = models.FloatField()
    respondent_score = models.FloatField()

    # Question 1
    x1 = models.IntegerField(choices=Constants.likert_choices, widget=widgets.RadioSelectHorizontal(),
                             verbose_name="This is the question you are after!")

    # Predictions for question 1, one for each likert option
    p1_1 = models.FloatField(min=0, max=1, verbose_name="How likely are others to answer %s?" % Constants.likert_choices[0])
    p1_2 = models.FloatField(min=0, max=1, verbose_name="How likely are others to answer %s?" % Constants.likert_choices[1])
    p1_3 = models.FloatField(min=0, max=1, verbose_name="How likely are others to answer %s?" % Constants.likert_choices[2])
    p1_4 = models.FloatField(min=0, max=1, verbose_name="How likely are others to answer %s?" % Constants.likert_choices[3])



