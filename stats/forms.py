from django import forms

class StatForm(forms.Form):
    name = forms.CharField(max_length=100)
    team = forms.CharField(max_length=100)
    competition = forms.CharField(max_length=100)
    season = forms.CharField(max_length=100)

    
