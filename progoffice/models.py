from cmath import exp
import time
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
import cv2
from PIL import Image as Img
from PIL import ExifTags
from io import BytesIO
from django.core.files import File
import face_recognition
import numpy as np
from django.core.exceptions import ValidationError
import pickle
import base64

from . import myFields
from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class Teacher(models.Model):
    Teacher_Statuses = (
        ('V', 'visiting'),
        ('P', 'permanent'),
    )
    Teacher_designations = (
        ('P', 'professor'),
        ('AP', 'asst. professor')
    )

    def check_faces(face_img_obj):
        pilImage = Img.open(BytesIO(face_img_obj.read()))
        img = np.array(pilImage)

        try:
            img = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            faces = face_recognition.face_locations(img)
        except:
            raise ValidationError('Error processing the image, please upload a clear picture with face focused')
        if len(faces) < 1:
            raise ValidationError('No faces detected')
        elif len(faces) > 1:
            raise ValidationError('Multiple faces detected')
        
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    teacher_name = models.CharField(max_length=50)
    teacher_designation = models.CharField(max_length=2, choices=Teacher_designations)
    teacher_status = models.CharField(max_length=1, choices=Teacher_Statuses)
    face_img = models.ImageField(upload_to='teachers/faces', default="", validators=[check_faces])
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

    def save(self, *args, **kwargs):
        if self.teacher_status == 'V':
            try:
                img = Img.open(self.face_img)
                img = np.array(img)
            except:
                img = None
            
            if img is not None:
                try:
                    # img = cv2.resize(img, (0, 0), None, 0.25, 0.25)
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    faces = face_recognition.face_locations(img)
                    print('No. of Faces: ', len(faces))
                    encodings = face_recognition.face_encodings(img, faces)[0]
                    print('Encodings Stored*********         : ', encodings)
                    np_bytes = pickle.dumps(encodings)
                    np_base64 = base64.b64encode(np_bytes)
                    self.face_encodings = np_base64
                except:
                    raise ValidationError('Error processing face image')
            
            # Extracting keypoints from Fingerprint samples and storing in the database
            sift = cv2.SIFT_create()
            fingerprints = []
            try:
                fingerprints.append(np.array(Img.open(self.right_thumb_img)))
            except:
                pass
            try:
                fingerprints.append(np.array(Img.open(self.right_index_img)))
            except:
                pass
            try:
                fingerprints.append(np.array(Img.open(self.right_middle_img)))
            except:
                pass
            try:
                fingerprints.append(np.array(Img.open(self.right_ring_img)))
            except:
                pass
            try:
                fingerprints.append(np.array(Img.open(self.right_little_img)))
            except:
                pass

            encoded_keypoints = []
            encoded_descriptors = []
            for fingerprint in fingerprints:
                keypoints, descriptors = sift.detectAndCompute(fingerprint, None)

                print('Before*******************')
                print(keypoints, descriptors)
            
                points_list = []
                for point in keypoints:
                    temp = (point.pt, point.size, point.angle, point.response, point.octave, point.class_id)
                    points_list.append(temp)

                np_bytes = pickle.dumps(points_list)
                encoded_keypoints.append(base64.b64encode(np_bytes))

                np_bytes = pickle.dumps(descriptors)
                encoded_descriptors.append(base64.b64encode(np_bytes))


            try: 
                self.right_thumb_keypoints = encoded_keypoints[0]
                self.right_thumb_descriptors = encoded_descriptors[0]
            except:
                pass
            try:
                self.right_index_keypoints = encoded_keypoints[1]
                self.right_index_descriptors = encoded_descriptors[1]
            except:
                pass
            try:
                self.right_middle_keypoints = encoded_keypoints[2]
                self.right_middle_descriptors = encoded_descriptors[2]
            except:
                pass
            try:
                self.right_ring_keypoints = encoded_keypoints[3]
                self.right_ring_descriptors = encoded_descriptors[3]
            except:
                pass
            try:
                self.right_little_keypoints = encoded_keypoints[4]
                self.right_little_descriptors = encoded_descriptors[4]
            except:
                pass

        super().save(*args, **kwargs)

    def __str__(self):
        if self.teacher_status == 'V':
            return self.teacher_name + " (Visiting)"
        else:
            return self.teacher_name + " (Permanent)"


