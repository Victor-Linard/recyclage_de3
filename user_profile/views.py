from django.shortcuts import render
import os

# Create your views here.

def general(request):
    return render(request, 'general.html', context={})

def avatar(request):
    path = os.path.dirname(os.path.dirname(__file__)) + "/static/pictures/"
    images = os.listdir(path)
    print(images)
    return render(request, 'avatar.html', context={"images": images})

def security(request):
    return render(request, 'security.html', context={})