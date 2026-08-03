from django import forms

from transactions.models import Transaction


class TransactionForm(forms.Form):

    ttype = forms.ChoiceField(label='type', required=False, choices=())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Built from the data rather than hardcoded: the vocabulary is still
        # being cleaned up in usd1_data and this should track it.
        types = Transaction.objects.exclude(ttype='').values_list(
            'ttype', flat=True).distinct().order_by('ttype')

        self.fields['ttype'].choices = [('', 'all')] + [(t, t) for t in types]
