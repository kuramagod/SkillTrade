from django.shortcuts import render
from django.views.generic import TemplateView, DetailView, ListView

from .models import PostModel, CategoryModel


class MainPage(ListView):
    model = PostModel
    template_name = 'main/main_page.html'
    context_object_name = 'posts'



class SkillCategory(ListView):
    model = PostModel
    template_name = 'main/main_page.html'
    context_object_name = 'post'

    def get_queryset(self):
        category_slug = self.kwargs['cat_slug']
        category = CategoryModel.objects.get(slug=category_slug)
        return PostModel.objects.filter(category_id=category.pk)
