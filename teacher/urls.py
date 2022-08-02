from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='teacher_home'),
    path('profile/', views.profile, name='teacher_profile'),
    path('teacher_report', views.teacherReport, name='teacher_report'),
    path('student_report', views.studentReport, name='student_report'),
    path('generate-teacher-csv/', views.generateTeacherCSV, name='generate_teacher_csv'),
    path('generate-student-csv/', views.generateStudentCSV, name='generate_student_csv'),
]