class TeacherAdminModel(admin.ModelAdmin):
    search_fields=('teacher_name', 'teacher_designation', 'teacher_status',)


class Attendance(models.Model):
    class Meta:
        verbose_name = _('Teacher Attendance')
        verbose_name_plural = _('Teacher Attendance')
    id = models.AutoField
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)
    checkin_img = models.ImageField(upload_to='teacher_attendance', default='')
    checkout_img = models.ImageField(upload_to='teacher_attendance', default='', null=True)
    checkin_time = models.DateTimeField(null=True)
    checkout_time = models.DateTimeField(null=True)


class AttendanceAdminModel(admin.ModelAdmin):
    search_fields=('checkin_time', 'checkout_time', 'id')


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


class ClassRoomAdminModel(admin.ModelAdmin):
    search_fields=('room_no',)


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
    def check_faces(face_img_obj):
        try:
            pilImage = Img.open(BytesIO(face_img_obj.read()))
            img = np.array(pilImage)
            img = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            faces = face_recognition.face_locations(img)
        except:
            raise ValidationError('Error processing the image, please upload a clear picture with face focused')
        if len(faces) < 1:
            raise ValidationError('No faces detected')
        elif len(faces) > 1:
            raise ValidationError('Multiple faces detected')

    reg_no = models.CharField(max_length=20, unique=True, primary_key=True)
    student_name = models.CharField(max_length=50)
    father_name = models.CharField(max_length=50)
    face_img = models.ImageField(upload_to='students', default="", validators=[check_faces])
    face_encodings = models.BinaryField(null=True)
    courses_enrolled = models.ManyToManyField(Course)

    def save(self, *args, **kwargs):
        try:
            img = Img.open(self.face_img)
            img = np.array(img)
        except:
            img = None

        if img is not None:
            try:
                # img = cv2.resize(img, (0, 0), None, 0.25, 0.25)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                faces = face_recognition.face_locations(img)
                print('No. of Faces: ', len(faces))
                encodings = face_recognition.face_encodings(img, faces)[0]
                print('Encodings Stored*********         : ', encodings)
                np_bytes = pickle.dumps(encodings)
                np_base64 = base64.b64encode(np_bytes)
                self.face_encodings = np_base64
            except:
                raise ValidationError('Error processing the image')

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.reg_no} : {self.student_name}'


class StudentAttendance(models.Model):
    Attendance_Statuses = (
        ('P', 'Present'),
        ('A', 'Absent'),
    )
    id = models.AutoField
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_timing = models.ForeignKey(ClassTiming, on_delete=models.SET_NULL, null=True)
    time = models.DateTimeField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=1, choices=Attendance_Statuses, null=True)

    def __str__(self):
        return f'{self.status} | {self.time} | {self.student} | {self.course}'


class StudentAttendanceAdminModel(admin.ModelAdmin):
    search_fields=('time', 'status', 'id')


class BulkAttendance(models.Model):
    id = models.AutoField
    time = models.DateTimeField(auto_now_add=True)
    room1_img = models.ImageField(upload_to=f'student_attendance/{datetime.now().year}/{datetime.now().month}/{datetime.now().day}/room1')
    room2_img = models.ImageField(upload_to=f'student_attendance/{datetime.now().year}/{datetime.now().month}/{datetime.now().day}/room2')

    def __str__(self):
        return str(self.time)


class BulkAttendanceAdminModel(admin.ModelAdmin):
    search_fields=('time',)


class SearchStudent(models.Model):
    id = models.AutoField
    reg_no = models.CharField(max_length=20, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)


class DataCSV(models.Model):
    data = models.BinaryField()