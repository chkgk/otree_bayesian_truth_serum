from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class TruthSerum(Page):
    form_model = 'player'
    form_fields = ['x1', 'p1_1', 'p1_2', 'p1_3', 'p1_4']

    def error_message(self, values):
        prediction_fields = ['p1_1', 'p1_2', 'p1_3', 'p1_4']
        prediction_values = [v for k, v in values.items() if k in prediction_fields]

        # if any individual value is 0, the geometric mean is not defined
        if any([pv == 0 for pv in prediction_values]):
            return "All predictions must be strictly larger than zero."

        # sum of values must be 1
        if round(sum(prediction_values), 4) != 1:
            return "The predictions must sum up to 1."


class ResultsWaitPage(WaitPage):
    wait_for_all_groups = True
    after_all_players_arrive = 'calculate_scores' # on subsession if wait_for_all_groups = True


class Results(Page):
    pass


page_sequence = [TruthSerum, ResultsWaitPage, Results]
