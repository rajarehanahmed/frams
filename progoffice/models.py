from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from .import myFields
from django.contrib import admin


class Teacher(models.Model):
    Teacher_Statuses = (
        ('V', 'visiting'),
        ('P', 'permanent'),
    )
    Teacher_designations = (
        ('P', 'professor'),
        ('AP', 'asst. professor')
    )
        
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    teacher_name = models.CharField(max_length=50)
    teacher_designation = models.CharField(max_length=2, choices=Teacher_designations)
    teacher_status = models.CharField(max_length=1, choices=Teacher_Statuses)
    face_img = models.ImageField(upload_to='teachers/faces', default="")
    face_encodings = models.BinaryField(null=True)
    right_thumb_img = models.ImageField(upload_to='teachers/fingerprints', default="")
    right_thumb_keypoints = models.BinaryField(null=True)
    right_thumb_descriptors = models.BinaryField(null=True)
    right_index_img = models.ImageField(upload_to='teachers/fingerprints', default="")
    right_index_keypoints = models.BinaryField(null=True)
    right_index_descriptors = models.BinaryField(null=True)
    right_middle_img = models.ImageField(upload_to='teachers/fingerprints', default="")
    right_middle_keypoints = models.BinaryField(null=True)
    right_middle_descriptors = models.BinaryField(null=True)
    right_ring_img = models.ImageField(upload_to='teachers/fingerprints', default="")
    right_ring_keypoints = models.BinaryField(null=True)
    right_ring_descriptors = models.BinaryField(null=True)
    right_little_img = models.ImageField(upload_to='teachers/fingerprints', default="")
    right_little_keypoints = models.BinaryField(null=True)
    right_little_descriptors = models.BinaryField(null=True)

    def __str__(self):
        if self.teacher_status == 'V':
            return self.teacher_name + " (Visiting)"
        else:
            return self.teacher_name + " (Permanent)"

class TeacherAdminModel(admin.ModelAdmin):
    search_fields=('teacher_name', 'teacher_designation', 'teacher_status',)


class Attendance(models.Model):
    id = models.AutoField
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)
    checkin_img = models.ImageField(upload_to='teacher_attendance', default='')
    checkout_img = models.ImageField(upload_to='teacher_attendance', default='', null=True)
    checkin_time = models.DateTimeField(null=True)
    checkout_time = models.DateTimeField(null=True)


class PendingRegistration(models.Model):
    id = models.AutoField
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    def __str__(self):
        return self.teacher.teacher_name


class Course(models.Model):  
    id = models.AutoField
    course_code =  models.CharField(max_length=6)
    course_name = models.CharField(max_length=50)
    teacher = models.ForeignKey(Teacher, null=True , on_delete=models.SET_NULL)

    def __str__(self):
        if self.teacher is not None:
            return f'{self.course_code} {self.course_name} | {self.teacher.teacher_name}'
        else:
            return f'{self.course_code} {self.course_name}'

class CourseAdminModel(admin.ModelAdmin):
    search_fields=('course_code', 'course_name')


class ClassRoom(models.Model):
    room_no = models.IntegerField(primary_key=True)

    def __str__(self):
        return str(self.room_no)


class ClassTiming(models.Model):
    start_time = models.TimeField(editable=True)
    end_time = models.TimeField(editable=True)

    def __str__(self):
        return str(self.start_time) + '-' + str(self.end_time)


class Timetable(models.Model):
    id = models.AutoField
    day = myFields.DayOfTheWeekField()
    time = models.ForeignKey(ClassTiming, on_delete=models.CASCADE)
    room = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f'Room {str(self.room)} : Day{self.day} - {str(self.time)} | {str(self.course)} '


class TimetableAdminModel(admin.ModelAdmin):
    search_fields=('day',)


class Student(models.Model):
    reg_no = models.CharField(max_length=20, primary_key=True)
    student_name = models.CharField(max_length=50)
    father_name = models.CharField(max_length=50)
    # email = models.CharField(max_length=50)
    face_img = models.ImageField(upload_to='students', default="")
    face_encodings = models.BinaryField(null=True)
    courses_enrolled = models.ManyToManyField(Course)


    def __str__(self):
        return f'{self.reg_no} : {self.student_name}'


class StudentAttendance(models.Model):
    Attendance_Statuses = (
        ('P', 'Present'),
        ('A', 'Absent'),
    )
    id = models.AutoField
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    time = models.DateTimeField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=1, choices=Attendance_Statuses, null=True)

    def __str__(self):
        return f'{self.status} | {self.time} | {self.student} | {self.course}'


class BulkAttendance(models.Model):
    id = models.AutoField
    time = models.DateTimeField(auto_now_add=True)
    room1_img = models.ImageField(upload_to=f'student_attendance/{datetime.now().year}/{datetime.now().month}/{datetime.now().day}/room1')
    room2_img = models.ImageField(upload_to=f'student_attendance/{datetime.now().year}/{datetime.now().month}/{datetime.now().day}/room2')

    def __str__(self):
        return str(self.time)


class SearchStudent(models.Model):
    id = models.AutoField
    reg_no = models.CharField(max_length=20, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)


class DataCSV(models.Model):
    data = models.BinaryField()