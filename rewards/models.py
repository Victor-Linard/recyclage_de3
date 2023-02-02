from django.db import models
from authenticate.models import User


# Create your models here.


class Rewards(models.Model):
    label = models.CharField(max_length=255)
    cost_point = models.IntegerField()
    label_image = models.CharField(max_length=255)


class Keys(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('claimed', 'Claimed'),
    ]
    key = models.CharField(max_length=14, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reward = models.ForeignKey(Rewards, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')

