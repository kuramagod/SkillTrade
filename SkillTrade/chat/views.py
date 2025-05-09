from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy

from .models import Chat, Message


@login_required
def chat_room(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    current_user = request.user
    if current_user not in chat.participants.all():
        return HttpResponseRedirect(reverse_lazy('chats'))
    messages = chat.messages.order_by('timestamp')
    return render(request, 'chat/chat_room.html', {'chat': chat, 'messages': messages, 'default_image': settings.DEFAULT_USER_IMAGE})

@login_required
def send_message(request, chat_id):
    if request.method == 'POST':
        chat = get_object_or_404(Chat, id=chat_id)
        content = request.POST.get('content')
        message = Message.objects.create(chat=chat, sender=request.user, content=content)
        return JsonResponse({'status': 'ok', 'message': 'Message sent'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)