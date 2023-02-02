from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from authenticate.models import User
from rewards.models import Keys


# Create your views here.


@login_required(login_url='/signin/')
def rewards(request):
    level_label = User.objects.select_related('level').get(pk=request.user.id)
    keys = Keys.objects.filter(user=request.user).select_related('reward')
    total_points = 0
    user = User.objects.get(pk=request.user.id)
    total_points = user.points
    return render(request, 'rewards.html', context={"level_label": level_label, "keys": keys, 'total_points': total_points})


@login_required(login_url='/signin/')
def claimed(request):
    level_label = User.objects.select_related('level').get(pk=request.user.id)
    keys = Keys.objects.filter(user=request.user).select_related('reward')
    return render(request, 'claimed.html', context={"level_label": level_label, "keys": keys})


@login_required(login_url='/signin/')
def change_reward_status(request, key, cost):
    giga_key = Keys.objects.get(pk=key)
    giga_key.status = "claimed"
    total_points = User.objects.get(pk=request.user.id)
    total_points.points = total_points.points - cost
    giga_key.save()
    total_points.save()

    if key is None:
        return render(request, 'change_reward_status.html', context={'icon': "error", 'title': "Oops...", 'text': "Something went wrong!"})
    else:
        return render(request, 'change_reward_status.html', context={'icon': "success", 'title': "Nice !", 'text': "Your Giga key : "+key})

