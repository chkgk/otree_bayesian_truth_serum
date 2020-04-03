from otree.api import Currency as c, currency_range, SubmissionMustFail
from . import pages
from ._builtin import Bot
from .models import Constants


class PlayerBot(Bot):
    def play_round(self):
        submissions = {
            1: {'question': 2, 'prediction1': 0.1, 'prediction2': 0.2, 'prediction3': 0.3, 'prediction4': 0.4},
            2: {'question': 3, 'prediction1': 0.5, 'prediction2': 0.3, 'prediction3': 0.1, 'prediction4': 0.1},
            3: {'question': 4, 'prediction1': 0.5, 'prediction2': 0.2, 'prediction3': 0.2, 'prediction4': 0.1}
        }

        correct_scores = {
            1: {'information_score': 0.3757, 'prediction_score': -0.1446, 'respondent_score': 0.2310},
            2: {'information_score': 0.6067, 'prediction_score': -0.8378, 'respondent_score': -0.2310},
            3: {'information_score': 0.7419, 'prediction_score': -0.7419, 'respondent_score': 0}
        }

        # test page
        # predictions do not sum to 1
        yield SubmissionMustFail(pages.TruthSerum, {'question': 2, 'prediction1': 0.1, 'prediction2': 0.2,
                                                    'prediction3': 0.3, 'prediction4': 0.5})
        # at least one entry == 0
        yield SubmissionMustFail(pages.TruthSerum, {'question': 2, 'prediction1': 0, 'prediction2': 0.2,
                                                    'prediction3': 0.3, 'prediction4': 0.5})

        # all good
        yield pages.TruthSerum, submissions[self.player.id_in_subsession]

        # check calculations
        assert round(self.player.information_score, 4) == correct_scores[self.player.id_in_subsession]['information_score']
        assert round(self.player.prediction_score, 4) == correct_scores[self.player.id_in_subsession]['prediction_score']
        assert round(self.player.respondent_score, 4) == correct_scores[self.player.id_in_subsession]['respondent_score']


        yield pages.Results
