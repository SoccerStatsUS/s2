

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
    (None, ''),
    (True, 'international'),
    (False, 'domestic')
    ]


CODE = [
    ('soccer', 'soccer'),
    ('indoor', 'indoor'),
    ('', ''),
    ]

AREA = [
    ('', ''),
    ('Earth', 'Earth'),
    ('CONCACAF', 'CONCACAF'),
    ('CONMEBOL', 'CONMEBOL'),
    ('United States', 'United States'),
    ('Canada', 'Canada'),
    ]
    

    

class CompetitionForm(forms.Form):

    #international = forms.ChoiceField(choices=INTERNATIONAL, required=False)
    code = forms.ChoiceField(choices=CODE, required=False)
    level = forms.ChoiceField(choices=LEVELS, required=False)
    ctype = forms.ChoiceField(choices=CTYPES, required=False)
    area = forms.ChoiceField(choices=AREA, required=False)


    