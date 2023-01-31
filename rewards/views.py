from django.shortcuts import render

# Create your views here.


def rewards(request):
    return render(request, 'rewards.html', context={})

def claimed(request):
    return render(request, 'claimed.html', context={})

