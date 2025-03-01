from django.urls import path


from . import views

urlpatterns = [
    path('', views.MainPage.as_view(), name="main_page"),
    path('category/<slug:cat_slug>', views.SkillCategory.as_view(), name="skill_category"),
    path("profile/<str:username>", views.ProfilePage.as_view(), name="profile_page"),
]
