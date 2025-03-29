from django import forms
from slugify import slugify
from .models import ExChangeRequestModel, UserSkills, SkillsModel


class CreationRequestForm(forms.ModelForm):
    class Meta:
        model = ExChangeRequestModel
        fields = ['sender', 'receiver', 'sender_skill', 'receiver_skill', 'status']


class AddSkillProfileForm(forms.ModelForm):
    class Meta:
        model = UserSkills
        fields = ['skill', 'level']


class AddSkill(forms.ModelForm):
    class Meta:
        model = SkillsModel
        fields = ['name']

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = slugify(instance.name)  # Генерация slug
        if commit:
            instance.save()
        return instance