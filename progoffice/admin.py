from django.contrib import admin
from .models import Student, Teacher, Course, Enrollment, PendingRegistration

# Register your models here.
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(PendingRegistration)