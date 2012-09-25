

from django import forms

from competitions.models import Competition


LEVELS = [
    ('', ''),
    (1, 1),
    (2, 2),
    (3, 3),
    ]

CTYPES = [
    ('', ''),
    ('Cup', 'Cup'),
    ('League', 'League'),
    ]

INTERNATIONAL = [
    (True, 'international'),
    (False, 'domestic')
    ]


CODE = [
    ('indoor', 'indoor'),
    ('soccer', 'soccer'),
    ]

class CompetitionForm(forms.Form):

    international = forms.ChoiceField(choices=INTERNATIONAL, required=False)
    level = forms.ChoiceField(choices=LEVELS, required=False)
    ctype = forms.ChoiceField(choices=CTYPES, required=False)
    

    
