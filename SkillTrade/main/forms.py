from django import forms

from .models import ExChangeRequestModel, UserSkills, SkillsModel


class CreationRequestForm(forms.ModelForm):
    class Meta:
        model = ExChangeRequestModel
        fields = ['sender', 'receiver', 'sender_skill', 'receiver_skill', 'status']


class AddSkillForm(forms.ModelForm):
    class Meta:
        model = UserSkills
        fields = ['skill', 'level']
