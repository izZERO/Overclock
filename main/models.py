from django.db import models

# Create your models here.
class Product(models.Model):
    name= models.CharField(max_length=50)
    description= models.CharField(max_length=250)
    image= models.ImageField(upload_to="main/static/uploads", default="")
    price= models.FloatField()
    weight= models.IntegerField()
    stock= models.IntegerField()

