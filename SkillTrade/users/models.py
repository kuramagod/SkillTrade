from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime



class User(AbstractUser):
    avatar = models.ImageField(upload_to="users/%Y/%m/%d/", blank=True, null=True, verbose_name='Аватарка')
    description = models.TextField(max_length=250, blank=True, null=True, verbose_name="Описание") # убрать None
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name="Город")
    rating = models.FloatField(verbose_name="Рейтинг", default=0.0)
    birth_date = models.DateField(verbose_name="Дата рождения", null=True, blank=True, default=datetime.date.today)
    age = models.IntegerField(verbose_name='Возраст', null=True, blank=True)

    def get_average_rating(self):
        reviews = self.target.all()
        if reviews.exists():
            return sum(r.rating for r in reviews) / reviews.count()
        return 0.0

    def save(self, *args, **kwargs):
        today = datetime.date.today()
        self.age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        super().save(*args, **kwargs)

