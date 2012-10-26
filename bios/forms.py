from django import forms

from competitions.models import Competition
from lineups.models import Appearance
from teams.models import Team

COMPETITIONS = []
TEAMS = []    

RESULTS = [
    ('', ''),
    ('win', 'win'),
    ('tie', 'tie'),
    ('loss', 'loss'),
    ]

    

class BioAppearanceForm(forms.Form):

    def __init__(self, bio, *args, **kwargs):
        super(BioAppearanceForm, self).__init__(*args, **kwargs)

        ac = Appearance.objects.filter(player=bio).order_by('game__competition__id').distinct('game__competition__id')
        competitions = Competition.objects.filter(id__in=ac.values_list('game__competition__id'))
        self.fields['competitions'] = forms.ModelChoiceField(queryset=competitions, required=False)        

        at = Appearance.objects.filter(player=bio).order_by('team__id').distinct('team__id')
        teams = Team.objects.filter(id__in=at.values_list('team__id'))
        self.fields['teams'] = forms.ModelChoiceField(queryset=teams, required=False)



    starts = forms.BooleanField(required=False)
    result = forms.ChoiceField(choices=RESULTS, required=False)


    
