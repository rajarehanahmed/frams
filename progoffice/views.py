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
from frams.tokens import generate_token
from frams import settings
from django.contrib.auth.models import User
from django.contrib import messages

from .models import Attendance, BulkAttendance, ClassTiming, Course, DataCSV, PendingRegistration, ClassRoom, Student, StudentAttendance, Teacher, Timetable
from .forms import SearchCourseForm, SearchStudentForm, StudentForm, TeacherAttendanceForm, TeacherForm, UserForm, BulkAttendanceForm

import cv2
import numpy as np
import face_recognition
from datetime import datetime
from django.db.models import Q


def home(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            now = datetime.now()
            pendingRegs = PendingRegistration.objects.all()
            studentsCount = Student.objects.all().count()
            teachersCount = Teacher.objects.all().count()
            checkinCount = Attendance.objects.filter(checkin_time__year=now.year, checkin_time__month=now.month, checkin_time__day=now.day).count()
            checkoutCount = Attendance.objects.filter(checkout_time__year=now.year, checkout_time__month=now.month, checkout_time__day=now.day).count()
            classesCount = Timetable.objects.filter(day=now.weekday()).count()
            
            curTime = now.time().replace(microsecond=0)

            classTime = None
            for timing in ClassTiming.objects.all():
                if timing.start_time <= curTime <= timing.end_time:
                    classTime = timing
            currentClassTime = None
            isTaken = None
            if classTime:
                currentClasses = Timetable.objects.filter(time=classTime, day=now.weekday())
                if currentClasses.count() > 0:
                    currentClassTime = classTime
                    isTaken = BulkAttendance.objects.filter(Q(time__range=[f'{now.date()} {classTime.start_time}', f'{now.date()} {classTime.end_time}']))
                    if isTaken.count() > 0:
                        isTaken = 'Taken'
                    else:
                        isTaken = 'Not taken'

            classTime = ClassTiming.objects.filter(start_time__gt=curTime).order_by('start_time')
            # print('Next Class: ', classTime)
            nextClassTime = None
            if classTime.count() > 0:
                nextClasses = Timetable.objects.filter(time=classTime[0], day=now.weekday())
                print('Next ClassTime: ', nextClasses)
                if nextClasses.count() > 0:
                    nextClassTime = f'at {nextClasses[0].time.start_time}'
                    print('nextClassTime: ', nextClassTime)

            if nextClassTime is None:
                if now.weekday() >= 4:
                    nextClasses = Timetable.objects.filter(day__gte=0).order_by('day')
                    if nextClasses.count() > 1:
                        nextClassTime = f'on {days[int(nextClasses[0].day)]}'
                else:
                    nextClasses = Timetable.objects.filter(day__gt=now.weekday()).order_by('day')
                    if nextClasses.count() > 1:
                        nextClassTime = f'on {days[int(nextClasses[0].day)]}'
            
            print('Current: ', currentClassTime, isTaken)
            print('Next: ', nextClassTime)

            context = {
                'pendingRegs': pendingRegs,
                'students_count': studentsCount,
                'teachers_count': teachersCount,
                'classes_count': classesCount,
                'checkin_count': checkinCount,
                'checkout_count': checkoutCount,
                'current_class_time': currentClassTime,
                'is_taken': isTaken,
                'next_class_time': nextClassTime,
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
                    user.save()
                    teacher  = Teacher(user=user)
                    teacher_form = TeacherForm(request.POST, request.FILES, instance=teacher)

                    if teacher_form.is_valid():
                        teacher_form.save()

                        # if teacher.teacher_status == 'V':

                            # Detecting face in the image and storing encodings in the database
                            # path = 'media/teachers/faces'
                            # fileName = teacher_form.cleaned_data.get('face_img')
                            # img = cv2.imread(f'{path}/{fileName}')
                            # # img = cv2.resize(img,(224,224),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)
                            # try:
                            #     img = cv2.resize(img, (0, 0), None, 0.25, 0.25)
                            #     img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                            # except:
                            #     user.delete()
                            #     teacher.delete()
                            #     messages.error(request, "Please Upload a Valid Picture!")
                            #     context = {
                            #         'teacher_form': teacher_form,
                            #         'user_form': user_form
                            #     }
                            #     return render(request, 'progoffice/add_teacher.html', context)
                            # try:
                            #     faces = face_recognition.face_locations(img)
                            # except:
                            #     user.delete()
                            #     teacher.delete()
                            #     messages.error(request, "Please Upload a Clear Picture!")
                            #     context = {
                            #         'teacher_form': teacher_form,
                            #         'user_form': user_form
                            #     }
                            #     return render(request, 'progoffice/add_teacher.html', context)
                            # if len(faces) < 1:
                            #     user.delete()
                            #     teacher.delete()
                            #     messages.error(request, "No Face Detected, Please Upload a Clear Picture")
                            #     context = {
                            #         'teacher_form': teacher_form,
                            #         'user_form': user_form
                            #     }
                            #     return render(request, 'progoffice/add_teacher.html', context)
                            # elif len(faces) > 1:
                            #     user.delete()
                            #     teacher.delete()
                            #     messages.error(request, "Multiple Faces Detected, Please Upload a Picture Containing only the Users Face")
                            #     context = {
                            #         'teacher_form': teacher_form,
                            #         'user_form': user_form
                            #     }
                            #     return render(request, 'progoffice/add_teacher.html', context)
                            # else:
                            #     encodings = face_recognition.face_encodings(img, faces)[0]
                            #     print('Encodings Stored*********         : ', encodings)
                            #     np_bytes = pickle.dumps(encodings)
                            #     np_base64 = base64.b64encode(np_bytes)
                            #     teacher.face_encodings = np_base64
                            #     teacher.save()
                            
                                # Extracting keypoints from Fingerprint samples and storing in the database
                                # sift = cv2.SIFT_create()
                                # path = 'media/teachers/fingerprints'
                                # filename_thumb = teacher_form.cleaned_data.get('right_thumb_img')
                                # filename_index = teacher_form.cleaned_data.get('right_index_img')
                                # filename_middle = teacher_form.cleaned_data.get('right_middle_img')
                                # filename_ring = teacher_form.cleaned_data.get('right_ring_img')
                                # filename_little = teacher_form.cleaned_data.get('right_little_img')

                                # fingerprints = []
                                # fingerprints.append(cv2.imread(f'{path}/{filename_thumb}'))
                                # fingerprints.append(cv2.imread(f'{path}/{filename_index}'))
                                # fingerprints.append(cv2.imread(f'{path}/{filename_middle}'))
                                # fingerprints.append(cv2.imread(f'{path}/{filename_ring}'))
                                # fingerprints.append(cv2.imread(f'{path}/{filename_little}'))

                                # encoded_keypoints = []
                                # encoded_descriptors = []
                                # for fingerprint in fingerprints:
                                #     keypoints, descriptors = sift.detectAndCompute(fingerprint, None)

                                #     print('Before*******************')
                                #     print(keypoints, descriptors)
                                
                                #     points_list = []
                                #     for point in keypoints:
                                #         temp = (point.pt, point.size, point.angle, point.response, point.octave, point.class_id)
                                #         points_list.append(temp)


                                #     np_bytes = pickle.dumps(points_list)
                                #     encoded_keypoints.append(base64.b64encode(np_bytes))


                                #     np_bytes = pickle.dumps(descriptors)
                                #     encoded_descriptors.append(base64.b64encode(np_bytes))
                                    
                                # teacher.right_thumb_keypoints = encoded_keypoints[0]
                                # teacher.right_index_keypoints = encoded_keypoints[1]
                                # teacher.right_middle_keypoints = encoded_keypoints[2]
                                # teacher.right_ring_keypoints = encoded_keypoints[3]
                                # teacher.right_little_keypoints = encoded_keypoints[4]

                                # teacher.right_thumb_descriptors = encoded_descriptors[0]
                                # teacher.right_index_descriptors = encoded_descriptors[1]
                                # teacher.right_middle_descriptors = encoded_descriptors[2]
                                # teacher.right_ring_descriptors = encoded_descriptors[3]
                                # teacher.right_little_descriptors = encoded_descriptors[4]
                                # teacher.save()
                            

                        # Sending Confirmation Email
                        try:
                            current_site = get_current_site(request)
                            email_subject = "Confirm your email @ FRAMS - Login!!"
                            message = render_to_string("authentication/email_confirmation.html", {
                                'name': teacher.teacher_name,
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
                try:
                    user = User.objects.get(email=email)
                    teacher = Teacher.objects.get(user=user)
                    form = TeacherForm(instance=teacher)
                except:
                    messages.error(request, 'Error fetching Pending Registration')
                    pendingRegs = PendingRegistration.objects.all()
                    return render(request, 'authentication/pending_registration.html', {'pending_regs': pendingRegs})
                context = {
                    'user': user,
                    'form': form
                }
                return render(request, 'authentication/complete_signup.html', context)
            
            pendingRegs = PendingRegistration.objects.all()
            return render(request, 'authentication/pending_registration.html', {'pending_regs': pendingRegs})
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

                        # if teacher.teacher_status == 'V':
                        #     print("VVVVVVVVVVVVVVVVVV")
                        #     # Detecting face in the image and storing encodings in the database
                        #     path = 'media/teachers/faces'
                        #     fileName = form.cleaned_data['face_img']
                        #     img = cv2.imread(f'{path}/{fileName}')
                        #     try:
                        #         # img = cv2.resize(img, (0, 0), None, 0.25, 0.25)
                        #         img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        #         faces = face_recognition.face_locations(img)
                        #         print('Faces: ', len(faces))
                        #     except:
                        #         os.remove(teacher.face_img.path)
                        #         os.remove(teacher.right_thumb_img.path)
                        #         os.remove(teacher.right_index_img.path)
                        #         os.remove(teacher.right_middle_img.path)
                        #         os.remove(teacher.right_ring_img.path)
                        #         os.remove(teacher.right_little_img.path)
                        #         teacher.face_img.delete()
                        #         teacher.right_thumb_img.delete()
                        #         teacher.right_index_img.delete()
                        #         teacher.right_middle_img.delete()
                        #         teacher.right_ring_img.delete()
                        #         teacher.right_little_img.delete()
                        #         messages.error(request, "Error processing the image, please upload a clear Face Picture!")
                        #         context = {
                        #             'user': user,
                        #             'form': form
                        #         }
                        #         return render(request, 'authentication/complete_signup.html', context)
                        #     if len(faces) < 1:
                        #         os.remove(teacher.face_img.path)
                        #         teacher.face_img.delete()
                        #         os.remove(teacher.right_thumb_img.path)
                        #         os.remove(teacher.right_index_img.path)
                        #         os.remove(teacher.right_middle_img.path)
                        #         os.remove(teacher.right_ring_img.path)
                        #         os.remove(teacher.right_little_img.path)
                        #         teacher.face_img.delete()
                        #         teacher.right_thumb_img.delete()
                        #         teacher.right_index_img.delete()
                        #         teacher.right_middle_img.delete()
                        #         teacher.right_ring_img.delete()
                        #         teacher.right_little_img.delete()
                        #         messages.error(request, "No face detected, please upload a clear Face Picture")
                        #         context = {
                        #             'user': user,
                        #             'form': form
                        #         }
                        #         return render(request, 'authentication/complete_signup.html', context)
                        #     elif len(faces) > 1:
                        #         os.remove(teacher.face_img.path)
                        #         os.remove(teacher.right_thumb_img.path)
                        #         os.remove(teacher.right_index_img.path)
                        #         os.remove(teacher.right_middle_img.path)
                        #         os.remove(teacher.right_ring_img.path)
                        #         os.remove(teacher.right_little_img.path)
                        #         teacher.face_img.delete()
                        #         teacher.right_thumb_img.delete()
                        #         teacher.right_index_img.delete()
                        #         teacher.right_middle_img.delete()
                        #         teacher.right_ring_img.delete()
                        #         teacher.right_little_img.delete()
                        #         messages.error(request, "Multiple faces detected, please upload a picture containing only the User's Face")
                        #         context = {
                        #             'user': user,
                        #             'form': form
                        #         }
                        #         return render(request, 'authentication/complete_signup.html', context)
                        #     else:
                        #         encodings = face_recognition.face_encodings(img, faces)[0]
                        #         # print('Encodings Stored*********         : ', encodings)
                        #         np_bytes = pickle.dumps(encodings)
                        #         np_base64 = base64.b64encode(np_bytes)
                        #         teacher.face_encodings = np_base64
                            
                        #         # Extracting keypoints and descriptors from fingerprint samples and saving in the database
                        #         sift = cv2.SIFT_create()
                        #         path = 'media/teachers/fingerprints'
                        #         filename_thumb = form.cleaned_data.get('right_thumb_img')
                        #         filename_index = form.cleaned_data.get('right_index_img')
                        #         filename_middle = form.cleaned_data.get('right_middle_img')
                        #         filename_ring = form.cleaned_data.get('right_ring_img')
                        #         filename_little = form.cleaned_data.get('right_little_img')

                        #         fingerprints = []
                        #         fingerprints.append(cv2.imread(f'{path}/{filename_thumb}'))
                        #         fingerprints.append(cv2.imread(f'{path}/{filename_index}'))
                        #         fingerprints.append(cv2.imread(f'{path}/{filename_middle}'))
                        #         fingerprints.append(cv2.imread(f'{path}/{filename_ring}'))
                        #         fingerprints.append(cv2.imread(f'{path}/{filename_little}'))

                        #         encoded_keypoints = []
                        #         encoded_descriptors = []
                        #         for fingerprint in fingerprints:
                        #             keypoints, descriptors = sift.detectAndCompute(fingerprint, None)

                        #             # print('Before*******************')
                        #             # print(keypoints, descriptors)
                                
                        #             points_list = []
                        #             for point in keypoints:
                        #                 temp = (point.pt, point.size, point.angle, point.response, point.octave, point.class_id)
                        #                 points_list.append(temp)


                        #             np_bytes = pickle.dumps(points_list)
                        #             encoded_keypoints.append(base64.b64encode(np_bytes))


                        #             np_bytes = pickle.dumps(descriptors)
                        #             encoded_descriptors.append(base64.b64encode(np_bytes))
                                    
                        #         teacher.right_thumb_keypoints = encoded_keypoints[0]
                        #         teacher.right_index_keypoints = encoded_keypoints[1]
                        #         teacher.right_middle_keypoints = encoded_keypoints[2]
                        #         teacher.right_ring_keypoints = encoded_keypoints[3]
                        #         teacher.right_little_keypoints = encoded_keypoints[4]

                        #         teacher.right_thumb_descriptors = encoded_descriptors[0]
                        #         teacher.right_index_descriptors = encoded_descriptors[1]
                        #         teacher.right_middle_descriptors = encoded_descriptors[2]
                        #         teacher.right_ring_descriptors = encoded_descriptors[3]
                        #         teacher.right_little_descriptors = encoded_descriptors[4]

                        try:
                            pr = PendingRegistration.objects.get(teacher=teacher)
                            print('Pending Registration: ', pr)
                            pr.delete()
                        except:
                            pass

                        # Send Email Confirmation Email
                        try:
                            current_site = get_current_site(request)
                            email_subject = "Confirm your email @ FRAMS - Login!!"
                            message2 = render_to_string("authentication/email_confirmation.html", {
                                'name': teacher.teacher_name,
                                'domain': current_site.domain,
                                'uid': force_str(urlsafe_base64_encode(force_bytes(user.pk))),
                                'token': generate_token.make_token(user)
                            })
                            email = EmailMessage(email_subject, message2, settings.EMAIL_HOST_USER, [user.email])
                            email.send()
                        except:
                            # try:
                            #     os.remove(teacher.face_img.path)
                            #     os.remove(teacher.right_thumb_img.path)
                            #     os.remove(teacher.right_index_img.path)
                            #     os.remove(teacher.right_middle_img.path)
                            #     os.remove(teacher.right_ring_img.path)
                            #     os.remove(teacher.right_little_img.path)
                            #     teacher.face_img.delete()
                            #     teacher.right_thumb_img.delete()
                            #     teacher.right_index_img.delete()
                            #     teacher.right_middle_img.delete()
                            #     teacher.right_ring_img.delete()
                            #     teacher.right_little_img.delete()
                            # except:
                            #     pass
                            pr = PendingRegistration(teacher=teacher)
                            pr.save()
                            messages.error(request, "Sending verification email failed!")
                            context = {
                                'user': user,
                                'form': form
                            }
                            return render(request, 'authentication/complete_signup.html', context)
                        
                        teacher.save()
                        messages.success(request, 'Registration Completed Successfully, Please Ask the Teacher to Verify their Email.')
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
            if datetime.now().weekday() > 4:
                messages.warning(request, 'Today is off!')
                return redirect('index')
            return render(request, 'progoffice/teacher_attendance.html')
        else:
            raise Http404()
    else:
        return redirect('index')

    
def teacherFaceAttendance(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            if datetime.now().weekday() > 4:
                messages.warning(request, 'Today is off!')
                return redirect('index')
            if request.method == 'POST':
                users = User.objects.filter(is_active=True)
                if Teacher.objects.filter(user__in=list(users), teacher_status='V').count() > 0:
                
                    form = TeacherAttendanceForm(request.POST, request.FILES)
                    if form.is_valid():
                        now = datetime.now()
                        # print('Year: ', now.year, ' Month: ', now.month, ' Day: ', now.day)
                        attendance = form.save()

                        path = 'media'
                        filename = attendance.checkin_img
                        # print(filename)
                        img = cv2.imread(f'{path}/{filename}')

                        try:
                            # img = cv2.resize(img, None, fx=0.25, fy=0.25)
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
                            
                            for obj in Teacher.objects.filter(teacher_status='V', user__in=list(users)):
                                try:
                                    np_bytes = base64.b64decode(obj.face_encodings)
                                except:
                                    continue
                                pks.append(obj)
                                # print('Email: ', obj.user.email)
                                encodings = pickle.loads(np_bytes)
                                # print('Encodings Stored*********         : ', encodings)
                                encodeList.append(encodings)
                                # print(encodeList)
                                # encodings_known = np.append(encodings_known, encodings)


                            matches = face_recognition.compare_faces(encodeList, encodings_test, 0.6)
                            faceDis = face_recognition.face_distance(encodeList, encodings_test)
                            
                            matchIndex = np.argmin(faceDis)

                            if matches[matchIndex]:
                                teacher = pks[matchIndex]
                                print('Teacher Name: ' + teacher.teacher_name)
                                print('Face Distance: ', faceDis[matchIndex])
                                now = datetime.now()
                                try:
                                    alreadyCheckedIn = Attendance.objects.get(teacher=teacher, checkin_time__year=now.year, checkin_time__month=now.month, checkin_time__day=now.day)
                                except:
                                    # print('already checkedin is False')
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
            if datetime.now().weekday() > 4:
                messages.warning(request, 'Today is off!')
                return redirect('index')
            if request.method == 'POST':
                users = User.objects.filter(is_active=True)
                if Teacher.objects.filter(user__in=list(users), teacher_status='V').count() > 0:
                    form = TeacherAttendanceForm(request.POST, request.FILES)
                    if form.is_valid():
                        now = datetime.now()
                        # print('Year: ', now.year, ' Month: ', now.month, ' Day: ', now.day)
                        attendance = form.save()
                        path = 'media'
                        filename = attendance.checkin_img
                        # print(filename)
                        sift = cv2.SIFT_create()
                        try:
                            img = cv2.imread(f'{path}/{filename}')
                            keypoints_test, descriptors_test = sift.detectAndCompute(img, None)
                        except:
                            attendance.delete()
                            messages.error(request, 'Error processing the image!')
                            return render(request, 'progoffice/teacher_fingerprint_attendance.html', {'form': form})

                        teacher_fingerprints = {}
                        for obj in Teacher.objects.filter(teacher_status='V', user__in=users):
                            
                            #Extracting right thumb keypoints and descriptors
                            try:
                                np_bytes = base64.b64decode(obj.right_thumb_keypoints)
                            except:
                                continue
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
                        # print(teacher_fingerprints)

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
                                # print('already checkedin is False')
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
                        return redirect('teacher_report_admin')
                    
                    elif start_date == end_date:
                        res = Attendance.objects.filter(teacher=teacher).filter(Q(checkin_time__year=start_date.year) and Q(checkin_time__month=start_date.month) and Q(checkin_time__day=start_date.day)).order_by('-checkin_time')
                    else:
                        try:
                            res = Attendance.objects.filter(teacher=teacher).filter(Q(checkin_time__range=[date_from, f'{date_to} 23:59:59'])).order_by('-checkin_time')
                        except:
                            res = None

                elif not email and date_from and date_to:
                    start_date = datetime.strptime(date_from, "%Y-%m-%d")
                    end_date = datetime.strptime(date_to, "%Y-%m-%d")
                    if start_date > end_date or start_date > today_obj or end_date > today_obj:
                        messages.error(request, 'Invalid Date! Please note that "Date to" must be greater than or equal to "Date From".')
                        return redirect('teacher_report_admin')
                    
                    elif start_date == end_date:
                        try:
                            res = Attendance.objects.filter(Q(checkin_time__year=start_date.year) and Q(checkin_time__month=start_date.month) and Q(checkin_time__day=start_date.day)).order_by('teacher', '-checkin_time')
                        except:
                            res = None
                    else:
                        try:
                            res = Attendance.objects.filter(Q(checkin_time__range=[date_from, f'{date_to} 23:59:59'])).order_by('teacher', '-checkin_time')
                        except:
                            res = None
                
                elif not email and not date_to and date_from:
                    start_date = datetime.strptime(date_from, "%Y-%m-%d")
                    if start_date > today_obj:
                        messages.error(request, 'Invalid Date! Ensure date is not greater than today. Please note that "Date to" must be greater than or equal to "Date From".')
                        return redirect('teacher_report_admin')
                    elif start_date == today_obj:
                        try:
                            res = Attendance.objects.filter(Q(checkin_time__year=start_date.year) and Q(checkin_time__month=start_date.month) and Q(checkin_time__day=start_date.day)).order_by('teacher', '-checkin_time')
                        except:
                            res = None
                    else:
                        try:
                            res = Attendance.objects.filter(Q(checkin_time__range=[date_from, f'{today} 23:59:59'])).order_by('teacher', '-checkin_time')
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
                        return redirect('teacher_report_admin')
                    
                    elif start_date == today_obj:
                        try:
                            res = Attendance.objects.filter(teacher=teacher).filter(Q(checkin_time__year=start_date.year) and Q(checkin_time__month=start_date.month) and Q(checkin_time__day=start_date.day)).order_by('-checkin_time')
                        except:
                            res = None
                    else:
                        try:
                            res = Attendance.objects.filter(teacher=teacher).filter(Q(checkin_time__range=[date_from, f'{today} 23:59:59'])).order_by('-checkin_time')
                        except:
                            res = None

                elif email and not date_from and not date_to:
                    try:
                        teacher=Teacher.objects.get(user=User.objects.get(email=email))
                        res = Attendance.objects.filter(teacher=teacher).order_by('-checkin_time')
                    except:
                        res = None
                
                elif not email and not date_from and not date_to:
                    res = Attendance.objects.all().order_by('teacher', '-checkin_time')
                    if res.count() < 1:
                        res = None
                
                elif not date_from and date_to:
                    messages.error(request, 'Invalid Date! Ensure date is not greater than today.  Please note that "Date to" must be greater than or equal to "Date From".')

                if res:
                    data_csv = DataCSV()
                    np_bytes = pickle.dumps(res)
                    np_base64 = base64.b64encode(np_bytes)
                    data_csv.data = np_base64
                    data_csv.save()
                    # print('PRIMARY KEY: ***************************', data_csv.pk)
                    # print('TYPE: ', type(data_csv.pk))
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

            res = Attendance.objects.all().order_by('teacher', '-checkin_time')
            if res.count() > 1:
                data_csv = DataCSV()
                np_bytes = pickle.dumps(res)
                np_base64 = base64.b64encode(np_bytes)
                data_csv.data = np_base64
                data_csv.save()
                context = {
                    'search': res,
                    'data_obj_pk': data_csv.pk,
                }
            else:
                context = {}
            return render(request, 'progoffice/teacher_report.html', context)
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
                    # path = 'media/students'
                    # fileName = form.cleaned_data.get('face_img')
                    # img = cv2.imread(f'{path}/{fileName}')
                    # try:
                    #     # img = cv2.resize(img, (0, 0), None, 0.25, 0.25)
                    #     img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    #     faces = face_recognition.face_locations(img)
                    # except:
                    #     student.delete()
                    #     messages.error(request, "Error Processing the image!")
                    #     return render(request, 'progoffice/add_student.html', {'form': form})
                    # if len(faces) < 1:
                    #     student.delete()
                    #     messages.error(request, "No Face Detected, Please Upload a Clear Picture")
                    #     return render(request, 'progoffice/add_student.html', {'form': form})
                    # elif len(faces) > 1:
                    #     student.delete()
                    #     messages.error(request, "Multiple Faces Detected, Please Upload a Picture Containing only the Users Face")
                    #     return render(request, 'progoffice/add_student.html', {'form': form})
                    # else:
                    #     encodings = face_recognition.face_encodings(img, faces)[0]
                    #     print('Encodings Stored*********         : ', encodings)
                    #     np_bytes = pickle.dumps(encodings)
                    #     np_base64 = base64.b64encode(np_bytes)
                    #     student.face_encodings = np_base64
                    #     student.save()



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
                    # print('Year: ', now.year, ' Month: ', now.month, ' Day: ', now.day)

                    now = datetime.now()

                    curTime = now.time().replace(microsecond=0)
                    # print('Current Time: ', curTime)

                    
                    classTime = None
                    for timing in ClassTiming.objects.all():
                        if timing.start_time <= curTime <= timing.end_time:
                            classTime = timing
                    # print('classTime: ', classTime)
                    # print('Weekday: ', now.weekday())
                    currentClasses = Timetable.objects.filter(time=classTime, day=now.weekday())
                    print(currentClasses)
                    if classTime is None or now.weekday() > 6 or currentClasses.count() < 1:
                        bulkAttendance.delete()
                        messages.error(request, 'No class at this time')
                        return redirect('student_attendance')
                    alreadyTaken = BulkAttendance.objects.filter(Q(time__range=[f'{now.date()} {classTime.start_time}', f'{now.date()} {classTime.end_time}']))
                    if alreadyTaken.count() > 1:
                        bulkAttendance.delete()
                        messages.warning(request, 'Attendance for the current classes is already taken, please come again after the classes end!')
                        return redirect('student_attendance')

                    for crs in Course.objects.all():
                        if Timetable.objects.filter(course=crs, time=classTime, day=now.weekday()).count() > 1:
                            messages.error(request, f"Timetable is incorrect! {crs}'s class is scheduled in multiple classrooms.")
                            return redirect('student_attendance')
                    
                    if Student.objects.all().count() > 0:
                        counter = 0
                        for classroom in ClassRoom.objects.all()[:2]:
                            counter += 1
                            # print('Weekday',  now.weekday())
                            timeTable = Timetable.objects.filter(room=classroom, time=classTime, day=now.weekday())
                            # print('timeTable.count(): ', timeTable.count())
                            # print('Room: ', classroom.room_no)
                            if timeTable.count() > 1:
                                bulkAttendance.delete()
                                messages.error(request, f'Timetable is incorrect, multiple classes at this time in Room{classroom.room_no}')
                                return render(request, 'progoffice/student_attendance.html', {'form': BulkAttendanceForm()})
                            elif timeTable.count() != 1:
                                messages.error(request, f'No class at this time in Room{classroom.room_no}')
                                continue
                            course = timeTable[0].course
                            print('Room: ', counter, ' ---> Course: ', course)
                            if course is None:
                                messages.error(request, f'No course is registered at this time in Room{classroom.room_no}')
                                continue
                            
                            students_enrolled = course.student_set.all()
                            
                            if students_enrolled.count() < 1:
                                messages.warning(request, f'No students enrolled in {course}')
                                continue
                            path = 'media'
                            filename = getattr(bulkAttendance, f'room{classroom.room_no}_img')
                            try:
                                img = cv2.imread(f'{path}/{filename}')
                                # img = cv2.resize(img, None, fx=0.25, fy=0.25)
                                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                                faces = face_recognition.face_locations(img)
                            except:
                                bulkAttendance.delete()
                                messages.error(request, f'Error processing Classroom{classroom.room_no} image!')
                                return render(request, 'progoffice/teacher_face_attendance.html', {'form': form})
                            
                            if len(faces) < 1:
                                bulkAttendance.delete()
                                messages.warning(request, f'No Faces Detected in Classroom{classroom.room_no}!')
                                for student in students_enrolled:
                                    if StudentAttendance.objects.filter(student=student, time__year=now.year, time__month=now.month, time__day=now.day, course=course, class_timing=classTime).count() != 1:
                                        attendance = StudentAttendance(student=student, class_timing=classTime, time=now, course=course, status='A')
                                        attendance.save()
                            else:
                                encodings_test = face_recognition.face_encodings(img, faces)

                                encodings_known = []
                                pks = []

                                for student in students_enrolled:
                                    try:
                                        np_bytes = base64.b64decode(student.face_encodings)
                                    except:
                                        continue
                                    pks.append(student)
                                    encodings = pickle.loads(np_bytes)
                                    # print('Type of Encodings fetched: ', type(encodings))
                                    # print('Encodings Stored*********         : ', encodings)
                                    encodings_known.append(encodings)
                                    # print(encodings_known)
                                
                                presentCount = 0
                                for encoding in encodings_test:
                                    matches = face_recognition.compare_faces(encodings_known, encoding, tolerance=0.5)
                                    faceDis = face_recognition.face_distance(encodings_known, encoding)
                                    
                                    # print('Face Distance: ', faceDis)
                                    matchIndex = np.argmin(faceDis)

                                    if matches[matchIndex]:
                                        print('Face Distance: ', faceDis[matchIndex])
                                        presentCount += 1
                                        # print('Matched: ', pks[matchIndex])


                                        student = pks[matchIndex]
                                        print('Student Name: ' + student.student_name, ' ----> Matched: ', pks[matchIndex].student_name)
                                        
                                        alreadyMarked = StudentAttendance.objects.filter(student=student, class_timing=classTime, time__year=now.year, time__month=now.month, time__day=now.day, course=course)
                                        if alreadyMarked.count() == 1:
                                            marked = alreadyMarked[0]
                                            marked.status = 'P'
                                            # print('Before Time: ', marked.time)
                                            marked.time = now
                                            marked.save()
                                            # print('After Time: ', marked.time)
                                            continue
                                        elif alreadyMarked.count() > 1:
                                            for attendance in alreadyMarked:
                                                attendance.delete()

                                        attendance = StudentAttendance(student=student, class_timing=classTime, time=now, course=course, status='P')
                                        attendance.save()

                                for student in students_enrolled:
                                    alreadyMarked = StudentAttendance.objects.filter(student=student, class_timing=classTime, time__year=now.year, time__month=now.month, time__day=now.day, course=course)
                                    if alreadyMarked.count() < 1:
                                        attendance = StudentAttendance(student=student, time=now, class_timing=classTime, course=course, status='A')
                                        attendance.save()
                                    elif alreadyMarked.count() == 1:
                                        marked = alreadyMarked[0]
                                        if marked.status == 'A':
                                            # print('Before Time: ', marked.time)
                                            marked.time = now
                                            marked.save()
                                            # print('After Time: ', marked.time)
                            
                                if presentCount > 0:
                                    absentCount = students_enrolled.count() - presentCount
                                    messages.success(request, f'Attendance Marked Successfully in Room{classroom.room_no} | {presentCount} Present, {absentCount} Absent')
                                else:
                                    messages.warning(request, f'No faces matched in Room{classroom.room_no}')

                        return render(request, 'progoffice/student_attendance.html', {'form': BulkAttendanceForm()})
                              

                    else:
                        bulkAttendance.delete()
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
                    # print(type(course))
                    # print('REG_NO: ', reg_no)
                    # print('COURSE', course)
                    # print('DATE FROM: ', date_from)
                    # print('DATE TO: ', date_to)


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
                            res = StudentAttendance.objects.filter(student=student, course=course).filter(Q(time__year=start_date.year) and Q(time__month=start_date.month) and Q(time__day=start_date.day)).order_by('-time')
                        else:
                            try:
                                res = StudentAttendance.objects.filter(student=student, course=course).filter(Q(time__range=[date_from, f'{date_to} 23:59:59'])).order_by('-time')
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
                            res = StudentAttendance.objects.filter(student=student).filter(Q(time__year=start_date.year) and Q(time__month=start_date.month) and Q(time__day=start_date.day)).order_by('course', '-time')
                        else:
                            try:
                                res = StudentAttendance.objects.filter(student=student).filter(Q(time__range=[date_from, f'{date_to} 23:59:59'])).order_by('course', '-time')
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
                                res = StudentAttendance.objects.filter(Q(time__year=start_date.year) and Q(time__month=start_date.month) and Q(time__day=start_date.day)).order_by('student', 'course', '-time')
                            except:
                                res = None
                        else:
                            try:
                                res = StudentAttendance.objects.filter(Q(time__range=[date_from, f'{date_to} 23:59:59'])).order_by('student', 'course', '-time')
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
                                res = StudentAttendance.objects.filter(Q(time__year=start_date.year) and Q(time__month=start_date.month) and Q(time__day=start_date.day)).order_by('student', 'course', '-time')
                            except:
                                res = None
                        else:
                            try:
                                res = StudentAttendance.objects.filter(Q(time__range=[date_from, f'{today} 23:59:59'])).order_by('student', 'course', '-time')
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
                                res = StudentAttendance.objects.filter(student=student).filter(Q(time__year=start_date.year) and Q(time__month=start_date.month) and Q(time__day=start_date.day)).order_by('course', '-time')
                            except:
                                res = None
                        else:
                            try:
                                res = StudentAttendance.objects.filter(student=student).filter(Q(time__range=[date_from, f'{today} 23:59:59'])).order_by('course', '-time')
                            except:
                                res = None

                    elif reg_no and not course and not date_from and not date_to:
                        try:
                            student=Student.objects.get(reg_no=reg_no)
                            res = StudentAttendance.objects.filter(student=student).order_by('course', '-time')
                        except:
                            res = None
                    
                    elif not reg_no and course and not date_from and not date_to:
                        try:
                            res = StudentAttendance.objects.filter(course=course).order_by('student', '-time')
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
                                res = StudentAttendance.objects.filter(course=course).filter(Q(time__year=start_date.year) and Q(time__month=start_date.month) and Q(time__day=start_date.day)).order_by('student', '-time')
                            except:
                                res = None
                        else:
                            try:
                                res = StudentAttendance.objects.filter(course=course).filter(Q(time__range=[date_from, f'{today} 23:59:59'])).order_by('student', '-time')
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
                            res = StudentAttendance.objects.filter(course=course).filter(Q(time__year=start_date.year) and Q(time__month=start_date.month) and Q(time__day=start_date.day)).order_by('student', '-time')
                        else:
                            try:
                                res = StudentAttendance.objects.filter(course=course).filter(Q(time__range=[date_from, f'{date_to} 23:59:59'])).order_by('student', '-time')
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
                                res = StudentAttendance.objects.filter(student=student, course=course).filter(Q(time__year=start_date.year) and Q(time__month=start_date.month) and Q(time__day=start_date.day)).order_by('-time')
                            except:
                                res = None
                        else:
                            try:
                                res = StudentAttendance.objects.filter(student=student, course=course).filter(Q(time__range=[date_from, f'{today} 23:59:59'])).order_by('-time')
                            except:
                                res = None
                    
                    elif reg_no and course and not date_from and not date_to:
                        try:
                            student=Student.objects.get(reg_no=reg_no)
                            res = StudentAttendance.objects.filter(student=student, course=course).order_by('-time')
                        except:
                            res = None
                    
                    elif not reg_no and course and not date_from and not date_to:
                        try:
                            res = StudentAttendance.objects.filter(course=course).order_by('student', '-time')
                        except:
                            res = None

                    elif not reg_no and not course and not date_from and not date_to:
                        res = StudentAttendance.objects.all().order_by('student', '-time')
                        if res.count() < 1:
                            res = None
                    
                    elif not date_from and date_to:
                        messages.error(request, 'Invalid Date! Ensure date is not greater than today.  Please note that "Date to" must be greater than or equal to "Date From".')
                    
                    if res:
                        data_csv = DataCSV()
                        np_bytes = pickle.dumps(res)
                        np_base64 = base64.b64encode(np_bytes)
                        data_csv.data = np_base64
                        data_csv.save()
                        # print('PRIMARY KEY: ***************************', data_csv.pk)
                        # print('TYPE: ', type(data_csv.pk))
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

                context = {
                    'form': form,
                    'date_from': date_from,
                    'date_to': date_to,
                }
                return render(request, 'progoffice/student_report.html', context)
                
            else:
                res = StudentAttendance.objects.all().order_by('student', '-time')
                if res.count() > 1:
                    data_csv = DataCSV()
                    np_bytes = pickle.dumps(res)
                    np_base64 = base64.b64encode(np_bytes)
                    data_csv.data = np_base64
                    data_csv.save()
                context = {
                        'search': res,
                        'form': SearchStudentForm(),
                        'data_obj_pk': data_csv.pk,
                    }
                return render(request, 'progoffice/student_report.html', context)
        else:
            raise Http404()
    else:
        return redirect('index')


def generateTeacherCSV(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            pk = request.GET['pk']
            # print(pk)
            try:
                data_obj = DataCSV.objects.get(pk=pk)
                np_bytes = base64.b64decode(data_obj.data)
                query_set = pickle.loads(np_bytes)
            except:
                messages.warning(request, 'No data found!')
                return redirect('teacher_report_admin')
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=teacher_report.csv'

            # Create a CSV writer
            writer = csv.writer(response)

            writer.writerow(['Sr No', 'Teacher Name', 'Email', 'Check In', 'Check Out'])

            for count, obj in enumerate(query_set):
                writer.writerow([count+1, obj.teacher.teacher_name, obj.teacher.user.email, obj.checkin_time, obj.checkout_time])

            # print(query_set)

            return response
        else:
            raise Http404()
    else:
        return redirect('index')


def generateStudentCSV(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            pk = request.GET['pk']
            # print(pk)
            try:
                data_obj = DataCSV.objects.get(pk=pk)
                np_bytes = base64.b64decode(data_obj.data)
                query_set = pickle.loads(np_bytes)
            except:
                messages.warning(request, 'No data found!')
                return redirect('student_report')
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=student_report.csv'

            # Create a CSV writer
            writer = csv.writer(response)

            writer.writerow(['Sr No', 'Reg No', 'Name', 'Course', 'Date', 'Attendance'])

            for count, obj in enumerate(query_set):
                writer.writerow([count+1, obj.student.reg_no, obj.student.student_name, obj.course, obj.time, obj.status])

            # print(query_set)

            return response
        else:
            raise Http404()
    else:
        return redirect('index')


def courseReport(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            if request.method == 'POST':
                form = SearchCourseForm(request.POST)
                if form.is_valid():
                    course = form.cleaned_data['course']
                    
                    classDates = StudentAttendance.objects.filter(course=course).dates('time', kind='day', order='ASC')
            
                    classTimings = []
                    totalClasses = 0
                    for date in classDates:
                        pkTimings = StudentAttendance.objects.filter(course=course, time__year=date.year, time__month=date.month, time__day=date.day).values('class_timing').distinct()
                        classTimesDay = []
                        for pk in pkTimings:
                            try:
                                classTimesDay.append(ClassTiming.objects.get(pk=pk['class_timing']))
                            except:
                                pass
                        classTimings.append(classTimesDay)
                        totalClasses += len(classTimesDay)

                    attendanceSheet = []
                    attendancePercentage = []
                    studentsEnrolled = course.student_set.all().order_by('reg_no')
                    if classDates.count() > 0:
                        for student in studentsEnrolled:
                            presentCount = 0
                            studentAttendance = []
                            counter = 0
                            for date in classDates:
                                for timing in classTimings[counter]:
                                    try:
                                        data = StudentAttendance.objects.get(student=student, class_timing=timing, course=course)
                                    except:
                                        data = None
                                    # print('Data: ', data)
                                    if data is not None:
                                        studentAttendance.append(data.status)
                                        if data.status == 'P':
                                            presentCount += 1
                                    else:
                                        studentAttendance.append('A')
                                counter += 1
                            attendancePercentage.append(round(presentCount/totalClasses*100, 2))
                            attendanceSheet.append(studentAttendance)
                    
                    counter = 0
                    classes = []
                    for date in classDates:
                        for timing in classTimings[counter]:
                            classes.append(f'{date} | {timing}')
                        counter += 1

                    if len(attendanceSheet) > 0:
                        data_csv = DataCSV()
                        data = {
                            'course': course,
                            'class_times': classes,
                            'attendance_sheet': zip(attendanceSheet, studentsEnrolled, attendancePercentage)
                        }
                        np_bytes = pickle.dumps(data)
                        np_base64 = base64.b64encode(np_bytes)
                        data_csv.data = np_base64
                        data_csv.save()
                        context = {
                            'form': form,
                            'course': course,
                            'class_times': classes,
                            'attendance_sheet': zip(attendanceSheet, studentsEnrolled, attendancePercentage),
                            'data_obj_pk': data_csv.pk,
                        }
                    else:
                        data_csv = DataCSV()
                        data = {
                            'course': course,
                            'students_enrolled': studentsEnrolled,
                        }
                        np_bytes = pickle.dumps(data)
                        np_base64 = base64.b64encode(np_bytes)
                        data_csv.data = np_base64
                        data_csv.save()
                        context = {
                            'form': form,
                            'course': course,
                            'students_enrolled': studentsEnrolled,
                            'data_obj_pk': data_csv.pk,
                        }
                    return render(request, 'progoffice/course_report.html', context)

                else:
                    messages.error(request, 'Error fetching the form, please try again!!')
                    return redirect('course_report_admin')
            
            else:
                return render(request, 'progoffice/course_report.html', {'form': SearchCourseForm()})
        else:
            raise Http404()
    else:
        return redirect('index')


def generateCourseCSV(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            pk = request.GET['pk']
            # print(pk)
            try:
                data_obj = DataCSV.objects.get(pk=pk)
                np_bytes = base64.b64decode(data_obj.data)
                dict = pickle.loads(np_bytes)
            except:
                messages.warning(request, 'No data found!')
                return redirect('course_report')
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=course_report.csv'

            # Create a CSV writer
            writer = csv.writer(response)
            
            # try:
            course = dict['course']
            writer.writerow([course])
            if 'students_enrolled' in dict.keys():
                writer.writerow(['Sr No', 'Reg#', 'Student Name', 'Percentage'])
                studentsEnrolled = dict['students_enrolled']
                for count, student in enumerate(studentsEnrolled):
                    writer.writerow([count+1, student.reg_no, student.student_name])
            else:
                attendanceSheet = dict['attendance_sheet']
                classTimes = list(dict['class_times'])
                writer.writerow(['Sr No', 'Reg#', 'Student Name'] + classTimes + ['Percentage'])
                count = 0
                for attendance, student, percentage in attendanceSheet:
                    count += 1
                    writer.writerow([count, student.reg_no, student.student_name] + list(attendance) + [percentage])
                
            # except:
            #     pass

            return response
        else:
            raise Http404()
    else:
        return redirect('index')