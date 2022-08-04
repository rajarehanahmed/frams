import base64
from cgitb import reset
import csv
import pickle
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.core.mail import EmailMessage, send_mail
# from pandas import date_range
from frams.tokens import generate_token
from frams import settings
from django.contrib.auth.models import User
from django.contrib import messages

from .models import Attendance, ClassTiming, DataCSV, PendingRegistration, ClassRoom, Student, StudentAttendance, Teacher, Timetable
from .forms import SearchStudentForm, StudentForm, TeacherAttendanceForm, TeacherForm, UserForm, BulkAttendanceForm

import cv2
import numpy as np
import face_recognition
from datetime import datetime
from django.db.models import Count, Q


def home(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            now = datetime.now()
            pendingRegs = PendingRegistration.objects.all()
            studentsCount = Student.objects.all().count()
            teachersCount = Teacher.objects.all().count()
            checkinCount = Attendance.objects.filter(checkin_time__year=now.year, checkin_time__month=now.month, checkin_time__day=now.day).count()
            checkoutCount = Attendance.objects.filter(checkout_time__year=now.year, checkout_time__month=now.month, checkout_time__day=now.day).count()
            classesCount = Timetable.objects.filter(day=now.weekday()).count()
            print('Total Teachers: ', teachersCount)
            print('Total Students: ', studentsCount)
            print('Class Today: ', classesCount)
            context = {
                'pendingRegs': pendingRegs,
                'students_count': studentsCount,
                'teachers_count': teachersCount,
                'classes_count': classesCount,
                'checkin_count': checkinCount,
                'checkout_count': checkoutCount,
            }
            return render(request, 'progoffice/index.html', context)
        else:
            raise Http404()
    else:
        return redirect('/signin')


def addTeacher(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            if request.method == 'POST':
                user_form = UserForm(request.POST)

                if user_form.is_valid():
                    user = user_form.save()
                    user.is_active = False
                    teacher  = Teacher(user=user)
                    teacher_form = TeacherForm(request.POST, request.FILES, instance=teacher)

                    if teacher_form.is_valid():
                        teacher_form.save()

                        if teacher.teacher_status == 'V':

                            # Detecting face in the image and storing encodings in the database
                            path = 'media/teachers/faces'
                            fileName = teacher_form.cleaned_data.get('face_img')
                            img = cv2.imread(f'{path}/{fileName}')
                            # img = cv2.resize(img,(224,224),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)
                            try:
                                img = cv2.resize(img, (0, 0), None, 0.25, 0.25)
                                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                            except:
                                user.delete()
                                teacher.delete()
                                messages.error(request, "Please Upload a Valid Picture!")
                                context = {
                                    'teacher_form': teacher_form,
                                    'user_form': user_form
                                }
                                return render(request, 'progoffice/add_teacher.html', context)
                            try:
                                faces = face_recognition.face_locations(img)
                            except:
                                user.delete()
                                teacher.delete()
                                messages.error(request, "Please Upload a Clear Picture!")
                                context = {
                                    'teacher_form': teacher_form,
                                    'user_form': user_form
                                }
                                return render(request, 'progoffice/add_teacher.html', context)
                            if len(faces) < 1:
                                user.delete()
                                teacher.delete()
                                messages.error(request, "No Face Detected, Please Upload a Clear Picture")
                                context = {
                                    'teacher_form': teacher_form,
                                    'user_form': user_form
                                }
                                return render(request, 'progoffice/add_teacher.html', context)
                            elif len(faces) > 1:
                                user.delete()
                                teacher.delete()
                                messages.error(request, "Multiple Faces Detected, Please Upload a Picture Containing only the Users Face")
                                context = {
                                    'teacher_form': teacher_form,
                                    'user_form': user_form
                                }
                                return render(request, 'progoffice/add_teacher.html', context)
                            else:
                                encodings = face_recognition.face_encodings(img, faces)[0]
                                print('Encodings Stored*********         : ', encodings)
                                np_bytes = pickle.dumps(encodings)
                                np_base64 = base64.b64encode(np_bytes)
                                teacher.face_encodings = np_base64
                                teacher.save()
                            
                                # Extracting keypoints from Fingerprint samples and storing in the database
                                sift = cv2.SIFT_create()
                                path = 'media/teachers/fingerprints'
                                filename_thumb = teacher_form.cleaned_data.get('right_thumb_img')
                                filename_index = teacher_form.cleaned_data.get('right_index_img')
                                filename_middle = teacher_form.cleaned_data.get('right_middle_img')
                                filename_ring = teacher_form.cleaned_data.get('right_ring_img')
                                filename_little = teacher_form.cleaned_data.get('right_little_img')

                                fingerprints = []
                                fingerprints.append(cv2.imread(f'{path}/{filename_thumb}'))
                                fingerprints.append(cv2.imread(f'{path}/{filename_index}'))
                                fingerprints.append(cv2.imread(f'{path}/{filename_middle}'))
                                fingerprints.append(cv2.imread(f'{path}/{filename_ring}'))
                                fingerprints.append(cv2.imread(f'{path}/{filename_little}'))

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
                                    
                                teacher.right_thumb_keypoints = encoded_keypoints[0]
                                teacher.right_index_keypoints = encoded_keypoints[1]
                                teacher.right_middle_keypoints = encoded_keypoints[2]
                                teacher.right_ring_keypoints = encoded_keypoints[3]
                                teacher.right_little_keypoints = encoded_keypoints[4]

                                teacher.right_thumb_descriptors = encoded_descriptors[0]
                                teacher.right_index_descriptors = encoded_descriptors[1]
                                teacher.right_middle_descriptors = encoded_descriptors[2]
                                teacher.right_ring_descriptors = encoded_descriptors[3]
                                teacher.right_little_descriptors = encoded_descriptors[4]
                                teacher.save()
                            

                        # Sending Confirmation Email
                        try:
                            current_site = get_current_site(request)
                            email_subject = "Confirm your email @ FRAMS - Login!!"
                            message = render_to_string("authentication/email_confirmation.html", {
                                'email': user.email,
                                'domain': current_site.domain,
                                'uid': force_str(urlsafe_base64_encode(force_bytes(user.pk))),
                                'token': generate_token.make_token(user)
                            })
                            email = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [user.email])
                            # email.fail_silently = True
                            email.send()
                        except:
                            user.delete()
                            messages.error(request, "Sending verification email failed!")
                            context = {
                                'teacher_form': teacher_form,
                                'user_form': user_form
                            }
                            return render(request, 'progoffice/add_teacher.html', context)
                            

                        messages.success(request, 'Teacher registered successfully, please ask the teacher to verify their email.')
                        context = {
                            'teacher_form': TeacherForm(),
                            'user_form': UserForm()
                        }
                        return render(request, 'progoffice/add_teacher.html', context)

                    else:
                        user.delete()
                        return render(request, 'progoffice/add_teacher.html', {'user_form': user_form, 'teacher_form': teacher_form})

                else:
                    return render(request, 'progoffice/add_teacher.html', {'user_form': user_form, 'teacher_form': TeacherForm(request.POST, request.FILES)})

            else:
                context = {
                    'teacher_form': TeacherForm(),
                    'user_form': UserForm()
                }
                return render(request, 'progoffice/add_teacher.html', context)

        else:
            raise Http404()

    else:
        return redirect('index')


def pendingRegistrations(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            if request.method == "POST":
                email = request.POST['email']
                teacher_user = User.objects.get(email__exact=email)
                teacher = Teacher.objects.get(user=teacher_user)
                form = TeacherForm(instance=teacher)
                context = {
                    'teacher': teacher,
                    't_user': teacher_user,
                    'form': form
                }
                return render(request, 'authentication/complete_signup.html', context)
            
            pendingRegs = PendingRegistration.objects.all()
            return render(request, 'authentication/pending_registration.html', {'pendingRegs': pendingRegs})
        else:
            raise Http404()
    else:
        return redirect('index')


def deletePendingReg(request):
    if request.user.is_authenticated:
        if request.user.is_superuser and request.method == 'POST':
            email = request.POST['email']
            try:
                user = User.objects.get(email=email)
            except(User.DoesNotExist):
                messages.error(request, 'User does not exist!')
                return redirect('pending_registrations')
            else:
                user.delete()
                messages.success(request, 'Registration Deleted Successfully')
                return redirect('pending_registrations')
        else:
            raise Http404()
    else:
        return redirect('index')


def completeSignup(request):
    if request.user.is_authenticated:
        if request.user.is_superuser and request.method == 'POST':
            email = request.POST['email']
            try:
                user = User.objects.get(email=email)
            except(User.DoesNotExist):
                messages.error(request, 'User does not exist!')
                return redirect('pending_registrations')

            else:
                try:
                    teacher = Teacher.objects.get(user=user)
                except(Teacher.DoesNotExist):
                    messages.error(request, 'Teacher Object does not exist!')
                    return redirect('pending_registrations')

                else:
                    form = TeacherForm(request.POST, request.FILES, instance=teacher)

                    if form.is_valid():
                        form.save()

                        # Detecting face in the image and storing encodings in the database
                        path = 'media/teachers/faces'
                        fileName = form.cleaned_data.get('face_img')
                        img = cv2.imread(f'{path}/{fileName}')
                        try:
                            img = cv2.resize(img, (0, 0), None, 0.25, 0.25)
                            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        except:
                            messages.error(request, "Please Upload a Valid Face Picture!")
                            return render(request, 'progoffice/add_teacher.html', {'form': form})
                        try:
                            faces = face_recognition.face_locations(img)
                        except:
                            messages.error(request, "Please Upload a Clear Face Picture!")
                            return render(request, 'progoffice/add_teacher.html', {'form': form})
                        if len(faces) < 1:
                            messages.error(request, "No Face Detected, Please Upload a Clear Face Picture")
                            context = {
                                'teacher_form': form,
                                'user_form': form
                            }
                            return render(request, 'progoffice/add_teacher.html', context)
                        elif len(faces) > 1:
                            messages.error(request, "Multiple Faces Detected, Please Upload a Picture Containing only the Users Face")
                            context = {
                                'teacher_form': form,
                                'user_form': form
                            }
                            return render(request, 'progoffice/add_teacher.html', context)
                        else:
                            encodings = face_recognition.face_encodings(img, faces)[0]
                            print('Encodings Stored*********         : ', encodings)
                            np_bytes = pickle.dumps(encodings)
                            np_base64 = base64.b64encode(np_bytes)
                            teacher.face_encodings = np_base64
                            teacher.save()
                        
                            # Extracting keypoints from Fingerprint samples and storing in the database
                            sift = cv2.SIFT_create()
                            path = 'media/teachers/fingerprints'
                            filename_thumb = form.cleaned_data.get('right_thumb_img')
                            filename_index = form.cleaned_data.get('right_index_img')
                            filename_middle = form.cleaned_data.get('right_middle_img')
                            filename_ring = form.cleaned_data.get('right_ring_img')
                            filename_little = form.cleaned_data.get('right_little_img')

                            fingerprints = []
                            fingerprints.append(cv2.imread(f'{path}/{filename_thumb}'))
                            fingerprints.append(cv2.imread(f'{path}/{filename_index}'))
                            fingerprints.append(cv2.imread(f'{path}/{filename_middle}'))
                            fingerprints.append(cv2.imread(f'{path}/{filename_ring}'))
                            fingerprints.append(cv2.imread(f'{path}/{filename_little}'))

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
                                
                            teacher.right_thumb_keypoints = encoded_keypoints[0]
                            teacher.right_index_keypoints = encoded_keypoints[1]
                            teacher.right_middle_keypoints = encoded_keypoints[2]
                            teacher.right_ring_keypoints = encoded_keypoints[3]
                            teacher.right_little_keypoints = encoded_keypoints[4]

                            teacher.right_thumb_descriptors = encoded_descriptors[0]
                            teacher.right_index_descriptors = encoded_descriptors[1]
                            teacher.right_middle_descriptors = encoded_descriptors[2]
                            teacher.right_ring_descriptors = encoded_descriptors[3]
                            teacher.right_little_descriptors = encoded_descriptors[4]


                        try:
                            pendingReg = PendingRegistration.objects.get(teacher_id=teacher)
                        except(PendingRegistration.DoesNotExist):
                            messages.warning(request, 'Pending Registration is not present!')
                        else:
                            pendingReg.delete()

                        # Email Address Confirmation Email
                        try:
                            current_site = get_current_site(request)
                            email_subject = "Confirm your email @ FRAMS - Login!!"
                            message2 = render_to_string("authentication/email_confirmation.html", {
                                'email': user.email,
                                'domain': current_site.domain,
                                'uid': force_str(urlsafe_base64_encode(force_bytes(user.pk))),
                                'token': generate_token.make_token(user)
                            })
                            email = EmailMessage(email_subject, message2, settings.EMAIL_HOST_USER, [user.email])
                            email.fail_silently = True
                            email.send()
                        except:
                            pr = PendingRegistration(teacher=teacher)
                            pr.save()
                            messages.error(request, "Sending verification email failed!")
                            return render(request, 'progoffice/add_teacher.html', {'form': form})
                        
                        teacher.save()
                        messages.success(request, 'Registration Completed Successfully, Please Ask the Teacher to Verify their Email. Thank you!')
                        return redirect('pending_registrations')

                    else:
                        return render(request, 'authentication/complete_signup.html', {'form': form})

        else:
            raise Http404()

    else:
        return redirect('index')


def teacherAttendance(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            
            return render(request, 'progoffice/teacher_attendance.html')
        else:
            raise Http404()
    else:
        return redirect('index')

    
def teacherFaceAttendance(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            if request.method == 'POST':
                dict = Teacher.objects.aggregate(actifs=Count('user', filter=Q(user__is_active=True)), inactifs=Count('user', filter=Q(user__is_active=False)))
                if int(dict.get('actifs')) > 0:
                
                    form = TeacherAttendanceForm(request.POST, request.FILES)
                    if form.is_valid():
                        now = datetime.now()
                        print('Year: ', now.year, ' Month: ', now.month, ' Day: ', now.day)
                        attendance = form.save()

                        path = 'media'
                        filename = attendance.checkin_img
                        print(filename)
                        img = cv2.imread(f'{path}/{filename}')

                        try:
                            img = cv2.resize(img, None, fx=0.25, fy=0.25)
                            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                            faces = face_recognition.face_locations(img)
                        except:
                            attendance.delete()
                            messages.error(request, 'Error processing the image!')
                            return render(request, 'progoffice/teacher_face_attendance.html', {'form': form})
                        
                        if len(faces) < 1:
                            attendance.delete()
                            messages.error(request, 'No Face Detected!')
                            return render(request, 'progoffice/teacher_face_attendance.html', {'form': form})
                        elif len(faces) > 1:
                            attendance.delete()
                            messages.error(request, 'Multiple Faces Detected!')
                            return render(request, 'progoffice/teacher_face_attendance.html', {'form': form})
                        else:
                            encodings_test = face_recognition.face_encodings(img, faces)[0]

                            encodeList = []
                            pks = []
                            
                            counter = 0
                            for obj in Teacher.objects.filter(teacher_status='V'):
                                counter += 1
                                print(counter)
                                np_bytes = base64.b64decode(obj.face_encodings)
                                pks.append(obj)
                                # print('Email: ', obj.user.email)
                                encodings = pickle.loads(np_bytes)
                                print('Type of Encodings fetched: ', type(encodings))
                                print('Encodings Stored*********         : ', encodings)
                                encodeList.append(encodings)
                                print(encodeList)
                                # encodings_known = np.append(encodings_known, encodings)


                            matches = face_recognition.compare_faces(encodeList, encodings_test, 0.6)
                            faceDis = face_recognition.face_distance(encodeList, encodings_test)
                            
                            print('Face Distance: ', faceDis)
                            matchIndex = np.argmin(faceDis)

                            if matches[matchIndex]:
                                print('Matched: ', pks[matchIndex])
                                teacher = pks[matchIndex]
                                print('Teacher Name: ' + teacher.teacher_name)
                                now = datetime.now()
                                try:
                                    alreadyCheckedIn = Attendance.objects.get(teacher=teacher, checkin_time__year=now.year, checkin_time__month=now.month, checkin_time__day=now.day)
                                except:
                                    print('already checkedin is False')
                                    alreadyCheckedIn = False
                                if alreadyCheckedIn is not False:
                                    if alreadyCheckedIn.checkout_time is not None:
                                        attendance.delete()
                                        messages.warning(request, teacher.teacher_name + ' has already checked out!')
                                        return render(request, 'progoffice/teacher_face_attendance.html', {'form': TeacherAttendanceForm()})
                                    else:
                                        alreadyCheckedIn.checkout_img = attendance.checkin_img
                                        attendance.delete()
                                        alreadyCheckedIn.checkout_time = datetime.now()
                                        alreadyCheckedIn.save()
                                        messages.success(request, teacher.teacher_name + ' checked out successfully')
                                        return render(request, 'progoffice/teacher_face_attendance.html', {'form': TeacherAttendanceForm()})
                                else:
                                    attendance.teacher = teacher
                                    attendance.checkin_time = datetime.now()
                                    attendance.save()
                                    messages.success(request, teacher.teacher_name + ' checked in successfully')
                                    return render(request, 'progoffice/teacher_face_attendance.html', {'form': TeacherAttendanceForm()})

                            messages.error(request, 'User is not registered!')
                            attendance.delete()
                            return render(request, 'progoffice/teacher_face_attendance.html', {'form': TeacherAttendanceForm()})
                    else:
                        return render(request, 'progoffice/teacher_face_attendance.html', {'form': form})
                else:
                    messages.warning(request, 'No users registered. Please register users first!')
                    return render(request, 'progoffice/teacher_face_attendance.html', {'form': TeacherAttendanceForm()})
            return render(request, 'progoffice/teacher_face_attendance.html', {'form': TeacherAttendanceForm()})
        else:
            raise Http404()
    else:
        return redirect('index')

    
def teacherFingerprintAttendance(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            if request.method == 'POST':
                dict = Teacher.objects.aggregate(actifs=Count('user', filter=Q(user__is_active=True)), inactifs=Count('user', filter=Q(user__is_active=False)))
                if int(dict.get('actifs')) > 0:
                    form = TeacherAttendanceForm(request.POST, request.FILES)
                    if form.is_valid():
                        now = datetime.now()
                        print('Year: ', now.year, ' Month: ', now.month, ' Day: ', now.day)
                        attendance = form.save()
                        path = 'media'
                        filename = attendance.checkin_img
                        print(filename)
                        sift = cv2.SIFT_create()
                        try:
                            img = cv2.imread(f'{path}/{filename}')
                            keypoints_test, descriptors_test = sift.detectAndCompute(img, None)
                        except:
                            attendance.delete()
                            messages.error(request, 'Error processing the image!')
                            return render(request, 'progoffice/teacher_fingerprint_attendance.html', {'form': form})

                        teacher_fingerprints = {}
                        for obj in Teacher.objects.filter(teacher_status='V'):
                            
                            #Extracting right thumb keypoints and descriptors
                            np_bytes = base64.b64decode(obj.right_thumb_keypoints)
                            points_list = pickle.loads(np_bytes)

                            right_thumb_kp = []
                            for point in points_list:
                                temp_kp = cv2.KeyPoint(x=point[0][0], y=point[0][1], size=point[1], angle=point[2], response=point[3], octave=point[4], class_id=point[5])
                                right_thumb_kp.append(temp_kp)

                            np_bytes = base64.b64decode(obj.right_thumb_descriptors)
                            right_thumb_desc = pickle.loads(np_bytes)

                            #Extracting right index finger keypoints and descriptors
                            np_bytes = base64.b64decode(obj.right_index_keypoints)
                            points_list = pickle.loads(np_bytes)

                            right_index_kp = []
                            for point in points_list:
                                temp_kp = cv2.KeyPoint(x=point[0][0], y=point[0][1], size=point[1], angle=point[2], response=point[3], octave=point[4], class_id=point[5])
                                right_index_kp.append(temp_kp)

                            np_bytes = base64.b64decode(obj.right_index_descriptors)
                            right_index_desc = pickle.loads(np_bytes)

                            #Extracting right middle finger keypoints and descriptors
                            np_bytes = base64.b64decode(obj.right_middle_keypoints)
                            points_list = pickle.loads(np_bytes)

                            right_middle_kp = []
                            for point in points_list:
                                temp_kp = cv2.KeyPoint(x=point[0][0], y=point[0][1], size=point[1], angle=point[2], response=point[3], octave=point[4], class_id=point[5])
                                right_middle_kp.append(temp_kp)

                            np_bytes = base64.b64decode(obj.right_middle_descriptors)
                            right_middle_desc = pickle.loads(np_bytes)

                            #Extracting right ring finger keypoints and descriptors
                            np_bytes = base64.b64decode(obj.right_ring_keypoints)
                            points_list = pickle.loads(np_bytes)

                            right_ring_kp = []
                            for point in points_list:
                                temp_kp = cv2.KeyPoint(x=point[0][0], y=point[0][1], size=point[1], angle=point[2], response=point[3], octave=point[4], class_id=point[5])
                                right_ring_kp.append(temp_kp)

                            np_bytes = base64.b64decode(obj.right_ring_descriptors)
                            right_ring_desc = pickle.loads(np_bytes)

                            #Extracting right little finger keypoints and descriptors
                            np_bytes = base64.b64decode(obj.right_little_keypoints)
                            points_list = pickle.loads(np_bytes)

                            right_little_kp = []
                            for point in points_list:
                                temp_kp = cv2.KeyPoint(x=point[0][0], y=point[0][1], size=point[1], angle=point[2], response=point[3], octave=point[4], class_id=point[5])
                                right_little_kp.append(temp_kp)

                            np_bytes = base64.b64decode(obj.right_little_descriptors)
                            right_little_desc = pickle.loads(np_bytes)

                            teacher_fingerprints.update({obj: {'right_thumb': {'keypoints': right_thumb_kp, 'descriptors': right_thumb_desc},
                                                                'right_index': {'keypoints': right_index_kp, 'descriptors': right_index_desc},
                                                                'right_middle': {'keypoints': right_middle_kp, 'descriptors': right_middle_desc},
                                                                'right_ring': {'keypoints': right_ring_kp, 'descriptors': right_ring_desc},
                                                                'right_little': {'keypoints': right_little_kp, 'descriptors': right_little_desc}}})
                        print(teacher_fingerprints)

                        best_score = 0
                        finger_matched = None
                        teacher_matched = None
                        for user in teacher_fingerprints:
                            for finger in teacher_fingerprints.get(user):

                                for value in finger:
                                    keypoints_known = teacher_fingerprints.get(user).get(finger).get('keypoints')
                                    descriptors_known = teacher_fingerprints.get(user).get(finger).get('descriptors')

                                matches = cv2.FlannBasedMatcher({'algorithm': 1, 'trees': 10},
                                                                {}).knnMatch(descriptors_test, descriptors_known, k=2)
                                
                                match_points = []

                                for p, q in matches:
                                    if p.distance < 0.1 * q.distance:
                                        match_points.append(p)
                                
                                keypoints = 0
                                if len(keypoints_known) < len(keypoints_test):
                                    keypoints = len(keypoints_known)
                                else:
                                    keypoints = len(keypoints_test)

                                if len(match_points) / keypoints * 100 > best_score:
                                    best_score = len(match_points) / keypoints * 100
                                    finger_matched = finger
                                    teacher_matched = user


                        print('BEST MATCH: ', teacher_matched)
                        print('FINGER MATCHED: ', finger_matched)
                        print('SCORE: ' + str(best_score))


                        if teacher_matched is not None:
                            print('Teacher Name: ' + teacher_matched.teacher_name)
                            now = datetime.now()
                            try:
                                alreadyCheckedIn = Attendance.objects.get(teacher=teacher_matched, checkin_time__year=now.year, checkin_time__month=now.month, checkin_time__day=now.day)
                            except:
                                print('already checkedin is False')
                                alreadyCheckedIn = False
                            if alreadyCheckedIn is not False:
                                if alreadyCheckedIn.checkout_time is not None:
                                    attendance.delete()
                                    messages.warning(request, teacher_matched.teacher_name + ' has already checked out!')
                                    return render(request, 'progoffice/teacher_fingerprint_attendance.html', {'form': TeacherAttendanceForm()})
                                else:
                                    alreadyCheckedIn.checkout_img = attendance.checkin_img
                                    attendance.delete()
                                    alreadyCheckedIn.checkout_time = datetime.now()
                                    alreadyCheckedIn.save()
                                    messages.success(request, teacher_matched.teacher_name + ' checked out successfully')
                                    return render(request, 'progoffice/teacher_fingerprint_attendance.html', {'form': TeacherAttendanceForm()})
                            else:
                                attendance.teacher = teacher_matched
                                attendance.checkin_time = datetime.now()
                                attendance.save()
                                messages.success(request, teacher_matched.teacher_name + ' checked in successfully')
                                return render(request, 'progoffice/teacher_fingerprint_attendance.html', {'form': TeacherAttendanceForm()})

                        else:
                            messages.error(request, 'User is not registered!')
                            attendance.delete()
                            return render(request, 'progoffice/teacher_fingerprint_attendance.html', {'form': TeacherAttendanceForm()})
                    else:
                        return render(request, 'progoffice/teacher_fingerprint_attendance.html', {'form': form})
                else:
                    messages.warning(request, 'No users registered. Please register users first!')
                    return render(request, 'progoffice/teacher_fingerprint_attendance.html', {'form': TeacherAttendanceForm()})
            else:
                return render(request, 'progoffice/teacher_fingerprint_attendance.html', {'form': TeacherAttendanceForm()})
        else:
            raise Http404()
    else:
        return redirect('index')


def teacherReport(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            if request.method == 'POST':
                email = request.POST['email']
                date_from = request.POST['date_from']
                date_to = request.POST['date_to']

                res = None
                today = datetime.today().strftime('%Y-%m-%d')
                today_obj = datetime.strptime(today, '%Y-%m-%d')
                if email and date_from and date_to:
                    start_date = datetime.strptime(date_from, "%Y-%m-%d")
                    end_date = datetime.strptime(date_to, "%Y-%m-%d")
                    try:
                        teacher=Teacher.objects.get(user=User.objects.get(email=email))
                    except:
                        pass
                    if start_date > end_date or start_date > today_obj or end_date > today_obj:
                        messages.error(request, 'Invalid Date! Please note that "Date to" must be greater than or equal to "Date From".')
                        return redirect('teacher_report')
                    
                    elif start_date == end_date:
                        res = Attendance.objects.filter(teacher=teacher).filter(Q(checkin_time__year=start_date.year) and Q(checkin_time__month=start_date.month) and Q(checkin_time__day=start_date.day))
                    else:
                        try:
                            res = Attendance.objects.filter(teacher=teacher).filter(Q(checkin_time__range=[date_from, f'{date_to} 23:59:59']))
                        except:
                            res = None

                elif not email and date_from and date_to:
                    start_date = datetime.strptime(date_from, "%Y-%m-%d")
                    end_date = datetime.strptime(date_to, "%Y-%m-%d")
                    if start_date > end_date or start_date > today_obj or end_date > today_obj:
                        messages.error(request, 'Invalid Date! Please note that "Date to" must be greater than or equal to "Date From".')
                        return redirect('teacher_report')
                    
                    elif start_date == end_date:
                        try:
                            res = Attendance.objects.filter(Q(checkin_time__year=start_date.year) and Q(checkin_time__month=start_date.month) and Q(checkin_time__day=start_date.day))
                        except:
                            res = None
                    else:
                        try:
                            res = Attendance.objects.filter(Q(checkin_time__range=[date_from, f'{date_to} 23:59:59']))
                        except:
                            res = None
                
                elif not email and not date_to and date_from:
                    start_date = datetime.strptime(date_from, "%Y-%m-%d")
                    if start_date > today_obj:
                        messages.error(request, 'Invalid Date! Ensure date is not greater than today. Please note that "Date to" must be greater than or equal to "Date From".')
                        return redirect('teacher_report')
                    elif start_date == today_obj:
                        try:
                            res = Attendance.objects.filter(Q(checkin_time__year=start_date.year) and Q(checkin_time__month=start_date.month) and Q(checkin_time__day=start_date.day))
                        except:
                            res = None
                    else:
                        try:
                            res = Attendance.objects.filter(Q(checkin_time__range=[date_from, f'{today} 23:59:59']))
                        except:
                            res = None

                elif email and date_from and not date_to:
                    start_date = datetime.strptime(date_from, "%Y-%m-%d")
                    try:
                        teacher=Teacher.objects.get(user=User.objects.get(email=email))
                    except:
                        pass
                    if start_date > today_obj:
                        messages.error(request, 'Invalid Date! Ensure date is not greater than today.  Please note that "Date to" must be greater than or equal to "Date From".')
                        return redirect('teacher_report')
                    
                    elif start_date == today_obj:
                        try:
                            res = Attendance.objects.filter(teacher=teacher).filter(Q(checkin_time__year=start_date.year) and Q(checkin_time__month=start_date.month) and Q(checkin_time__day=start_date.day))
                        except:
                            res = None
                    else:
                        try:
                            res = Attendance.objects.filter(teacher=teacher).filter(Q(checkin_time__range=[date_from, f'{today} 23:59:59']))
                        except:
                            res = None

                elif email and not date_from and not date_to:
                    try:
                        teacher=Teacher.objects.get(user=User.objects.get(email=email))
                        res = Attendance.objects.filter(teacher=teacher)
                    except:
                        res = None
                
                elif not date_from and date_to:
                    messages.error(request, 'Invalid Date! Ensure date is not greater than today.  Please note that "Date to" must be greater than or equal to "Date From".')

                if res:
                    data_csv = DataCSV()
                    np_bytes = pickle.dumps(res)
                    np_base64 = base64.b64encode(np_bytes)
                    data_csv.data = np_base64
                    data_csv.save()
                    print('PRIMARY KEY: ***************************', data_csv.pk)
                    print('TYPE: ', type(data_csv.pk))
                    context = {
                        'search': res,
                        'email': email,
                        'date_from': date_from,
                        'date_to': date_to,
                        'data_obj_pk': data_csv.pk,
                    }
                else:
                    context = {
                        'search': res,
                        'email': email,
                        'date_from': date_from,
                        'date_to': date_to,
                    }
                return render(request, 'progoffice/teacher_report.html', context)
            

            return render(request, 'progoffice/teacher_report.html')
        else:
            raise Http404()
    else:
        return redirect('index')


def addStudent(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            if request.method == 'POST':
                form = StudentForm(request.POST, request.FILES)

                if form.is_valid():
                    student = form.save()


                    # Detecting face in the image and storing encodings in the database
                    path = 'media/students'
                    fileName = form.cleaned_data.get('face_img')
                    img = cv2.imread(f'{path}/{fileName}')
                    try:
                        img = cv2.resize(img, (0, 0), None, 0.25, 0.25)
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        faces = face_recognition.face_locations(img)
                    except:
                        student.delete()
                        messages.error(request, "Error Processing the image!")
                        return render(request, 'progoffice/add_student.html', {'form': form})
                    if len(faces) < 1:
                        student.delete()
                        messages.error(request, "No Face Detected, Please Upload a Clear Picture")
                        return render(request, 'progoffice/add_student.html', {'form': form})
                    elif len(faces) > 1:
                        student.delete()
                        messages.error(request, "Multiple Faces Detected, Please Upload a Picture Containing only the Users Face")
                        return render(request, 'progoffice/add_student.html', {'form': form})
                    else:
                        encodings = face_recognition.face_encodings(img, faces)[0]
                        print('Encodings Stored*********         : ', encodings)
                        np_bytes = pickle.dumps(encodings)
                        np_base64 = base64.b64encode(np_bytes)
                        student.face_encodings = np_base64
                        student.save()



                        messages.success(request, 'Student Registered Successfully')
                        return render(request, 'progoffice/add_student.html', {'form': StudentForm()})
                else:
                    return render(request, 'progoffice/add_student.html', {'form': form})
            
            else:    
                return render(request, 'progoffice/add_student.html', {'form': StudentForm()})
        
        else:
            raise Http404()
    
    else:
        return redirect('index')


def studentAttendance(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            if request.method == 'POST':
                form = BulkAttendanceForm(request.POST, request.FILES)
                if form.is_valid():
                    bulkAttendance = form.save()
                    now = datetime.now()
                    print('Year: ', now.year, ' Month: ', now.month, ' Day: ', now.day)


                    
                    now = datetime.now()

                    curTime = now.time().replace(microsecond=0)
                    print('Current Time: ', curTime)
                    
                    classTime = None
                    for timing in ClassTiming.objects.all():
                        if timing.start_time <= curTime <= timing.end_time:
                            classTime = timing
                    print('classTime: ', classTime)
                    print('Weekday: ', now.weekday())
                    
                    if classTime is None or now.weekday() > 4:
                        bulkAttendance.delete()
                        messages.error(request, 'No class at this time')
                        return render(request, 'progoffice/student_attendance.html', {'form': BulkAttendanceForm()})

                    if Student.objects.all().count() > 1:
                        counter = 0
                        for classroom in ClassRoom.objects.all()[:2]:
                            counter += 1
                            print('Counter: ', counter)
                            timeTable = Timetable.objects.filter(room=classroom, time=classTime)
                            print('timeTable.count(): ', timeTable.count())
                            print('Room: ', classroom.room_no)
                            if timeTable.count() > 1:
                                messages.error(request, 'Timetable is incorrect')
                                return render(request, 'progoffice/student_attendance.html', {'form': BulkAttendanceForm()})
                            elif timeTable.count() != 1:
                                messages.error(request, f'No class at this time in Room{classroom.room_no}')
                                continue
                                # return render(request, 'progoffice/student_attendance.html', {'form': BulkAttendanceForm()})
                            course = timeTable[0].course
                            print('Course: ', course)
                            if course is None:
                                messages.error(request, f'No course is registered at this time in Room{classroom.room_no}')
                                continue
                                # return render(request, 'progoffice/student_attendance.html', {'form': BulkAttendanceForm()})
                            
                            students_enrolled = course.student_set.all()
                            print('Students Enrolled: ', students_enrolled)

                            path = 'media'
                            filename = getattr(bulkAttendance, f'room{classroom.room_no}_img')
                            print(filename)
                            try:
                                img = cv2.imread(f'{path}/{filename}')
                                img = cv2.resize(img, None, fx=0.25, fy=0.25)
                                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                                faces = face_recognition.face_locations(img)
                            except:
                                bulkAttendance.delete()
                                messages.error(request, f'Error processing Classroom{classroom.room_no} image!')
                                return render(request, 'progoffice/teacher_face_attendance.html', {'form': form})
                            
                            if len(faces) < 1:
                                bulkAttendance.delete()
                                messages.error(request, f'No Faces Detected in Classroom{classroom.room_no}!')
                                return render(request, 'progoffice/teacher_face_attendance.html', {'form': form})
                            else:
                                encodings_test = face_recognition.face_encodings(img, faces)

                                encodings_known = []
                                pks = []

                                for student in students_enrolled:
                                    np_bytes = base64.b64decode(student.face_encodings)
                                    pks.append(student)
                                    encodings = pickle.loads(np_bytes)
                                    print('Type of Encodings fetched: ', type(encodings))
                                    print('Encodings Stored*********         : ', encodings)
                                    encodings_known.append(encodings)
                                    print(encodings_known)

                                for encoding in encodings_test:
                                    matches = face_recognition.compare_faces(encodings_known, encoding, 0.6)
                                    faceDis = face_recognition.face_distance(encodings_known, encoding)
                                    
                                    print('Face Distance: ', faceDis)
                                    matchIndex = np.argmin(faceDis)

                                    if matches[matchIndex]:
                                        print('Matched: ', pks[matchIndex])


                                        student = pks[matchIndex]
                                        print('Teacher Name: ' + student.student_name)
                                        
                                        try:
                                            alreadyMarked = StudentAttendance.objects.get(student=student, time__year=now.year, time__month=now.month, time__day=now.day, course=course)
                                        except:
                                            print('already Marked is False')
                                            alreadyMarked = False
                                        if alreadyMarked is not False:
                                            messages.warning(request, student.reg_no + ' ' + student.student_name + 's attendance already marked')
                                            
                                        else:
                                            attendance = StudentAttendance(student=student, time=now, course=course, status='P')
                                            attendance.save()

                                for student in students_enrolled:
                                    if StudentAttendance.objects.filter(student=student, time__year=now.year, time__month=now.month, time__day=now.day, course=course).count() != 1:
                                        attendance = StudentAttendance(student=student, time=now, course=course, status='A')
                                        attendance.save()
                        
                        if StudentAttendance.objects.filter(time__year=now.year, time__month=now.month, time__day=now.day).count() > 1:
                            messages.success(request, 'Attendance marked Successfully')
                            return render(request, 'progoffice/student_attendance.html', {'form': BulkAttendanceForm()})

                        return render(request, 'progoffice/student_attendance.html', {'form': BulkAttendanceForm()})
                              

                    else:
                        messages.warning(request, 'No students registered')
                        return render(request, 'progoffice/student_attendance.html', {'form': form})

                else:
                    return render(request, 'progoffice/student_attendance.html', {'form': form})
            else:
                return render(request, 'progoffice/student_attendance.html', {'form': BulkAttendanceForm()})
        else:
            raise Http404()
    else:
        return redirect('index')


def studentReport(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            if request.method == 'POST':
                form = SearchStudentForm(request.POST)
                date_from = request.POST['date_from']
                date_to = request.POST['date_to']
                if form.is_valid():
                    search_instance = form.save()
                    reg_no = search_instance.reg_no
                    course = search_instance.course
                    print(type(course))
                    print('REG_NO: ', reg_no)
                    print('COURSE', course)
                    print('DATE FROM: ', date_from)
                    print('DATE TO: ', date_to)




                    res = None
                    today = datetime.today().strftime('%Y-%m-%d')
                    today_obj = datetime.strptime(today, '%Y-%m-%d')
                    if reg_no and course and date_from and date_to:
                        start_date = datetime.strptime(date_from, "%Y-%m-%d")
                        end_date = datetime.strptime(date_to, "%Y-%m-%d")
                        try:
                            student = Student.objects.get(reg_no=reg_no)
                        except:
                            pass
                        if start_date > end_date or start_date > today_obj or end_date > today_obj:
                            messages.error(request, 'Invalid Date! Please note that "Date to" must be greater than or equal to "Date From".')
                            context = {
                                'search': res,
                                'form': form,
                                'date_from': date_from,
                                'date_to': date_to,
                            }
                            return render(request, 'progoffice/student_report.html', context)
                        
                        elif start_date == end_date:
                            res = StudentAttendance.objects.filter(student=student, course=course).filter(Q(time__year=start_date.year) and Q(time__month=start_date.month) and Q(time__day=start_date.day))
                        else:
                            try:
                                res = StudentAttendance.objects.filter(student=student, course=course).filter(Q(time__range=[date_from, f'{date_to} 23:59:59']))
                            except:
                                res = None
                    
                    elif reg_no and not course and date_from and date_to:
                        start_date = datetime.strptime(date_from, "%Y-%m-%d")
                        end_date = datetime.strptime(date_to, "%Y-%m-%d")
                        try:
                            student = Student.objects.get(reg_no=reg_no)
                        except:
                            pass
                        if start_date > end_date or start_date > today_obj or end_date > today_obj:
                            messages.error(request, 'Invalid Date! Please note that "Date to" must be greater than or equal to "Date From".')
                            context = {
                                'search': res,
                                'form': form,
                                'date_from': date_from,
                                'date_to': date_to,
                            }
                            return render(request, 'progoffice/student_report.html', context)
                        
                        elif start_date == end_date:
                            res = StudentAttendance.objects.filter(student=student).filter(Q(time__year=start_date.year) and Q(time__month=start_date.month) and Q(time__day=start_date.day))
                        else:
                            try:
                                res = StudentAttendance.objects.filter(student=student).filter(Q(time__range=[date_from, f'{date_to} 23:59:59']))
                            except:
                                res = None

                    elif not reg_no and not course and date_from and date_to:
                        start_date = datetime.strptime(date_from, "%Y-%m-%d")
                        end_date = datetime.strptime(date_to, "%Y-%m-%d")
                        if start_date > end_date or start_date > today_obj or end_date > today_obj:
                            messages.error(request, 'Invalid Date! Please note that "Date to" must be greater than or equal to "Date From".')
                            context = {
                                'search': res,
                                'form': form,
                                'date_from': date_from,
                                'date_to': date_to,
                            }
                            return render(request, 'progoffice/student_report.html', context)
                        
                        elif start_date == end_date:
                            try:
                                res = StudentAttendance.objects.filter(Q(time__year=start_date.year) and Q(time__month=start_date.month) and Q(time__day=start_date.day))
                            except:
                                res = None
                        else:
                            try:
                                res = StudentAttendance.objects.filter(Q(time__range=[date_from, f'{date_to} 23:59:59']))
                            except:
                                res = None
                    
                    elif not reg_no and not course and not date_to and date_from:
                        start_date = datetime.strptime(date_from, "%Y-%m-%d")
                        if start_date > today_obj:
                            messages.error(request, 'Invalid Date! Ensure date is not greater than today. Please note that "Date to" must be greater than or equal to "Date From".')
                            context = {
                                'search': res,
                                'form': form,
                                'date_from': date_from,
                                'date_to': date_to,
                            }
                            return render(request, 'progoffice/student_report.html', context)
                        elif start_date == today_obj:
                            try:
                                res = StudentAttendance.objects.filter(Q(time__year=start_date.year) and Q(time__month=start_date.month) and Q(time__day=start_date.day))
                            except:
                                res = None
                        else:
                            try:
                                res = StudentAttendance.objects.filter(Q(time__range=[date_from, f'{today} 23:59:59']))
                            except:
                                res = None

                    elif reg_no and not course and date_from and not date_to:
                        start_date = datetime.strptime(date_from, "%Y-%m-%d")
                        try:
                            student=Student.objects.get(reg_no=reg_no)
                        except:
                            pass
                        if start_date > today_obj:
                            messages.error(request, 'Invalid Date! Ensure date is not greater than today.  Please note that "Date to" must be greater than or equal to "Date From".')
                            context = {
                                'search': res,
                                'form': form,
                                'date_from': date_from,
                                'date_to': date_to,
                            }
                            return render(request, 'progoffice/student_report.html', context)
                        
                        elif start_date == today_obj:
                            try:
                                res = StudentAttendance.objects.filter(student=student).filter(Q(time__year=start_date.year) and Q(time__month=start_date.month) and Q(time__day=start_date.day))
                            except:
                                res = None
                        else:
                            try:
                                res = StudentAttendance.objects.filter(student=student).filter(Q(time__range=[date_from, f'{today} 23:59:59']))
                            except:
                                res = None

                    elif reg_no and not course and not date_from and not date_to:
                        try:
                            student=Student.objects.get(reg_no=reg_no)
                            res = StudentAttendance.objects.filter(student=student)
                        except:
                            res = None
                    
                    elif not reg_no and course and not date_from and not date_to:
                        try:
                            res = StudentAttendance.objects.filter(course=course)
                        except:
                            res = None
                    
                    elif not reg_no and course and date_from and not date_to:
                        start_date = datetime.strptime(date_from, "%Y-%m-%d")
                        if start_date > today_obj:
                            messages.error(request, 'Invalid Date! Ensure date is not greater than today.  Please note that "Date to" must be greater than or equal to "Date From".')
                            context = {
                                'search': res,
                                'form': form,
                                'date_from': date_from,
                                'date_to': date_to,
                            }
                            return render(request, 'progoffice/student_report.html', context)
                        
                        elif start_date == today_obj:
                            try:
                                res = StudentAttendance.objects.filter(course=course).filter(Q(time__year=start_date.year) and Q(time__month=start_date.month) and Q(time__day=start_date.day))
                            except:
                                res = None
                        else:
                            try:
                                res = StudentAttendance.objects.filter(course=course).filter(Q(time__range=[date_from, f'{today} 23:59:59']))
                            except:
                                res = None
                    
                    elif not reg_no and course and date_from and date_to:
                        start_date = datetime.strptime(date_from, "%Y-%m-%d")
                        end_date = datetime.strptime(date_to, "%Y-%m-%d")
                        if start_date > end_date or start_date > today_obj or end_date > today_obj:
                            messages.error(request, 'Invalid Date! Please note that "Date to" must be greater than or equal to "Date From".')
                            context = {
                                'search': res,
                                'form': form,
                                'date_from': date_from,
                                'date_to': date_to,
                            }
                            return render(request, 'progoffice/student_report.html', context)
                        
                        elif start_date == end_date:
                            res = StudentAttendance.objects.filter(course=course).filter(Q(time__year=start_date.year) and Q(time__month=start_date.month) and Q(time__day=start_date.day))
                        else:
                            try:
                                res = StudentAttendance.objects.filter(course=course).filter(Q(time__range=[date_from, f'{date_to} 23:59:59']))
                            except:
                                res = None
                    
                    elif reg_no and course and date_from and not date_to:
                        start_date = datetime.strptime(date_from, "%Y-%m-%d")
                        try:
                            student = Student.objects.get(reg_no=reg_no)
                        except:
                            pass
                        if start_date > today_obj:
                            messages.error(request, 'Invalid Date! Ensure date is not greater than today.  Please note that "Date to" must be greater than or equal to "Date From".')
                            context = {
                                'search': res,
                                'form': form,
                                'date_from': date_from,
                                'date_to': date_to,
                            }
                            return render(request, 'progoffice/student_report.html', context)
                        
                        elif start_date == today_obj:
                            try:
                                res = StudentAttendance.objects.filter(student=student, course=course).filter(Q(time__year=start_date.year) and Q(time__month=start_date.month) and Q(time__day=start_date.day))
                            except:
                                res = None
                        else:
                            try:
                                res = StudentAttendance.objects.filter(student=student, course=course).filter(Q(time__range=[date_from, f'{today} 23:59:59']))
                            except:
                                res = None
                    
                    elif reg_no and course and not date_from and not date_to:
                        try:
                            student=Student.objects.get(reg_no=reg_no)
                            res = StudentAttendance.objects.filter(student=student, course=course)
                        except:
                            res = None
                    
                    elif not reg_no and course and not date_from and not date_to:
                        try:
                            res = StudentAttendance.objects.filter(course=course)
                        except:
                            res = None
                    
                    elif not date_from and date_to:
                        messages.error(request, 'Invalid Date! Ensure date is not greater than today.  Please note that "Date to" must be greater than or equal to "Date From".')
                    
                    if res:
                        data_csv = DataCSV()
                        np_bytes = pickle.dumps(res)
                        np_base64 = base64.b64encode(np_bytes)
                        data_csv.data = np_base64
                        data_csv.save()
                        print('PRIMARY KEY: ***************************', data_csv.pk)
                        print('TYPE: ', type(data_csv.pk))
                        context = {
                            'search': res,
                            'form': form,
                            'date_from': date_from,
                            'date_to': date_to,
                            'data_obj_pk': data_csv.pk,
                        }
                    else:
                        context = {
                            'search': res,
                            'form': form,
                            'date_from': date_from,
                            'date_to': date_to,
                        }
                    return render(request, 'progoffice/student_report.html', context)


                return HttpResponse('Hi there')
            else:
                return render(request, 'progoffice/student_report.html', {'form': SearchStudentForm()})
        else:
            raise Http404()
    else:
        return redirect('index')


def generateTeacherCSV(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            pk = request.GET['pk']
            print(pk)
            try:
                data_obj = DataCSV.objects.get(pk=pk)
                np_bytes = base64.b64decode(data_obj.data)
                query_set = pickle.loads(np_bytes)
            except:
                messages.warning(request, 'No dat found!')
                return redirect('teacher_report')
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=teacher_report.csv'

            # Create a CSV writer
            writer = csv.writer(response)

            writer.writerow(['Sr No', 'Teacher Name', 'Email', 'Check In', 'Check Out'])

            for count, obj in enumerate(query_set):
                writer.writerow([count+1, obj.teacher.teacher_name, obj.teacher.user.email, obj.checkin_time, obj.checkout_time])

            print(query_set)

            return response
        else:
            raise Http404()
    else:
        return redirect('index')


def generateStudentCSV(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            pk = request.GET['pk']
            print(pk)
            try:
                data_obj = DataCSV.objects.get(pk=pk)
                np_bytes = base64.b64decode(data_obj.data)
                query_set = pickle.loads(np_bytes)
            except:
                messages.warning(request, 'No dat found!')
                return redirect('student_report')
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=student_report.csv'

            # Create a CSV writer
            writer = csv.writer(response)

            writer.writerow(['Sr No', 'Reg No', 'Name', 'Course', 'Date', 'Attendance'])

            for count, obj in enumerate(query_set):
                writer.writerow([count+1, obj.student.reg_no, obj.student.student_name, obj.course, obj.time, obj.status ])

            print(query_set)

            return response
        else:
            raise Http404()
    else:
        return redirect('index')
