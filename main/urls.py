from django.urls import path, include
from . import views

urlpatterns = [
    # Admin
    path("manage/", views.manage_index, name= "manage"),
    path("manage/products/", views.ProductList.as_view(), name="products_index"),
    # Signup
    path("accounts/signup/", views.signup, name="signup"),
    path("", views.landing, name="landing"),
    path("home/", views.home, name="home"),
    path("about/", views.about, name="about"),
    # Profile
    path("profile/edit", views.profile, name="profile-edit"),
]
