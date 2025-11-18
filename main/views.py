from datetime import datetime, timedelta
import stripe
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .forms import (
    RegisterForm,
    UpdateUserForm,
    UpdateProfileForm,
    UpdateStatus,
)
from .models import (
    Profile,
    Product,
    Category,
    Order,
    Order_Detail,
    Wishlist,
)


def landing(request):
    return render(request, "landing.html")


def about(request):
    return render(request, "about.html")


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
        wishlist = Wishlist.objects.get_or_create(user=request.user)

    return render(
        request,
        "customer_product_detail.html",
        {
            "product": product,
            "wishlist": wishlist,
        },
    )


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

    wishlist = Wishlist.objects.get_or_create(user=request.user)
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


def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    items = Order_Detail.objects.filter(order_id=order)

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
            "items": items,
        },
    )


#  User Views
def wishlist_index(request):
    wishlist = Wishlist.objects.get_or_create(user=request.user)
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
    cart = Order.objects.get_or_create(
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
    # out of stock check in case someone crafts a POST request manually
    if product.stock <= 0:
        return redirect("customer_product_detail", product_id=product.id)

    cart = Order.objects.get_or_create(
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

        existing_item.quantity = quantity
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


def place_order(request):
    cart = Order.objects.get(user_id=request.user, status="c")
    items = Order_Detail.objects.filter(order_id=cart)

    if not items:  #  if cart is empty then reload thy page
        return redirect("cart_view")

    if request.method == "POST":
        address = request.POST.get("address", "").strip()
        phone = request.POST.get("phone", "").strip()

        # If either is empty, show error in thy cart page
        if address == "" or phone == "":
            return render(
                request,
                "cart.html",
                {
                    "cart": cart,
                    "items": items,
                    "error": "Please fill in both address and phone number to place your order, you really want your items to be lost in the sea?",
                },
            )

        # Save / update to user's profile while at it
        profile = Profile.objects.get(user=request.user)
        profile.address = address
        profile.phone = phone
        profile.save()
        # Save shipping address on the order
        cart.shipping_address = address
        cart.save()

        # purchase using stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY

        stripe_data = []
        for item in items:
            stripe_data.append(
                {
                    "price": item.product_id.price_id,
                    "quantity": item.quantity,
                }
            )

        checkout_session = stripe.checkout.Session.create(
            line_items=stripe_data,
            mode="payment",
            success_url=request.build_absolute_uri(
                reverse("thank_you", kwargs={"order_id": cart.id})
            ),
            cancel_url=request.build_absolute_uri(reverse("cart_view")),
        )
        return redirect(checkout_session.url, code=303)

    return redirect("cart_view")


def thank_you(request, order_id):
    order = Order.objects.get(id=order_id, user_id=request.user)
    items = Order_Detail.objects.filter(order_id=order)

    # Deduct stock
    for item in items:
        product = item.product_id
        product.stock = product.stock - item.quantity
        if product.stock < 0:
            product.stock = 0
        product.save()

    order.status = "p"
    order.save()

    # Build items HTML
    items_html = ""
    for item in items:
        items_html += "<tr>"
        items_html += "<td>" + str(item.product_id.name) + "</td>"
        items_html += "<td style='text-align: center;'>" + str(item.quantity) + "</td>"
        items_html += (
            "<td style='text-align: right;'>$"
            + "{:.2f}".format(item.product_id.price)
            + "</td>"
        )
        items_html += (
            "<td style='text-align: right;'>$"
            + "{:.2f}".format(item.order_cost)
            + "</td>"
        )
        items_html += "</tr>"

    # Build email
    customer_name = request.user.get_full_name() or request.user.username
    order_date = order.date_placed.strftime("%B %d, %Y at %I:%M %p")
    order_detail_url = request.build_absolute_uri(
        reverse("customer_order_detail", kwargs={"order_id": order.id})
    )

    html_message = (
        """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Order Confirmation</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f4f4f4;
            }
            .container {
                background-color: #ffffff;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .header {
                text-align: center;
                border-bottom: 3px solid #fd8211;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }
            .header h1 {
                color: #fd8211;
                margin: 0;
                font-size: 32px;
            }
            .header p {
                color: #666;
                margin: 5px 0 0 0;
            }
            .order-info {
                background-color: #f9f9f9;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 25px;
            }
            .order-info h2 {
                color: #fd8211;
                margin-top: 0;
                font-size: 20px;
            }
            .order-info p {
                margin: 8px 0;
            }
            .order-info strong {
                color: #333;
            }
            .items-table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }
            .items-table th {
                background-color: #fd8211;
                color: white;
                padding: 12px;
                text-align: left;
                font-weight: bold;
            }
            .items-table td {
                padding: 12px;
                border-bottom: 1px solid #ddd;
            }
            .items-table tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            .total-section {
                text-align: right;
                margin-top: 20px;
                padding-top: 15px;
                border-top: 2px solid #fd8211;
            }
            .total-section p {
                margin: 8px 0;
                font-size: 16px;
            }
            .total-amount {
                font-size: 24px;
                color: fd8211;
                font-weight: bold;
            }
            .footer {
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                color: #666;
                font-size: 14px;
            }
            .footer p {
                margin: 5px 0;
            }
            .cta-button {
                display: inline-block;
                padding: 12px 30px;
                background-color: #fd8211;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
                font-weight: bold;
            }
            .shipping-address {
                background-color: #fff8e1;
                padding: 15px;
                border-left: 4px solid #ffc107;
                margin: 20px 0;
            }
            .shipping-address h3 {
                margin-top: 0;
                color: #f57c00;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>OVERCLOCK</h1>
                <p>Thank you for your purchase!</p>
            </div>

            <div class="order-info">
                <h2>Order Confirmation</h2>
                <p><strong>Order Number:</strong> #"""
        + str(order.id)
        + """</p>
                <p><strong>Order Date:</strong> """
        + order_date
        + """</p>
                <p><strong>Customer:</strong> """
        + customer_name
        + """</p>
                <p><strong>Email:</strong> """
        + request.user.email
        + """</p>
            </div>

            <div class="shipping-address">
                <h3>Shipping Address</h3>
                <p>"""
        + str(order.shipping_address)
        + """</p>
            </div>

            <h2 style="color: #fd8211; margin-top: 30px;">Order Items</h2>
            <table class="items-table">
                <thead>
                    <tr>
                        <th>Product</th>
                        <th style="text-align: center;">Quantity</th>
                        <th style="text-align: right;">Price</th>
                        <th style="text-align: right;">Subtotal</th>
                    </tr>
                </thead>
                <tbody>
                    """
        + items_html
        + """
                </tbody>
            </table>

            <div class="total-section">
                <p>Subtotal: $"""
        + "{:.2f}".format(order.total_cost)
        + """</p>
                <p class="total-amount">Total: $"""
        + "{:.2f}".format(order.total_cost)
        + """</p>
            </div>

            <div style="text-align: center;">
                <a style="text-decoration: none; color: white;" href="""
        " + order_detail_url + "
        """ class="cta-button">
                    View Order Details
                </a>
            </div>

            <div class="footer">
                <p><strong>What happens next?</strong></p>
                <p>We're processing your order and will send you a shipping notification once it's on its way.</p>
                <p style="margin-top: 20px;">If you have any questions, feel free to contact our support team.</p>
                <p style="margin-top: 20px; color: #999; font-size: 12px;">
                    2025 OVERCLOCK. All rights reserved.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    )

    send_mail(
        subject="Thank you for your purchase from OVERCLOCK - Order Confirmation",
        message="Thank you for your order #"
        + str(order.id)
        + "! Your order has been confirmed and is being processed.",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[request.user.email],
        fail_silently=False,
        html_message=html_message,
    )
    return render(
        request,
        "thank_you.html",
        {
            "order": order,
            "items": items,
        },
    )


def customer_orders(request):
    orders = Order.objects.filter(user_id=request.user).order_by("-date_placed")

    return render(request, "orders.html", {"orders": orders})


def customer_order_detail(request, order_id):
    order = Order.objects.get(id=order_id, user_id=request.user)
    items = Order_Detail.objects.filter(order_id=order)

    return render(
        request,
        "customer_order_detail.html",
        {
            "order": order,
            "items": items,
        },
    )


def analytical_dashboard(request):

    date_labels = []
    revenue_data = []
    quantity_data = []
    category_labels = []
    category_values = []
    revenue_by_day = {}
    quantity_by_day = {}

    today = datetime.today().date()
    start_date = today - timedelta(days=6)

    date_list = []
    day = start_date
    while day <= today:
        date_list.append(day)
        day = day + timedelta(days=1)

    for date in date_list:
        revenue_by_day[date] = 0
        quantity_by_day[date] = 0

    order_details = Order_Detail.objects.filter(
        order_id__status__in=["p", "t", "d"],
        order_id__date_placed__date__gte=start_date,
        order_id__date_placed__date__lte=today,
    )

    for item in order_details:
        order_day = item.order_id.date_placed.date()
        revenue_by_day[order_day] = revenue_by_day[order_day] + item.order_cost
        quantity_by_day[order_day] = quantity_by_day[order_day] + item.quantity

    for date in date_list:
        date_labels.append(date.strftime("%b %d"))
        revenue_data.append(revenue_by_day[date])
        quantity_data.append(quantity_by_day[date])

    categories = Category.objects.all()
    for category in categories:
        total = 0
        products = Product.objects.filter(category=category)
        for product in products:
            item_details = Order_Detail.objects.filter(
                product_id=product, order_id__status__in=["p", "t", "d"]
            )
            for detail in item_details:
                total = total + detail.order_cost

        category_labels.append(category.name)
        category_values.append(total)

    context = {
        "date_labels": date_labels,
        "revenue_data": revenue_data,
        "quantity_data": quantity_data,
        "category_labels": category_labels,
        "category_values": category_values,
    }

    return render(request, "main/analytical_dashboard.html", context)


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
        "price_id",
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
        "price_id",
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
