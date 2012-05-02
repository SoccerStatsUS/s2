from django import forms

class GameSearchForm(forms.Form):
    
    team = forms.CharField(max_length=100)
    competition = forms.CharField(max_length=100)
    year = forms.IntegerField()
    stadium = forms.CharField(max_length=100)
    referee = forms.CharField(max_length=100)
    attendance_min = forms.IntegerField()
    atendance_max = forms.IntegerField()


class StatSearchForm(forms.Form):
    
    team = forms.CharField(max_length=100)
    competition = forms.CharField(max_length=100)
    year = forms.IntegerField()


class GoalSearchForm(forms.Form):
    
    team = forms.CharField(max_length=100)
    competition = forms.CharField(max_length=100)
    year = forms.IntegerField()

class LineupSearchForm(forms.Form):
    
    team = forms.CharField(max_length=100)
    competition = forms.CharField(max_length=100)
    year = forms.IntegerField()
