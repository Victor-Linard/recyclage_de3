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
import rewards.views
import user_profile.views
import capture_image.views
import home.views


urlpatterns = [
    path('', home.views.home, name="home"),
    path('admin/', admin.site.urls),
    path('signin/', authenticate.views.SigninPageView.as_view(), name="signin"),
    path('signup/', authenticate.views.signup_page, name="signup"),
    path('signout/', authenticate.views.signout_user, name="signout"),
    path('dashboard/', dashboard.views.dashboard, name="dashboard"),
    path('user_profile/', user_profile.views.general, name="general"),
    path('user_profile/security/', user_profile.views.security, name="security"),
    path('user_profile/stats/', user_profile.views.stats, name="stats"),
    path('rewards/', rewards.views.rewards, name="rewards"),
    path('rewards/claimed', rewards.views.claimed, name="claimed"),
    path('capture_image/', capture_image.views.capture_image, name='capture_image'),
    path('change_reward_status/<str:key>/<int:cost>', rewards.views.change_reward_status, name='change_reward_status'),
    path('pricing/', home.views.pricing, name='pricing')
]
