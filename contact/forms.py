
from django import forms


class ContactForm(forms.Form):
    email = forms.EmailField(required=False)
    message = forms.CharField(widget=forms.Textarea())

