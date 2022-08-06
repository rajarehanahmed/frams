from django.contrib import admin
from .models import Attendance, ClassTiming, Student, Teacher, Course, PendingRegistration, ClassRoom, Timetable, StudentAttendance, BulkAttendance#, TeacherAttendance

admin.site.site_header = 'F R A M S'

admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Course)
admin.site.register(PendingRegistration)
admin.site.register(ClassRoom)
admin.site.register(Timetable)
admin.site.register(StudentAttendance)
admin.site.register(Attendance)
admin.site.register(BulkAttendance)
admin.site.register(ClassTiming)
