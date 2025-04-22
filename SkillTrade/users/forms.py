from datetime import date

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class DateVerification:
    allowed_date = date(date.today().year - 13, date.today().month, date.today().day)
    code = 'date_verification'

    def __init__(self, message=None):
        self.message = message if message else f"Возраст должен быть не менее 13 полных лет."

    def __call__(self, *args, **kwargs):
        if self.allowed_date < args[0]:
            raise ValidationError(self.message, code=self.code)


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label="Логин",
                               widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label="Пароль",
                               widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta:
        model = get_user_model()

    fields = ['username', 'password']


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label="Логин")
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput())
    password2 = forms.CharField(label="Повтор пароля", widget=forms.PasswordInput())
    birth_date = forms.DateField(label='Дата рождения', validators=([DateVerification(), ]))

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'gender', 'first_name', 'last_name', 'birth_date', 'password1', 'password2']
        labels = {
            'email': 'E-mail',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }

        def clean_email(self):
            email = self.cleaned_data['email']
            if get_user_model().objects.filter(email=email).exists():
                raise forms.ValidationError("Такой E-mail уже существует!")
            return email


class ProfileUserForm(forms.ModelForm):
    username = forms.CharField(disabled=True, label="Логин")
    email = forms.CharField(disabled=True, label="E-mail")
    birth_date = forms.DateField(label='Дата рождения', validators=([DateVerification(), ]))

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'gender', 'first_name', 'last_name', 'description', 'location', 'birth_date', 'avatar']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }
