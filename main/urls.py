from django.urls import path, include
from . import views

urlpatterns = [
    # Signup
    path('accounts/signup/', views.signup, name='signup'),
    path("", views.landing, name="landing"),
]

