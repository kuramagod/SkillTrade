from django.urls import path


app_name = "chats"
from . import views

urlpatterns = [
    path('chat/<int:chat_id>/', views.chat_room, name='chat_room'),
    path('chat/<int:chat_id>/send/', views.send_message, name='send_message'),
]