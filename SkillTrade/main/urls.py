from django.urls import path


from . import views

urlpatterns = [
    path('', views.MainPage.as_view(), name="main_page"),
    path('category/<slug:cat_slug>', views.MainPage.as_view(), name="skill_category"),
    path('profile/<str:username>', views.ProfilePage.as_view(), name="profile_page"),
    path('request/<str:username>', views.RequestPage.as_view(), name="request_page"),
    path('create-request/<int:post_id>', views.create_request, name='create_request'),
    path('update_status/', views.update_status, name='update_status'),
    path('add_skill/', views.AddSkill.as_view(), name='add_skill')
]
