from django import forms
from django.contrib.auth import user_logged_in, get_user, get_user_model
from slugify import slugify
from .models import ExChangeRequestModel, UserSkills, SkillsModel, PostModel


class CreationRequestForm(forms.ModelForm):
    class Meta:
        model = ExChangeRequestModel
        fields = ['sender', 'receiver', 'sender_skill', 'receiver_skill', 'status']


class AddSkillProfileForm(forms.ModelForm):
    class Meta:
        model = UserSkills
        fields = ['skill', 'level']
        labels = {
            'skill': 'Название умения',
            'level': 'Уровень владения'
        }


class AddSkill(forms.ModelForm):
    class Meta:
        model = SkillsModel
        fields = ['name']
        labels = {
            'name': 'Название умения',
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = slugify(instance.name)
        if commit:
            instance.save()
        return instance


class AddPostForm(forms.ModelForm):
    class Meta:
        model = PostModel
        fields = ['wanted_skill', 'offered_skill']
        labels = {
            'wanted_skill': 'Хотите получить навык',
            'offered_skill': 'Взамен предлагаете'
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['offered_skill'].queryset = UserSkills.objects.filter(user=user)