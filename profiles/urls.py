from django.contrib import admin
from django.urls import path, include, re_path

from profiles import views

urlpatterns = [
    path('', views.index, name='profile'),
    path('connect/', views.connect, name='connect'),
    path('edit/', views.edit),
    path('payment/', views.payment)
]

