from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    role = models.CharField(max_length=50, default="user")
    address = models.CharField(max_length=250)
    phone = models.CharField(max_length=50)

    def __str__(self):
        return self.user.username
class Product(models.Model):
    name= models.CharField(max_length=50)
    description= models.CharField(max_length=250)
    image= models.ImageField(upload_to="main/static/uploads", default="")
    price= models.FloatField()
    weight= models.IntegerField()
    stock= models.IntegerField()

    def __str__(self):
        return self.name

