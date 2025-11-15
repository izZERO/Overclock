from django.shortcuts import render, redirect
from .models import Profile, Product, Category, Order, Order_Detail, Wishlist
from .forms import RegisterForm, UpdateUserForm, UpdateProfileForm, UpdateStatus
from django.views import View
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.db.models import Q


# Create your views here.
def landing(request):
    return render(request, "landing.html")


def browse(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    return render(
        request, "browse.html", {"categories": categories, "products": products}
    )


def browse_category(request, category_id):
    category = Category.objects.get(id=category_id)
    products = Product.objects.filter(category=category)
    return render(
        request, "browse_category.html", {"category": category, "products": products}
    )


def customer_product_detail(request, product_id):
    product = Product.objects.get(id=product_id)

    wishlist = None
    if request.user.is_authenticated:
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)

    return render(
        request,
        "customer_product_detail.html",
        {
            "product": product,
            "wishlist": wishlist,
        },
    )


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


def profile_view(request):
    recent_orders = Order.objects.filter(user_id=request.user).order_by("-date_placed")[
        :5
    ]

    total_orders = Order.objects.filter(user_id=request.user).count()

    # Generator expression, its like list comprehension but more memory effective in this usecase
    total_spent = sum(
        order.total_cost for order in Order.objects.filter(user_id=request.user)
    )

    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist_items = wishlist.products.all()[:4]
    wishlist_count = wishlist.products.count()

    context = {
        "recent_orders": recent_orders,
        "total_orders": total_orders,
        "total_spent": total_spent,
        "wishlist_items": wishlist_items,
        "wishlist_count": wishlist_count,
    }

    return render(request, "user/profile.html", context)


# Admin Views


def manage_index(request):
    return render(request, "manage/index.html")


class ProductList(ListView):
    model = Product

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search")

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(category__name__icontains=search_query)
            )

        return queryset


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


def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)

    if request.method == "POST":
        form = UpdateStatus(request.POST)
        if form.is_valid():
            selected_status = form.cleaned_data["status_dropdown"]
            order.status = selected_status
            order.save()
            return redirect("orders_detail", order_id=order.id)
    else:
        form = UpdateStatus(initial={"status_dropdown": order.status})
    return render(
        request,
        "main/order_detail.html",
        {
            "order": order,
            "form": form,
        },
    )


#  User Views
def wishlist_index(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    products = wishlist.products.all()

    return render(
        request,
        "wishlist.html",
        {
            "products": products,
            "wishlist": wishlist,
        },
    )


def assoc_product(request, wishlist_id, product_id):
    wishlist = Wishlist.objects.get(id=wishlist_id, user=request.user)
    wishlist.products.add(product_id)
    return redirect("wishlist_index")


def unassoc_product(request, wishlist_id, product_id):
    wishlist = Wishlist.objects.get(id=wishlist_id, user=request.user)
    wishlist.products.remove(product_id)
    return redirect("wishlist_index")


def cart_view(request):
    cart, created = Order.objects.get_or_create(
        user_id=request.user,
        status="c",
        defaults={
            "total_cost": 0,
            "shipping_address": "",
        },
    )

    items = Order_Detail.objects.filter(order_id=cart)

    return render(
        request,
        "cart.html",
        {
            "cart": cart,
            "items": items,
        },
    )


def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart, created = Order.objects.get_or_create(
        user_id=request.user,
        status="c",
        defaults={
            "total_cost": 0,
            "shipping_address": "",
        },
    )

    quantity_str = 0

    if request.method == "POST":
        quantity_str = request.POST.get("quantity", "1")
    else:
        quantity_str = "1"

    quantity = int(quantity_str)

    # to prevent users from doing 0 or negative qty
    if quantity < 1:
        quantity = 1

    existing_item = Order_Detail.objects.filter(
        order_id=cart,
        product_id=product,
    ).first()

    if existing_item:

        existing_item.quantity += quantity
        existing_item.save()
    else:

        Order_Detail.objects.create(
            order_id=cart,
            product_id=product,
            quantity=quantity,
            order_cost=0,
        )

    items = Order_Detail.objects.filter(order_id=cart)
    total = 0
    for item in items:
        total = total + item.order_cost

    cart.total_cost = total
    cart.save()

    return redirect("cart_view")


def update_cart_item(request, item_id):
    item = Order_Detail.objects.get(id=item_id)
    cart = item.order_id

    if request.method == "POST":

        quantity = int(request.POST.get("quantity", item.quantity))

        if quantity < 1:
            quantity = 1

        item.quantity = quantity
        # order_cost is updated in save()
        item.save()

        # Redo cart total
        items = Order_Detail.objects.filter(order_id=cart)
        total = 0
        for item in items:
            total = total + item.order_cost

        cart.total_cost = total
        cart.save()

    return redirect("cart_view")


def remove_from_cart(request, item_id):
    item = Order_Detail.objects.get(id=item_id)
    cart = item.order_id

    if request.method == "POST":
        item.delete()

        # Redo cart total after delete
        items = Order_Detail.objects.filter(order_id=cart)
        total = 0
        for item in items:
            total = total + item.order_cost

        cart.total_cost = total
        cart.save()

    return redirect("cart_view")


def customer_orders(request):
    orders = Order.objects.filter(user_id=request.user).order_by("-date_placed")

    context = {
        "orders": orders,
    }

    return render(request, "orders.html", {"orders": orders})
