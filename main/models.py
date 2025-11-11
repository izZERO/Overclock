from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, default="user")
    address = models.CharField(max_length=250)
    phone = models.CharField(max_length=50)

    def __str__(self):
        return self.user.username


class Product(models.Model):
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=250)
    image = models.ImageField(upload_to="main/static/uploads", default="")
    price = models.FloatField()
    weight = models.FloatField()
    stock = models.IntegerField()

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Order(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    total_cost = models.FloatField()
    shipping_address = models.CharField(max_length=250)
    status = models.CharField(max_length=250)
    date_placed = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"Order for {self.user_id.username} placed on {self.date_placed}"

class Order_Detail(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    order_cost = models.FloatField()

    def save(self, *args, **kwargs):
        self.order_cost = self.quantity * self.product_id.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order Details for {self.order_id.user_id.username} placed on {self.order_id.date_placed}"
