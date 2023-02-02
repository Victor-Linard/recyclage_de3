from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

# Create your models here.


class User(AbstractUser):
    level_id = models.IntegerField(default=1)
    points = models.IntegerField(default=0)
    exp = models.IntegerField(default=0)
    last_last_login = models.DateTimeField(default=timezone.now)
