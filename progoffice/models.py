from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Student(models.Model):
    reg_no = models.CharField(max_length=20, primary_key=True)
    student_name = models.CharField(max_length=50)
    father_name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)

    def __str__(self):
        return self.student_name


class Course(models.Model):
    course_code =  models.CharField(max_length=6, primary_key=True)
    course_name = models.CharField(max_length=50)

    def __str__(self):
        return self.course_name


class Teacher(models.Model):
    Teacher_Statuses = (
        ('V', 'visiting'),
        ('P', 'permanent'),
    )
    Teacher_designations = (
        ('P', 'professor'),
        ('AP', 'asst. professor')
    )
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, unique=True)
    teacher_name = models.CharField(max_length=50)
    teacher_designation = models.CharField(max_length=2, choices=Teacher_designations)
    teacher_status = models.CharField(max_length=1, choices=Teacher_Statuses)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.teacher_name


class Enrollment(models.Model):
    id = models.AutoField
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher_id = models.ForeignKey(Teacher, on_delete=models.CASCADE)


class PendingRegistration(models.Model):
    id = models.AutoField
    teacher_id = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    def __str__(self):
        return self.teacher_id.teacher_name