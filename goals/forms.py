from django import forms

class GoalForm(forms.Form):
    player = forms.CharField(max_length=100)
    team = forms.CharField(max_length=100)
    minute = forms.CharField(max_length=100)
    
