from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse


class SkillsModel(models.Model):
    name = models.CharField(max_length=100,
                            verbose_name="Название")
    category = models.ForeignKey('CategoryModel', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'
        ordering = ['name']


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
        return self.user

    class Meta:
        verbose_name = 'Навык пользователя'
        verbose_name_plural = 'Навыки пользователей'
        ordering = ['user']


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

    def __str__(self):
        return self.status

    class Meta:
        verbose_name = 'Запрос обмена'
        verbose_name_plural = 'Запросы обмена'
        ordering = ['status']


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

    def __str__(self):
        return self.author.username

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
        return self.author

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['author']


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
