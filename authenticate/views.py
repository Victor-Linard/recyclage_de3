from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_http_methods
from django.views.generic import View
from recyclage import settings
from . import forms

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
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
    return render(request, 'authenticate/signup.html', context={'form': form})


@require_GET
def signout_user(request):
    logout(request)
    return redirect('dashboard')
