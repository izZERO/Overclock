from django.contrib import admin
from .models import Profile, Product, Category, Order, Order_Detail

# Register your models here.
admin.site.register(Profile)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(Order_Detail)
