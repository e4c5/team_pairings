"""team_pair URL Configuration

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
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views

from api import urls
from tournament import views


urlpatterns = [
    path('', views.index),
    path('login/', 
         auth_views.LoginView.as_view(template_name='account/login.html'),
        name='login'
    ),
    path('loout/', auth_views.LoginView.as_view()),
    path('change-password/', 
         auth_views.PasswordChangeView.as_view(template_name='account/change-password.html')
    ),
    path('change-password/done', auth_views.PasswordChangeDoneView.as_view()),
    path('accounts/password_reset/', 
         auth_views.PasswordResetView.as_view(),
         name='password_reset'
    ),
    
    path('admin/', admin.site.urls),
    path('api/', include(urls.urlpatterns)),
    path('api-auth/', include('rest_framework.urls')),
    re_path('^', views.redirect_view)
]
13