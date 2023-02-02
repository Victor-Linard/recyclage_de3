from django.db import models

# Create your models here.


class Image(models.Model):
    anonyme_id = models.CharField(max_length=50)
    image = models.ImageField(upload_to='./UPLOADED_IMAGES/')
