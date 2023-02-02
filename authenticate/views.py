from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_http_methods
from django.views.generic import View
from recyclage import settings
from rewards.models import Keys, Rewards
from . import forms
import secrets
import re

from .models import User


# Create your views here.


class SigninPageView(View):
    template_name = 'authenticate/signin.html'
    form_class = forms.SignInForm

    def get(self, request):
        form = self.form_class()
        message = ''
        return render(request, self.template_name, context={'form': form, 'message': message})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                user.last_last_login = user.last_login
                user.save()
                login(request, user)
                return redirect(settings.LOGIN_REDIRECT_URL)
        message = 'Identifiants invalides.'
        return render(request, self.template_name, context={'form': form, 'message': message})


@require_http_methods(["GET", "POST"])
def signup_page(request):
    form = forms.SignupForm()
    if request.method == 'POST':
        form = forms.SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            rewards_keys(user)
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
    return render(request, 'authenticate/signup.html', context={'form': form})


def rewards_keys(user):
    reward_user = Keys()
    rewards = Rewards.objects.all()
    print(rewards)
    for reward in rewards:
        reward_user.key = generate_unique_key()
        reward_user.reward_id = reward.id
        reward_user.user_id = user.id
        reward_user.save()


def generate_unique_key():
    key = secrets.token_hex(6)
    key = re.sub("(.{4})", "\\1-", key, count=2)
    return key


@require_GET
def signout_user(request):
    logout(request)
    return redirect('signin')
