from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='teacher_home'),
    path('profile/', views.profile, name='teacher_profile')
]
