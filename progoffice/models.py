import datetime
from tkinter.tix import Tree
from django.db import models
from django.contrib.auth.models import User
from .import myFields


class Teacher(models.Model):
    Teacher_Statuses = (
        ('V', 'visiting'),
        ('P', 'permanent'),
    )
    Teacher_designations = (
        ('P', 'professor'),
        ('AP', 'asst. professor')
    )
    # instance.user.username
    # def getcurrentusername(instance, filename):
    #     return "/teacher/{0}/{1}".format(instance.user_id.username, filename)
        
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
        return self.course_code + " " + self.course_name + " " + self.teacher.teacher_name


class Room(models.Model):
    room_no = models.IntegerField(primary_key=True)

    def __str__(self):
        return str(self.room_no)


class Timetable(models.Model):
    id = models.AutoField
    day = myFields.DayOfTheWeekField(default="")
    time = models.TimeField(editable=True, default=datetime.time(16, 00))
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, default="")

    def __str__(self):
        return 'Room:' + str(self.room.room_no) + '  Course: ' + str(self.course)


class Student(models.Model):
    reg_no = models.CharField(max_length=20, primary_key=True)
    student_name = models.CharField(max_length=50)
    father_name = models.CharField(max_length=50)
    # email = models.CharField(max_length=50)
    face_img = models.ImageField(upload_to='students', default="")
    courses_enrolled = models.ManyToManyField(Course, null=True)
    # img2 = models.ImageField(upload_to='students', default="")
    # img3 = models.ImageField(upload_to='students', default="")


    def __str__(self):
        return self.reg_no + ' ' + self.student_name


class StudentAttendance(models.Model):
    id = models.AutoField
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.student.reg_no + " " + self.student.student_name


# class TeacherAttendance(models.Model):
#     id = models.AutoField
#     teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)
#     checkin_time = models.DateTimeField(null=True)
#     checkout_time = models.DateTimeField(null=True)
#     checkin_img = models.ImageField(upload_to='teacher_attendance', default='')
#     checkout_img = models.ImageField(upload_to='teacher_attendance', default='', null=True)

    # def __str__(self):
    #     return self.teacher.teacher_name + str(self.checkin_time)





# class Enrollment(models.Model):
#     id = models.AutoField
#     student = models.ForeignKey(Student, on_delete=models.CASCADE)
#     # course = models.ForeignKey(Teacher_Course, on_delete=models.CASCADE)
#     # course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
#     # teacher_id = models.ForeignKey(Teacher, on_delete=models.CASCADE)

#     def __str__(self):
#         return self.student.student_name