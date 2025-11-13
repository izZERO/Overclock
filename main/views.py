from django.shortcuts import render, redirect
from .models import Profile, Product, Category, Order, Order_Detail, Wishlist
from .forms import RegisterForm, UpdateUserForm, UpdateProfileForm
from django.views import View
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView


# Create your views here.
def landing(request):
    return render(request, "landing.html")


def browse(request):
    return render(request, "browse.html")


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


class ProductCreate(CreateView):
    model = Product
    fields = [
        "name",
        "description",
        "image",
        "price",
        "weight",
        "stock",
        "category",
    ]

    def form_valid(self, form):
        form.instance.added_by = self.request.user
        return super().form_valid(form)


class ProductUpdate(UpdateView):
    model = Product
    fields = [
        "name",
        "description",
        "image",
        "price",
        "weight",
        "stock",
        "category",
    ]

    def form_valid(self, form):
        form.instance.added_by = self.request.user
        return super().form_valid(form)


class ProductDelete(DeleteView):
    model = Product
    success_url = "/manage/products/"


class CategoryList(ListView):
    model = Category


class CategoryCreate(CreateView):
    model = Category
    fields = ["name"]

    def form_valid(self, form):
        form.instance.added_by = self.request.user
        return super().form_valid(form)


class CategoryUpdate(UpdateView):
    model = Category
    fields = [
        "name",
    ]

    def form_valid(self, form):
        form.instance.added_by = self.request.user
        return super().form_valid(form)


class CategoryDelete(DeleteView):
    model = Category
    success_url = "/manage/categories/"


class OrderList(ListView):
    model = Order


class OrderDetail(DetailView):
    model = Order


# class OrderAdd(CreateView):
#     model = Order
#     fields = ["name"]

#     def form_valid(self, form):
#         form.instance.user_id = self.request.user
#         return super().form_valid(form)


def update_status(request, order_id, status):
    order = Order.objects.get(id=order_id)
    order.status = status
    order.save()


# class OrderDelete(DeleteView):
#     model = Order


def wishlist_index(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)

    products = wishlist.products.all()

    return render(request, "wishlist.html", {"products": products})


def assoc_product(request, wishlist_id, product_id):
    Wishlist.objects.get(id=wishlist_id).products.add(product_id)
    return redirect("detail", wishlist_id=wishlist_id)


def unassoc_product(request, wishlist_id, product_id):
    Wishlist.objects.get(id=wishlist_id).products.remove(product_id)
    return redirect("detail", wishlist_id=wishlist_id)
