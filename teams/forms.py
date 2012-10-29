from django import forms

from bios.models import Bio
from competitions.models import Competition
from games.models import Game
from places.models import Stadium, City, State, Country
from stats.models import TeamStat
from teams.models import Team

COMPETITIONS = []
TEAMS = []    

RESULTS = [
    ('', ''),
    ('w', 'win'),
    ('t', 'tie'),
    ('l', 'loss'),
    ]


class TeamStatForm(forms.Form):

    def __init__(self, team, *args, **kwargs):
        super(TeamStatForm, self).__init__(*args, **kwargs)

        team_stats = TeamStat.objects.filter(team=team)
        bio_ids = [e[0] for e in team_stats.values_list('player__id')]
        bios = Bio.objects.filter(id__in=bio_ids)

        birthplace_ids = bios.exclude(birthplace=None).order_by('birthplace__id').distinct('birthplace__id').values_list('birthplace__id')
        cities = City.objects.filter(id__in=birthplace_ids)
        #self.fields['birthplace'] = forms.ModelChoiceField(queryset=cities, required=False)

        state_ids = cities.order_by('state__id').distinct('state__id').values_list('state__id')
        states = State.objects.filter(id__in=state_ids)
        self.fields['birth_state'] = forms.ModelChoiceField(queryset=states, required=False)        

        """
        birth_country_ids = bios.exclude(birth_country=None).order_by('birth_country__id').distinct('birth_country__id').values_list('birth_country__id')
        countries = Country.objects.filter(id__in=birth_country_ids)
        self.fields['birth_country'] = forms.ModelChoiceField(queryset=countries, required=False)        
        """
    

class TeamGameForm(forms.Form):

    def __init__(self, team, *args, **kwargs):
        super(TeamGameForm, self).__init__(*args, **kwargs)

        games = Game.objects.team_filter(team)

        cids = games.order_by('competition__id').distinct('competition__id').values_list('competition__id')
        competitions = Competition.objects.filter(id__in=cids)
        self.fields['competition'] = forms.ModelChoiceField(queryset=competitions, required=False)        

        stadium_ids = games.exclude(stadium=None).order_by('stadium__id').distinct('stadium__id').values_list('stadium__id')
        stadiums = Stadium.objects.filter(id__in=stadium_ids)
        self.fields['stadium'] = forms.ModelChoiceField(queryset=stadiums, required=False)        

        gt1 = games.order_by('team1__id').distinct('team1__id')
        gt2 = games.order_by('team2__id').distinct('team2__id')
        tids = [e[0] for e in gt1.values_list('team1')] + [e[0] for e in gt2.values_list('team2')]
        teams = Team.objects.filter(id__in=tids)
        self.fields['opponent'] = forms.ModelChoiceField(queryset=teams, required=False)

    result = forms.ChoiceField(choices=RESULTS, required=False)


    
