from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='office_home'),
    path('addteacher/', views.addTeacher, name='add_teacher'),
    path('addstudent/', views.addStudent, name='add_student'),
]
