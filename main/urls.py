from django.urls import path, include
from . import views

urlpatterns = [
    # Admin
    path("manage/", views.manage_index, name="manage"),
    # Admin Orders
    path("manage/orders/", views.OrderList.as_view(), name="orders_index"),
    path(
        "manage/orders/<int:order_id>/",
        views.order_detail,
        name="orders_detail",
    ),
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
    path("about/", views.about, name="about"),
    # Customer Pages
    path("profile/", views.profile_view, name="profile-view"),
    path("profile/edit", views.profile, name="profile-edit"),
    # Order
    path("orders/", views.customer_orders, name="customer_orders"),
    # Wishlist
    path("wishlist/", views.wishlist_index, name="wishlist_index"),
    path(
        "wishlist/<int:wishlist_id>/assoc_product/<int:product_id>",
        views.assoc_product,
        name="assoc_product",
    ),
    path(
        "wishlist/<int:wishlist_id>/unassoc_product/<int:product_id>",
        views.unassoc_product,
        name="unassoc_product",
    ),
    # Browse
    path("browse/", views.browse, name="browse"),
    path("browse/<int:category_id>/", views.browse_category, name="browse_category"),
    path(
        "product/<int:product_id>/",
        views.customer_product_detail,
        name="customer_product_detail",
    ),
    # Cart
    path("cart/", views.cart_view, name="cart_view"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<int:item_id>/", views.update_cart_item, name="update_cart_item"),
    path("cart/remove/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),
    
]
