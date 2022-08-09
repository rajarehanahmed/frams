from django.contrib import admin
from .models import Attendance, ClassTiming, Student, Teacher, TeacherAdminModel, Course, CourseAdminModel, ClassRoom, Timetable, TimetableAdminModel, StudentAttendance, BulkAttendance

admin.site.register(Student)
admin.site.register(Teacher, TeacherAdminModel)
admin.site.register(Course, CourseAdminModel)
admin.site.register(ClassRoom)
admin.site.register(Timetable, TimetableAdminModel)
admin.site.register(StudentAttendance)
admin.site.register(Attendance)
admin.site.register(BulkAttendance)
admin.site.register(ClassTiming)
