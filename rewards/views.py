from django.shortcuts import render
from authenticate.models import User
from rewards.models import Keys


# Create your views here.


def rewards(request):
    level_label = User.objects.select_related('level').get(pk=request.user.id)
    keys = Keys.objects.filter(user=request.user).select_related('reward')
    return render(request, 'rewards.html', context={"level_label": level_label, "keys": keys})


def claimed(request):
    level_label = User.objects.select_related('level').get(pk=request.user.id)
    return render(request, 'claimed.html', context={"level_label": level_label})
