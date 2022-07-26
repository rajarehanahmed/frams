from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='office_home'),
    path('addteacher/', views.addTeacher, name='add_teacher'),
    path('completesignup/', views.completeSignup, name='complete_signup'),
    path('pendingregistrations/', views.pendingRegistrations, name='pending_registrations'),
    path('deletependingreg/', views.deletePendingReg, name='delete_pending_reg'),
    path('teacher-attendance/', views.teacherAttendance, name='teacher_attendance'),
    path('teacher-face-attendance/', views.teacherFaceAttendance, name='teacher_face_attendance'),
    path('teacher-fingerprint-attendance/', views.teacherFingerprintAttendance, name='teacher_fingerprint_attendance'),
    path('addstudent/', views.addStudent, name='add_student'),
    path('student-attendance/', views.studentAttendance, name='student_attendance'),
]
