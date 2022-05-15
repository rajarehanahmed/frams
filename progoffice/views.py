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

from .models import Student, Teacher
from .forms import StudentForm, TeacherForm

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
                email = request.POST['email']
                username = request.POST['username']
                p = request.POST['pass']
                p1 = request.POST['pass1']
                if not User.objects.filter(username=username).exists(): # Checks if username doesn't already exists
                    if not User.objects.filter(email=email).exists(): # Checks if email doesn't already exists
                        if p == p1: # Checks if the passwords are same
                            # Creat a new User object
                            user = User.objects.create_user(username=username, email=email, password=p)
                            user.is_active = False
                            user.save()

                            teacher  = Teacher(user_id=user)
                            form = TeacherForm(request.POST, request.FILES, instance=teacher)
                            if form.is_valid():
                                form.save()
                                
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
                                messages.error(request, 'Please enter correct teacher data!')
                                return redirect('add_teacher')
                        else:
                            messages.error(request, 'Passwords does not match!')
                            return redirect('add_teacher')
                    else:
                        messages.error(request, 'Email already exists!')
                        return redirect('add_teacher')
                else:
                    messages.error(request, 'Username is taken! Please Try Another One.')
                    return redirect('add_teacher')
            else:
                form = TeacherForm()
                return render(request, 'progoffice/add_teacher.html', {'form': form})
        else:
            return HttpResponse('404 - Page Not Found')
    else:
        return redirect('index')


def addStudent(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            if request.method == 'POST':
                form = StudentForm(request.POST, request.FILES)
                # if not Student.objects.filter(reg_no=form.reg_no).exists():
                if form.is_valid():
                    if not Student.objects.filter(reg_no=form.cleaned_data('reg_no')).exists():
                        print('valid')
                        form.save()
                        messages.success(request, 'Student Registered Successfully')
                        return redirect('index')
                    else:
                        print('invalid')
                        messages.error(request, 'Reg# is already present')
                        return redirect('add_student')
                else:
                    print(form.errors.as_data())
                    return render(request, 'progoffice/add_student.html', {'form': form})
                    # messages.error(request, 'Errors in Form!')
                    # return redirect('add_student')
            
            else:    
                form = StudentForm()
                return render(request, 'progoffice/add_student.html', {'form': form})
        else:
            return HttpResponse('404 - Page Not Found')
    else:
        return redirect('index')