from django.contrib import admin
from django.urls import path

from tournament import views

urlpatterns = [
    path('', views.register),
]
