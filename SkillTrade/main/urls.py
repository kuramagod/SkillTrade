from django.urls import path


from . import views

urlpatterns = [
    path('', views.MainPage.as_view(), name="main_page"),
    path('skill_filter/<slug:skill_slug>', views.MainPage.as_view(), name="skill_category"),
    path('profile/<str:username>', views.ProfilePage.as_view(), name="profile_page"),
    path('request/<str:username>', views.RequestPage.as_view(), name="request_page"),
    path('create-request/<int:post_id>', views.create_request, name='create_request'),
    path('update_status/', views.update_status, name='update_status'),
    path('add_skill_profile/', views.AddSkillProfile.as_view(), name='add_skill_profile'),
    path('add_skill/', views.AddSkill.as_view(), name='add_skill'),
    path('delete/<int:pk>/', views.DeleteSkill.as_view(), name="delete_skill"),
    path('start_chat/<int:request_id>', views.start_chat, name="start_chat")
]
