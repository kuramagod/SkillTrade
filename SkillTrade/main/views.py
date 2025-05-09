from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Q
from django.dispatch import receiver
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, CreateView, DeleteView


from .forms import AddSkillProfileForm, AddSkill, AddPostForm, AddReviewForm
from .models import PostModel, ExChangeRequestModel, UserSkills, ReviewModel, SkillsModel
from chat.models import Chat

from .utils import DefaultImageMixin


class MainPage(DefaultImageMixin, ListView):
    model = PostModel
    template_name = 'main/main_page.html'
    context_object_name = 'posts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        existing_offered_post_skills = PostModel.objects.values_list("offered_skill__skill__name", flat=True).distinct()
        existing_wanted_post_skills = PostModel.objects.values_list("wanted_skill__name", flat=True).distinct()
        context['offered_skills'] = SkillsModel.objects.filter(name__in=existing_offered_post_skills)
        context['wanted_skills'] = SkillsModel.objects.filter(name__in=existing_wanted_post_skills)
        return context

    def get_queryset(self):
        skill_slug = self.request.GET.get('skill')
        user = self.request.user
        if not user.is_authenticated:
            posts = PostModel.objects.all()
            if skill_slug:
                posts = posts.filter(wanted_skill__slug=skill_slug) | posts.filter(offered_skill__skill__slug=skill_slug)
            return posts
        posts = PostModel.objects.exclude(author=user).exclude(responder=user)
        current_user_skills = UserSkills.objects.filter(user=user).values_list('skill', flat=True)
        posts = posts.filter(wanted_skill__in=current_user_skills)
        if skill_slug:
            posts = posts.filter(wanted_skill__slug=skill_slug) | posts.filter(offered_skill__skill__slug=skill_slug)
        return posts


class ProfilePage(LoginRequiredMixin, DefaultImageMixin, DetailView):
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
        context['reviews'] = ReviewModel.objects.filter(target_user=user)
        return context


class RequestPage(LoginRequiredMixin, DefaultImageMixin, ListView):
    model = ExChangeRequestModel
    template_name = 'main/request_page.html'
    context_object_name = 'requests'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs.get('username')
        user = get_user_model().objects.get(username=username)
        exchanges = ExChangeRequestModel.objects.exclude(reviewed_user=user)
        context['incoming_requests'] = exchanges.filter(sender=user).exclude(status__in=['Активно', 'Завершено', 'Отклонено'])
        context['sent_requests'] = exchanges.filter(receiver=user).exclude(status__in=['Активно', 'Завершено', 'Отклонено'])
        context['active_requests'] = exchanges.filter(status='Активно').filter(Q(receiver=user) | Q(sender=user))
        context['completed_requests'] = exchanges.filter(status='Завершено').filter(Q(receiver=user) | Q(sender=user))
        return context

    def dispatch(self, request, *args, **kwargs): # Перехватывает HTTP-запрос, проверяя является ли пользователь владельцем страницы, иначе пересылает на главную.
        username = kwargs.get('username')
        if request.user.username != username:
            return HttpResponseRedirect(reverse_lazy('main_page'))
        return super().dispatch(request, *args, **kwargs)


class AddSkillProfile(DefaultImageMixin, CreateView):
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


class UserPosts(LoginRequiredMixin, DefaultImageMixin, ListView):
    model = PostModel
    template_name = 'main/user_posts.html'
    context_object_name = 'posts'

    def get_queryset(self):
        user = self.request.user
        return PostModel.objects.filter(author=user)

    def dispatch(self, request, *args, **kwargs):
        username = kwargs.get('username')
        if request.user.username != username:
            return HttpResponseRedirect(reverse_lazy('main_page'))
        return super().dispatch(request, *args, **kwargs)


class AddPost(DefaultImageMixin, CreateView):
    form_class = AddPostForm
    template_name = 'main/add_post.html'
    success_url = reverse_lazy('main_page')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        offered_skill = form.cleaned_data.get('offered_skill')
        wanted_skill = form.cleaned_data.get('wanted_skill')

        if PostModel.objects.filter(author=user, offered_skill=offered_skill, wanted_skill=wanted_skill).exists():
            form.add_error(None, 'Такой пост уже существует')
            return self.form_invalid(form)

        form.instance.author = user
        form.instance.offered_skill = offered_skill
        form.instance.wanted_skill = wanted_skill
        return super().form_valid(form)


class DeletePost(DeleteView):
    model = PostModel
    http_method_names = ['post']

    def get_success_url(self):
        return reverse_lazy('user_posts', kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        self.object.delete()
        return redirect(self.get_success_url())


class AddReview(DefaultImageMixin, CreateView):
    form_class = AddReviewForm
    template_name = 'main/add_review.html'
    success_url = reverse_lazy('main_page')

    def get_exchange(self):
        return get_object_or_404(ExChangeRequestModel, id=self.kwargs.get('exchange_id'))

    def get_target_user(self, exchange):
        current_user = self.request.user
        return exchange.sender if current_user == exchange.receiver else exchange.receiver

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exchange = self.get_exchange()
        context['target_user'] = self.get_target_user(exchange)
        print(exchange.reviewed_user)
        return context

    def form_valid(self, form):
        exchange = self.get_exchange()
        current_user = self.request.user
        form.instance.author = current_user
        form.instance.target_user = self.get_target_user(exchange)
        form.instance.exchange = exchange

        response = super().form_valid(form)  # Сохраняем форму

        exchange.reviewed_user.add(current_user)  # Добавляем пользователя, затем проверяем и удаляем обмен.
        if exchange.reviewed_user.count() == 2:
            exchange.delete()

        return response


class AddSkill(DefaultImageMixin, CreateView):
    form_class = AddSkill
    template_name = 'main/add_skill.html'

    def get_success_url(self):
        return reverse_lazy('add_skill_profile')


class DeleteSkill(DefaultImageMixin, DeleteView):
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
        receiver = exchange.receiver
        check_name = f"Чат {exchange.sender_skill} - {exchange.receiver_skill}" # название чата которое дается при создании, для проверки
        if Chat.objects.filter(participants=current_user).filter(participants=sender).filter(name=check_name).exists():
            if exchange.status != 'Активно':
                exchange.status = 'Активно'
                exchange.save()
            chat_id = Chat.objects.filter(participants=current_user).filter(participants=sender).filter(name=check_name).values()[0]['id']
            return redirect(reverse_lazy('chats:chat_room', args=[chat_id]))

        chat = Chat.objects.create()
        chat.name = f"Чат {exchange.sender_skill} - {exchange.receiver_skill}"
        if current_user == sender:
            chat.participants.add(current_user, receiver)
        else:
            chat.participants.add(current_user, sender)
        chat_id = chat.id
        chat.save()
        exchange.status = 'Активно'
        exchange.save()
        return redirect(reverse_lazy('chats:chat_room', args=[chat_id]))

    return JsonResponse({'success': False})


class ShowChats(DefaultImageMixin, ListView):
    model = Chat
    template_name = 'main/chats.html'
    context_object_name = 'chats'

    def get_queryset(self):
        current_user = self.request.user
        return Chat.objects.filter(participants=current_user)


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
            receiver_skill = UserSkills.objects.get(user=receiver, skill=post.wanted_skill)
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
            post.responder.add(receiver)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
