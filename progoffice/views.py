from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.core.mail import EmailMessage, send_mail
from frams.tokens import generate_token
from frams import settings
from django.contrib.auth.models import User
from django.contrib import messages

from .models import PendingRegistration, Student, Teacher, TeacherAttendance
from .forms import StudentForm, TeacherAttendanceForm, TeacherForm, UserForm

import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime

# Create your views here.


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
                    # user = User.objects.get(username=user_form.cleaned_data['username'])

                    # if user_form.cleaned_data['password'] == p1:
                    teacher  = Teacher(user_id=user)
                    teacher_form = TeacherForm(request.POST, request.FILES, instance=teacher)

                    if teacher_form.is_valid():
                        teacher_form.save()
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

                    # else:
                    #     user.delete()
                    #     messages.error(request, 'Passwords do not match')
                    #     return render(request, 'progoffice/add_teacher.html', {'user_form': user_form, 'teacher_form': TeacherForm()})

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
    User.objects.get(email='rajarehan.ahmd@gmail.com').delete()
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


def markTeacherAttendance(request):
    if request.method == 'POST':
        form = TeacherAttendanceForm(request.POST, request.FILES)
        if form.is_valid():
            facePic = form.cleaned_data.get('face')
            attendance = TeacherAttendance(checkin_image=facePic)
            attendance.save()

            path = 'media/teacher_attendance'
            img = cv2.imread(f'{path}/{facePic}')
            # imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            facesCurFrame = face_recognition.face_locations(imgS)
            print('NoOfFaces in counter: ', len(facesCurFrame))
            # if len(facesCurFrame) = 1:

            encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
            print(encodesCurFrame)
            cap = cv2.VideoCapture(0)
            if (cap.isOpened()== False):
                print("Error opening video stream or file")
            # Read until video is completed
            while(cap.isOpened()):
                # Capture frame-by-frame
                ret, frame = cap.read()
                if ret == True:
                    # Display the resulting frame
                    cv2.imshow('Frame',frame)
                    # Press Q on keyboard to  exit
                    if cv2.waitKey(25) & 0xFF == ord('q'):
                        break
                # Break the loop
                else:
                    break
            # When everything done, release the video capture object
            cap.release()
            # Closes all the frames
            cv2.destroyAllWindows
            
            # cv2.imshow('Webcam', img)
            # cv2.waitKey(2000)



            messages.success(request, 'Attendance Marked Successfully')
            return render(request, 'progoffice/teacher_attendance.html', {'form': TeacherAttendanceForm()})
        else:
            return render(request, 'progoffice/teacher_attendance.html', {'form': form})
    return render(request, 'progoffice/teacher_attendance.html', {'form': TeacherAttendanceForm()})