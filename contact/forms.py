
from django import forms


class ContactForm(forms.Form):
    email = forms.EmailField(required=False, label="Email (not required)")
    message = forms.CharField(widget=forms.Textarea())

