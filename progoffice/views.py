import base64
from itertools import count
from cgi import test
from mimetypes import encodings_map
import pickle
from xml.dom.minidom import TypeInfo
from cv2 import waitKey
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.core.mail import EmailMessage, send_mail
from pandas import date_range
from frams.tokens import generate_token
from frams import settings
from django.contrib.auth.models import User
from django.contrib import messages

from .models import Attendance, PendingRegistration, StudentAttendance, Teacher#, TeacherAttendance
from .forms import StudentForm, TeacherForm, UserForm, TeacherFaceAttendanceForm, TeacherFingerprintAttendanceForm

import cv2
import numpy as np
import face_recognition
from datetime import datetime
from django.db.models import Count, Q


def home(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return render(request, 'progoffice/index.html')
        else:
            return HttpResponse('404 - Page Not Found')
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
                    teacher  = Teacher(user_id=user)
                    teacher_form = TeacherForm(request.POST, request.FILES, instance=teacher)

                    if teacher_form.is_valid():
                        teacher_form.save()

                        path = 'media/teachers'
                        fileName = teacher_form.cleaned_data.get('img1')
                        img = cv2.imread(f'{path}/{fileName}')
                        # img = cv2.resize(img,(224,224),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)
                        try:
                            img = cv2.resize(img, (0, 0), None, 0.25, 0.25)
                            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        except:
                            messages.error(request, "Please Upload a Valid Picture!")
                            context = {
                                'teacher_form': teacher_form,
                                'user_form': user_form
                            }
                            return render(request, 'progoffice/add_teacher.html', context)
                        try:
                            faces = face_recognition.face_locations(img)
                        except:
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

                        # # for face in facesCurFrame:
                        # #     y1, x2, y2, x1 = face
                        # #     # y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                        # #     cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        # # img = cv2.resize(img, (1080, 720))
                        # # cv2.imshow("Image", img)
                        # # cv2.waitKey(0)
                        # print('NoOfFaces in counter: ', len(facesCurFrame))
                        # encodings_known = face_recognition.face_encodings(imgS, facesCurFrame)
                        # print(encodings_known)

                        # path = 'media'
                        # name = 'test.jpg'
                        # imgTest = cv2.imread(f'{path}/{name}')
                        # imgS = cv2.resize(imgTest, (0, 0), None, 0.25, 0.25)
                        # imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
                        # facesTestFrame = face_recognition.face_locations(imgS)
                        # # for face in facesCurFrame:
                        # #     y1, x2, y2, x1 = face
                        # #     # y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                        # #     cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        # # img = cv2.resize(img, (1080, 720))
                        # # cv2.imshow("Image", img)
                        # # cv2.waitKey(0)

                        # print('NoOfFaces in counter: ', len(facesTestFrame))
                        # encodings_test = face_recognition.face_encodings(imgS, facesTestFrame)
                        # print(encodings_test)

                        # for encodeFace, faceLoc in zip(encodings_known, facesCurFrame):
                        #     matches = face_recognition.compare_faces(encodings_test, encodeFace, 0.5)
                        #     faceDis = face_recognition.face_distance(encodings_test, encodeFace)
                        # # print(faceDis)
                        #     matchIndex = np.argmin(faceDis)

                        #     if matches[matchIndex]:
                        #         print('matched')
                        #         y1, x2, y2, x1 = faceLoc
                        #         # y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                        #         cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

                        # img = cv2.resize(img, (1080, 720))
                        # cv2.imshow("test", img)
                        # cv2.waitKey(0)
                        #     #     counter += 1
                        #     #     name = classNames[matchIndex].upper()
                        #     #     print (name, counter)

                            # Sending Confirmation Email
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

                            messages.success(request, 'Teacher Registered Successfully, Please Ask the Teacher to Verify their Email. Thank you!')
                            return redirect('index')

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
            return HttpResponse('404 - Page Not Found')

    else:
        return redirect('index')


def pendingRegistrations(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            if request.method == "POST":
                email = request.POST['email']
                teacher_user = User.objects.get(email__exact=email)
                teacher = Teacher.objects.get(user_id=teacher_user)
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
            return HttpResponse('404 - Page Not Found')
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
            return HttpResponse('404 - Page Not Found')
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
                    teacher = Teacher.objects.get(user_id=user)
                except(Teacher.DoesNotExist):
                    messages.error(request, 'Teacher Object does not exist!')
                    return redirect('pending_registrations')

                else:
                    form = TeacherForm(request.POST, request.FILES, instance=teacher)

                    if form.is_valid():
                        form.save()
                        try:
                            pendingReg = PendingRegistration.objects.get(teacher_id=teacher)
                        except(PendingRegistration.DoesNotExist):
                            messages.warning(request, 'Pending Registration is not present!')
                        else:
                            pendingReg.delete()

                        # Email Address Confirmation Email
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

                        messages.success(request, 'Registration Completed Successfully, Please Ask the Teacher to Verify their Email. Thank you!')
                        return redirect('pending_registrations')

                    else:
                        return render(request, 'authentication/complete_signup.html', {'form': form})

        else:
            return HttpResponse('404 - Page Not Found')

    else:
        return redirect('index')


def addStudent(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            if request.method == 'POST':
                form = StudentForm(request.POST, request.FILES)

                if form.is_valid():
                    form.save()
                    messages.success(request, 'Student Registered Successfully')
                    return redirect('index')
                else:
                    print(form.errors.as_data())
                    return render(request, 'progoffice/add_student.html', {'form': form})
            
            else:    
                form = StudentForm()
                return render(request, 'progoffice/add_student.html', {'form': form})
        
        else:
            return HttpResponse('404 - Page Not Found')
    
    else:
        return redirect('index')


def TeacherAttendance(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            
            return render(request, 'progoffice/teacher_attendance.html')
        else:
            return HttpResponse('404 - Page Not Found')
    else:
        return redirect('index')

    
def TeacherFaceAttendance(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            if request.method == 'POST':
                dict = Teacher.objects.aggregate(actifs=Count('user_id', filter=Q(user_id__is_active=True)), inactifs=Count('user_id', filter=Q(user_id__is_active=False)))
                if int(dict.get('actifs')) > 0:
                
                    form = TeacherFaceAttendanceForm(request.POST, request.FILES)
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
                        except:
                            print('Resize Failed')
                        try:
                            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                            faces = face_recognition.face_locations(img)
                        except:
                            messages.error(request, 'Error processing the image!')
                            return render(request, 'progoffice/teacher_face_attendance.html', {'form': form})
                        
                        if len(faces) < 1:
                            messages.error(request, 'No Face Detected!')
                            return render(request, 'progoffice/teacher_face_attendance.html', {'form': form})
                        elif len(faces) > 1:
                            messages.error(request, 'Multiple Faces Detected!')
                            return render(request, 'progoffice/teacher_face_attendance.html', {'form': form})
                        else:
                            encodings_test = face_recognition.face_encodings(img, faces)

                            encodings_known = np.array([])
                            pks = []
                            for obj in Teacher.objects.all():
                                np_bytes = base64.b64decode(obj.face_encodings)
                                print('Type: ', type(obj.user_id))
                                pks.append(obj.user_id)
                                print('Email: ', obj.user_id.email)
                                encodings_known = np.append(encodings_known, pickle.loads(np_bytes))

                            matches = face_recognition.compare_faces(encodings_known, encodings_test, 0.5)
                            faceDis = face_recognition.face_distance(encodings_known, encodings_test)
                            
                            print('Face Distance: ', faceDis)
                            matchIndex = np.argmin(faceDis)

                            if matches[matchIndex]:
                                print('Matched: ', pks[matchIndex])
                                teacher = Teacher.objects.get(user_id=pks[matchIndex])
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
                                        messages.warning(request, 'User has already checked out!')
                                        return render(request, 'progoffice/teacher_face_attendance.html', {'form': TeacherFaceAttendanceForm()})
                                    else:
                                        alreadyCheckedIn.checkout_img = attendance.checkin_img
                                        attendance.delete()
                                        alreadyCheckedIn.checkout_time = datetime.now()
                                        alreadyCheckedIn.save()
                                        messages.success(request, 'User checked out successfully')
                                        return render(request, 'progoffice/teacher_face_attendance.html', {'form': TeacherFaceAttendanceForm()})
                                else:
                                    attendance.teacher = teacher
                                    attendance.checkin_time = datetime.now()
                                    attendance.save()
                                    messages.success(request, 'User checked in successfully')
                                    return render(request, 'progoffice/teacher_face_attendance.html', {'form': TeacherFaceAttendanceForm()})

                    else:
                        return render(request, 'progoffice/teacher_attendance.html', {'form': form})
                else:
                    messages.warning(request, 'No users registered. Please register users first!')
                    return render(request, 'progoffice/teacher_face_attendance.html', {'form': TeacherFaceAttendanceForm()})
            return render(request, 'progoffice/teacher_face_attendance.html', {'form': TeacherFaceAttendanceForm()})
        else:
            return HttpResponse('404 - Page Not Found')
    else:
        return redirect('index')

    
def TeacherFingerprintAttendance(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return render(request, 'progoffice/teacher_fingerprint_attendance.html', {'form': TeacherFingerprintAttendance()})
        else:
            return HttpResponse('404 - Page Not Found')
    else:
        return redirect('index')