from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.urls import reverse
from slugify import slugify


class SkillsModel(models.Model):
    name = models.CharField(max_length=100,
                            verbose_name="Название")
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'
        ordering = ['name']

    def get_absolute_url(self):
        return reverse('skill_category', kwargs={'skill_slug': self.slug})


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

    def __str__(self):
        return self.skill.name

    class Meta:
        verbose_name = 'Навык пользователя'
        verbose_name_plural = 'Навыки пользователей'
        ordering = ['user']


class ExChangeRequestModel(models.Model):
    class ExchangeStatus(models.TextChoices):
        PENDING = 'Ожидание'
        ACCEPTED = 'Принято'
        DECLINED = 'Отклонено'
        ACTIVE = 'Активно'
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
    sender_skill = models.ForeignKey(UserSkills,
                             on_delete=models.SET_NULL,
                             null=True,
                             related_name="skill_sender")
    receiver_skill = models.ForeignKey(UserSkills,
                                     on_delete=models.SET_NULL,
                                     null=True,
                                     related_name="receiver_skill")
    status = models.CharField(max_length=10,
                              choices=ExchangeStatus.choices,
                              default=ExchangeStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_user = models.ManyToManyField(get_user_model(), null=True,
                                       related_name="reviewed_user")


    def __str__(self):
        return f"{self.sender.username}[{self.sender_skill.skill}] to {self.receiver.username}[{self.receiver_skill.skill}]"

    class Meta:
        verbose_name = 'Запрос обмена'
        verbose_name_plural = 'Запросы обмена'
        ordering = ['status']


class PostModel(models.Model):
    author = models.ForeignKey(get_user_model(),
                             on_delete=models.SET_NULL,
                             default=None,
                             null=True,
                             related_name="автор_поста")

    offered_skill = models.ForeignKey(UserSkills,
                             on_delete=models.SET_NULL,
                             null=True,
                             related_name="Предлагает")
    wanted_skill = models.ForeignKey(SkillsModel,
                             on_delete=models.SET_NULL,
                             null=True,
                             related_name="Запрашивает")
    created_at = models.DateTimeField(auto_now_add=True)
    responder = models.ManyToManyField(get_user_model(), null=True,
                                       related_name="responder")

    def __str__(self):
        return f"{self.author.username}[{self.offered_skill.skill}] to {self.wanted_skill.name}"

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['created_at']


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

    def __str__(self):
        return f"Отзыв к {self.exchange.sender_skill}|{self.exchange.receiver_skill} от {self.author.username}"

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['author']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        avg_rating = ReviewModel.objects.filter(target_user=self.target_user).aggregate(Avg('rating'))['rating__avg']
        self.target_user.rating = round(avg_rating, 1) if avg_rating is not None else 0.0
        self.target_user.save()
