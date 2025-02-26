from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    avatar = models.ImageField(upload_to="users/%Y/%m/%d/", blank=True, null=True, verbose_name='Аватарка')
    description = models.CharField(max_length=250, blank=True, null=True, verbose_name="Описание")
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name="Расположение")
    rating = models.FloatField(verbose_name="Рейтинг", default=0.0)

    def get_average_rating(self):
        reviews = self.target.all()
        if reviews.exists():
            return sum(r.rating for r in reviews) / reviews.count()
        return 0.0
