from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


# Create your models here.


class Level(models.Model):
    label = models.CharField(max_length=255)
    exp_level_up = models.IntegerField(default=0)
    label_image = models.CharField(max_length=255)


class User(AbstractUser):
    level = models.ForeignKey(Level, on_delete=models.CASCADE, default=1)
    points = models.IntegerField(default=0)
    exp = models.IntegerField(default=1)
    last_last_login = models.DateTimeField(default=timezone.now)


