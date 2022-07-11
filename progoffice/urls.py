from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='office_home'),
    path('addteacher/', views.addTeacher, name='add_teacher'),
    path('completesignup/', views.completeSignup, name='complete_signup'),
    path('pendingregistrations/', views.pendingRegistrations, name='pending_registrations'),
    path('deletependingreg/', views.deletePendingReg, name='delete_pending_reg'),
    path('markteacherattendance/', views.markTeacherAttendance, name='mark_teacher_attendance'),
    path('addstudent/', views.addStudent, name='add_student'),
]
