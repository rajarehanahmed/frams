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

from .models import PendingRegistration, Student, Teacher
from .forms import StudentForm, TeacherForm, UserForm

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
                # p1 = request.POST['pass1']
                user_form = UserForm(request.POST)

                if user_form.is_valid():
                    user_form.save()
                    user = User.objects.get(username=user_form.cleaned_data['username'])
                    user.is_active = False
                    
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

                else:
                    return render(request, 'progoffice/add_teacher.html', {'user_form': user_form, 'teacher_form': TeacherForm()})

            else:
                return render(request, 'progoffice/add_teacher.html', {'teacher_form': TeacherForm(), 'user_form': UserForm()})

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
                        context = {
                            't_user': User.objects.get(email__exact=email),
                            'form': form
                        }
                        return render(request, 'authentication/complete_signup.html', context)

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
                    return render(request, 'progoffice/add_student.html', {'form': form})
            
            else:
                form = StudentForm()
                return render(request, 'progoffice/add_student.html', {'form': form})
        
        else:
            return HttpResponse('404 - Page Not Found')
    
    else:
        return redirect('index')