from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime


class User(AbstractUser):
    class Gender(models.TextChoices):
        MALE = 'M', 'Мужской'
        FEMALE = 'F', 'Женский'
        NOT_SPECIFIED = 'N', 'Не указан'

    avatar = models.ImageField(upload_to="users/%Y/%m/%d/", blank=True, null=True, verbose_name='Аватарка', default=settings.DEFAULT_USER_IMAGE)
    description = models.TextField(max_length=250, blank=True, null=True, verbose_name="Описание")
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name="Город")
    rating = models.FloatField(verbose_name="Рейтинг", default=0.0)
    birth_date = models.DateField(verbose_name="Дата рождения", null=True, blank=True, default=datetime.date.today)
    age = models.IntegerField(verbose_name='Возраст', null=True, blank=True)
    gender = models.CharField(max_length=1, choices=Gender.choices, default=Gender.NOT_SPECIFIED, verbose_name='Пол')

    def save(self, *args, **kwargs):
        today = datetime.date.today()
        self.age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        super().save(*args, **kwargs)