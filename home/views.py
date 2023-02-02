from django.shortcuts import render

# Create your views here.


def home(request):
    return render(request, "home.html", context={})


def pricing(request):
    return render(request, 'pricing.html', context={})
