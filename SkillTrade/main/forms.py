from django import forms

from .models import ExChangeRequestModel


class CreationRequestForm(forms.ModelForm):
    class Meta:
        model = ExChangeRequestModel
        fields = ['sender', 'receiver', 'sender_skill', 'receiver_skill', 'status']