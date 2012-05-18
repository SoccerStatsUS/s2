
from django import forms


class ContactForm(forms.Form):
    email = forms.EmailField(required=False, label="Email (optional)")
    message = forms.CharField(widget=forms.Textarea())

