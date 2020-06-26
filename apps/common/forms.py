from django import forms

from .utils import send_contact_us


class ContactUsForm(forms.Form):
    name = forms.CharField()
    email = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)

    def send_contact_email(self):
        send_contact_us(self.cleaned_data)


class SubscriptionForm(forms.Form):
    email = forms.EmailField()
