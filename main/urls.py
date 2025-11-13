from django.urls import path, include
from . import views

urlpatterns = [
    # Admin
    path("manage/", views.manage_index, name="manage"),
    # Admin Products
    path("manage/products/", views.ProductList.as_view(), name="products_index"),
    path(
        "manage/products/<int:pk>/",
        views.ProductDetail.as_view(),
        name="products_detail",
    ),
    path(
        "manage/products/create/", views.ProductCreate.as_view(), name="products_create"
    ),
    path(
        "manage/products/<int:pk>/update/",
        views.ProductUpdate.as_view(),
        name="products_update",
    ),
    path(
        "manage/products/<int:pk>/delete/",
        views.ProductDelete.as_view(),
        name="products_delete",
    ),
    # Admin categories
    path("manage/categories/", views.CategoryList.as_view(), name="categories_index"),
    path(
        "manage/categories/create/",
        views.CategoryCreate.as_view(),
        name="categories_create",
    ),
    path(
        "manage/categories/<int:pk>/update/",
        views.CategoryUpdate.as_view(),
        name="categories_update",
    ),
    path(
        "manage/categories/<int:pk>/delete/",
        views.CategoryDelete.as_view(),
        name="categories_delete",
    ),
    # Signup
    path("accounts/signup/", views.signup, name="signup"),
    path("", views.landing, name="landing"),
    path("browse/", views.browse, name="browse"),
    path("about/", views.about, name="about"),
    # Profile
    path("profile/edit", views.profile, name="profile-edit"),
    # Order
    path("manage/orders/", views.OrderList.as_view(), name="orders_index"),
       path(
        "manage/orders/<int:pk>/",
        views.OrderDetail.as_view(),
        name="orders_detail",
    ),
]
