from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView, DetailView, ListView

from .models import PostModel, CategoryModel


class MainPage(ListView):
    model = PostModel
    template_name = 'main/main_page.html'
    context_object_name = 'posts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = CategoryModel.objects.all()
        return context



class SkillCategory(ListView):
    model = PostModel
    template_name = 'main/main_page.html'
    context_object_name = 'posts'

    def get_queryset(self):
        category_slug = self.kwargs['cat_slug']
        category = CategoryModel.objects.get(slug=category_slug)
        return PostModel.objects.filter(category_id=category.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = CategoryModel.objects.all()
        return context


class ProfilePage(LoginRequiredMixin, DetailView):
    model = PostModel
    template_name = 'main/profile.html'
    context_object_name = 'post'

    def get_object(self):
        username = self.kwargs.get('username')
        user = get_user_model().objects.get(username=username)
        return user

