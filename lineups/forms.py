from django import forms

class AppearanceForm(forms.Form):
    player = forms.CharField(max_length=100)
    team = forms.CharField(max_length=100)
    
    #date = forms.CharField(max_length=100)

    on = forms.CharField(max_length=100)
    off = forms.CharField(max_length=100)

    age = forms.CharField(max_length=100)
