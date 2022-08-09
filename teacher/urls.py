from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='teacher_home'),
    # path('profile/', views.profile, name='teacher_profile'),
    path('teacher-report', views.teacherReport, name='teacher_report'),
    path('student-report', views.studentReport, name='student_report'),
    path('course-report', views.courseReport, name='course_report'),
    path('generate-teacher-csv/', views.generateTeacherCSV, name='generate_teacher_csv'),
    path('generate-student-csv/', views.generateStudentCSV, name='generate_student_csv'),
    path('generate-course-csv/', views.generateCourseCSV, name='generate_course_csv'),
]
