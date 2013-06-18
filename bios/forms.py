from django import forms

from competitions.models import Competition
from lineups.models import Appearance
from stats.models import GameStat
from teams.models import Team

COMPETITIONS = []
TEAMS = []    

RESULTS = [
    ('', ''),
    ('w', 'win'),
    ('t', 'tie'),
    ('l', 'loss'),
    ]

    

class BioGameStatForm(forms.Form):

    def __init__(self, bio, *args, **kwargs):
        super(BioGameStatForm, self).__init__(*args, **kwargs)

        ac = GameStat.objects.filter(player=bio).order_by('game__competition__id').distinct('game__competition__id')
        competitions = Competition.objects.filter(id__in=ac.values_list('game__competition__id'))
        self.fields['competition'] = forms.ModelChoiceField(queryset=competitions, required=False)        

        at = GameStat.objects.filter(player=bio).order_by('team__id').distinct('team__id')
        teams = Team.objects.filter(id__in=at.values_list('team__id'))
        self.fields['team'] = forms.ModelChoiceField(queryset=teams, required=False)

        # Add opponent field back into appearance...or team stat.
        #at = Appearance.objects.filter(player=bio).order_by('opponent__id').distinct('opponent__id')
        #teams = Team.objects.filter(id__in=at.values_list('opponents__id'))
        #self.fields['opponent'] = forms.ModelChoiceField(queryset=teams, required=False)

    starter = forms.BooleanField(required=False)
    result = forms.ChoiceField(choices=RESULTS, required=False)


    
