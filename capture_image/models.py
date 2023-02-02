from django.db import models
from django.utils import timezone
from authenticate.models import User

# Create your models here.


class ImageWebCam(models.Model):
    anonyme_id = models.CharField(max_length=50)
    image = models.ImageField(upload_to='./UPLOADED_IMAGES/')


class Scan(models.Model):
    date = models.DateTimeField(default=timezone.now)
    type_of_waste = models.CharField(max_length=50)
    points = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
