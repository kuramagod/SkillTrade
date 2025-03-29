from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, DetailView, ListView, CreateView, DeleteView

from django.conf import settings
from .forms import CreationRequestForm, AddSkillProfileForm, AddSkill
from .models import PostModel, ExChangeRequestModel, UserSkills, ReviewModel, SkillsModel
from chat.models import Chat


class MainPage(ListView):
    model = PostModel
    template_name = 'main/main_page.html'
    context_object_name = 'posts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['skills'] = SkillsModel.objects.all()
        context['default_image'] = settings.DEFAULT_USER_IMAGE
        return context

    def get_queryset(self):
        skill_slug = self.kwargs.get('skill_slug')
        user = self.request.user
        if not user.is_authenticated:
            posts = PostModel.objects.all()
            if skill_slug:
                posts = posts.filter(wanted_skill__slug__exact=skill_slug)
            return posts
        posts = PostModel.objects.exclude(author=user)
        sent_requests = ExChangeRequestModel.objects.filter(receiver=user).values_list('sender_skill_id', flat=True)
        print(sent_requests)
        posts = posts.exclude(offered_skill_id__in=sent_requests)
        if skill_slug:
            posts = posts.filter(wanted_skill__slug__exact=skill_slug)
        return posts


class ProfilePage(LoginRequiredMixin, DetailView):
    model = ReviewModel
    template_name = 'main/profile.html'
    context_object_name = 'review'

    def get_object(self):
        username = self.kwargs.get('username')
        user = get_user_model().objects.get(username=username)
        return user

    def get_queryset(self):
        username = self.kwargs.get('username')
        author = get_user_model().objects.get(username=username)
        return PostModel.objects.filter(author=author)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs.get('username')
        user = get_user_model().objects.get(username=username)
        context['author'] = user
        context['review'] = self.get_queryset()
        context['default_image'] = settings.DEFAULT_USER_IMAGE
        return context


class RequestPage(LoginRequiredMixin, DetailView):
    model = ExChangeRequestModel
    template_name = 'main/request_page.html'
    context_object_name = 'requests'

    def get_object(self):
        username = self.kwargs.get('username')
        user = get_user_model().objects.get(username=username)
        return ExChangeRequestModel.objects.filter(sender=user) | ExChangeRequestModel.objects.filter(receiver=user)


class AddSkillProfile(CreateView):
    form_class = AddSkillProfileForm
    template_name = 'main/add_skill_profile.html'

    def get_success_url(self):
        return reverse_lazy('profile_page', kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        user = self.request.user
        skill = form.cleaned_data.get('skill')

        if UserSkills.objects.filter(user=user, skill=skill).exists():
            form.add_error(None, 'Навык уже существует')
            return self.form_invalid(form)

        form.instance.user = user
        form.instance.skill = skill
        return super().form_valid(form)


class AddSkill(CreateView):
    form_class = AddSkill
    template_name = 'main/add_skill.html'

    def get_success_url(self):
        return reverse_lazy('add_skill_profile')


class DeleteSkill(DeleteView):
    model = SkillsModel
    http_method_names = ['post']

    def get_queryset(self):
        return UserSkills.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy('profile_page', kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        self.object.delete()
        return redirect(self.get_success_url())


def start_chat(request, request_id):
    if request.method == 'POST':
        current_user = request.user
        exchange = get_object_or_404(ExChangeRequestModel, id=request_id)
        sender = exchange.sender
        if Chat.objects.filter(participants=current_user).filter(participants=sender).exists():
            chat_id = Chat.objects.filter(participants=current_user).filter(participants=sender).values()[0]['id']
            return redirect(reverse_lazy('chats:chat_room', args=[chat_id]))

        chat = Chat.objects.create()
        chat.participants.add(current_user, sender)
        chat.save()
        return JsonResponse({'success': True, 'current': current_user.username, 'sender': sender.username})

    return JsonResponse({'success': False})


@csrf_protect
@require_POST
def update_status(request):
    request_id = request.POST.get("request_id")
    status = request.POST.get("status")

    exchange_request = get_object_or_404(ExChangeRequestModel, id=request_id)
    exchange_request.status = status
    exchange_request.save()

    return JsonResponse({"message": "Статус обновлён", "new_status": status})


def create_request(request, post_id):
    if request.method == 'POST':
        try:
            receiver = request.user
            post = get_object_or_404(PostModel, id=post_id)
            sender = post.author
            sender_skill = post.offered_skill
            receiver_skill = UserSkills.objects.get(skill=post.wanted_skill)
            if ExChangeRequestModel.objects.filter(sender=sender, receiver=receiver, sender_skill=sender_skill,
                                                   receiver_skill=receiver_skill).exists():
                return JsonResponse({'success': False, 'error': 'Запрос уже существует'})

            exchange_request = ExChangeRequestModel.objects.create(
                sender=sender,
                receiver=receiver,
                sender_skill=sender_skill,
                receiver_skill=receiver_skill,
                status=ExChangeRequestModel.ExchangeStatus.PENDING
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
