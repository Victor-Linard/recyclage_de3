"""recyclage URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
import authenticate.views
import dashboard.views
import user_profile.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signin/', authenticate.views.SigninPageView.as_view(), name="signin"),
    path('signup/', authenticate.views.signup_page, name="signup"),
    path('signout/', authenticate.views.signout_user, name="signout"),
    path('dashboard/', dashboard.views.dashboard, name="dashboard"),
    path('', dashboard.views.dashboard, name="dashboard"),
    path('user_profile/', user_profile.views.general, name="general"),
    path('user_profile/avatar/', user_profile.views.avatar, name="avatar"),
    path('user_profile/security/', user_profile.views.security, name="security")
]
