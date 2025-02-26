from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse


class SkillsModel(models.Model):
    name = models.CharField(max_length=100,
                            verbose_name="Название")


class UserSkills(models.Model):
    class SkillLevel(models.TextChoices):
        BEGINNER = 'Новичок'
        INTERMEDIATE = 'Средний'
        EXPERT = 'Эксперт'

    user = models.ForeignKey(get_user_model(),
                             on_delete=models.SET_NULL,
                             null=True,
                             default=None,
                             related_name="skills")
    skill = models.ForeignKey(SkillsModel,
                              on_delete=models.SET_NULL,
                              null=True)
    level = models.CharField(max_length=10,
                             choices=SkillLevel.choices)


class ExChangeRequestModel(models.Model):
    class ExchangeStatus(models.TextChoices):
        PENDING = 'Ожидание'
        ACCEPTED = 'Принято'
        DECLINED = 'Отклонено'
        COMPLETED = 'Завершено'

    sender = models.ForeignKey(get_user_model(),
                             on_delete=models.SET_NULL,
                             null=True,
                             default=None,
                             related_name="sender")
    receiver = models.ForeignKey(get_user_model(),
                             on_delete=models.SET_NULL,
                             null=True,
                             default=None,
                             related_name="received")
    sender_skill = models.ForeignKey(SkillsModel,
                             on_delete=models.SET_NULL,
                             null=True,
                             related_name="skill_sender")
    receiver_skill = models.ForeignKey(SkillsModel,
                                     on_delete=models.SET_NULL,
                                     null=True,
                                     related_name="receiver_skill")
    status = models.CharField(max_length=10,
                              choices=ExchangeStatus.choices,
                              default=ExchangeStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)


class PostModel(models.Model):
    author = models.ForeignKey(get_user_model(),
                             on_delete=models.SET_NULL,
                             default=None,
                             null=True,
                             related_name="author_post")

    offered_skill = models.ForeignKey(SkillsModel,
                             on_delete=models.SET_NULL,
                             null=True,
                             related_name="offered_skill")
    wanted_skill = models.ForeignKey(SkillsModel,
                             on_delete=models.SET_NULL,
                             null=True,
                             related_name="wanted_skill")

    created_at = models.DateTimeField(auto_now_add=True)

class ReviewModel(models.Model):
    author = models.ForeignKey(get_user_model(),
                             on_delete=models.SET_NULL,
                             null=True,
                             related_name="author_review")
    target_user = models.ForeignKey(get_user_model(),
                             on_delete=models.SET_NULL,
                             null=True,
                             related_name="target_user")
    exchange = models.ForeignKey(ExChangeRequestModel,
                             on_delete=models.SET_NULL,
                             null=True)
    rating = models.PositiveSmallIntegerField(verbose_name="Рейтинг", choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(max_length=500, verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True)


class CategoryModel(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def get_absolute_url(self):
        return reverse('categories', kwargs={'cat_slug': self.slug})
