

from django import forms

from competitions.models import Competition


LEVELS = [
    ('', 'all'),
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    ]

CTYPES = [
    ('', 'all'),
    ('Cup', 'Cup'),
    ('League', 'League'),
    ]

INTERNATIONAL = [
    (None, ''),
    (True, 'international'),
    (False, 'domestic')
    ]


CODE = [
    ('', 'all'),
    ('soccer', 'soccer'),
    ('indoor', 'indoor'),
    ('women', 'women'),
    ]

AREA = [
    ('', 'all'),
    ('Earth', 'Earth'),
    ('CONCACAF', 'CONCACAF'),
    ('CONMEBOL', 'CONMEBOL'),
    ('UEFA', 'UEFA'),
    ('AFC', 'AFC'),
    ('United States', 'United States'),
    ]
    

    

class CompetitionForm(forms.Form):

    #international = forms.ChoiceField(choices=INTERNATIONAL, required=False)
    code = forms.ChoiceField(choices=CODE, required=False)
    level = forms.ChoiceField(choices=LEVELS, required=False)
    ctype = forms.ChoiceField(choices=CTYPES, required=False, label='type')
    area = forms.ChoiceField(choices=AREA, required=False)


    
