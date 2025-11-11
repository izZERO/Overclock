from django.urls import path, include
from . import views

urlpatterns = [
    # Signup
    path("accounts/signup/", views.signup, name="signup"),
    path("", views.landing, name="landing"),
    path("home/", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("profile/edit", views.profile, name="profile-edit"),
]
