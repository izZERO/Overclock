from django.shortcuts import render, redirect
from .models import Profile, Product, Category, Order, Order_Detail, Wishlist
from .forms import RegisterForm, UpdateUserForm, UpdateProfileForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView


# Create your views here.
def landing(request):
    return render(request, "landing.html")


def home(request):
    return render(request, "home.html")


def about(request):
    return render(request, "about.html")


def signup(request):
    error_message = ""
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("landing")
        else:
            error_message = "invalid signup - try again later..."
    form = RegisterForm()
    context = {"form": form, "error_message": error_message}
    return render(request, "registration/signup.html", context)


# code from https://dev.to/earthcomfy/django-update-user-profile-33ho
def profile(request):
    if request.method == "POST":
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect(to="/profile")
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    return render(
        request,
        "user/profile_edit.html",
        {"user_form": user_form, "profile_form": profile_form},
    )


# Admin Views


def manage_index(request):
    return render(request, "manage/index.html")


class ProductList(ListView):
    model = Product


class ProductDetail(DetailView):
    model = Product
