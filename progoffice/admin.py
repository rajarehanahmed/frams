from dataclasses import field
import time
from django.contrib import admin
from django import forms
import cv2

# from .forms import StudentUptionForm
from .models import Attendance, AttendanceAdminModel, BulkAttendanceAdminModel, ClassTiming, Student, StudentAttendanceAdminModel, Teacher, TeacherAdminModel, Course, CourseAdminModel, ClassRoom, ClassRoomAdminModel, Timetable, TimetableAdminModel, StudentAttendance, BulkAttendance



class StudentUpdationForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'

class StudentAdmin(admin.ModelAdmin):
    form = StudentUpdationForm
    search_fields=('reg_no', 'student_name')

admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher, TeacherAdminModel)
admin.site.register(Course, CourseAdminModel)
admin.site.register(ClassRoom, ClassRoomAdminModel)
admin.site.register(Timetable, TimetableAdminModel)
admin.site.register(StudentAttendance, StudentAttendanceAdminModel)
admin.site.register(Attendance, AttendanceAdminModel)
admin.site.register(BulkAttendance, BulkAttendanceAdminModel)
admin.site.register(ClassTiming)
