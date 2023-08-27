from django.contrib import admin
from django.urls import path, include, re_path

from profiles import views

urlpatterns = [
    path('', views.index),
    path('connect/', views.connect)
]
