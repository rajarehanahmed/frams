from django.contrib import admin
from .models import Student, Teacher, Course, Enrollment, PendingRegistration, Room, Timetable, StudentAttendance, TeacherAttendance

# Register your models here.
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(PendingRegistration)
admin.site.register(Room)
admin.site.register(Timetable)
admin.site.register(StudentAttendance)
admin.site.register(TeacherAttendance)