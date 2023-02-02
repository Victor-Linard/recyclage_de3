from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import os
from authenticate.models import User


# Create your views here.


@login_required(login_url='/signin/')
def general(request):
    level_label = User.objects.select_related('level').get(pk=request.user.id)
    return render(request, 'general.html', context={"level_label": level_label})


@login_required(login_url='/signin/')
def security(request):
    level_label = User.objects.select_related('level').get(pk=request.user.id)
    return render(request, 'security.html', context={"level_label": level_label})


