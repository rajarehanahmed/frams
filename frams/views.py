from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from . tokens import generate_token
from django.contrib import messages

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.core.mail import EmailMessage, send_mail
from frams import settings

from progoffice.models import Teacher, PendingRegistration
from progoffice.forms import LoginForm, UserForm, PartialTeacherForm

# Create your views here.


def index(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('progoffice/')
        else:
            return redirect('teacher/')
    else:
        return redirect('signin')


def signin(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Successfully Logged in.')
            return redirect('index')
        else:
            return render(request, 'authentication/signin.html', {'form': form})
    return render(request, 'authentication/signin.html', {'form': LoginForm()})


def signup(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)

        if user_form.is_valid():
            user = user_form.save()

            teacher  = Teacher(user=user)
            teacher_form = PartialTeacherForm(request.POST, instance=teacher)

            if teacher_form.is_valid():
                teacher_form.save()

                if teacher.teacher_status == 'V':
                    pr = PendingRegistration(teacher=teacher)
                    pr.save()

                    messages.success(request, 'Account Created, Please go to Admin for completing the Registration Process. Thank you!')
                else:
                    # Sending Confirmation Email
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
                        email.send()
                    except:
                        messages.error(request, "Sending verification email failed!")
                        return render(request, 'authentication/signup.html', {'user_form': user_form, 'teacher_form': teacher_form})
                    
                    messages.success(request, 'Account Created. Please verify your email by clicking on the verification link sent to you')
                return render(request, 'authentication/signup_completed.html')

            else:
                user.delete()
                return render(request, 'authentication/signup.html', {'user_form': user_form, 'teacher_form': teacher_form})

        else:
            print('user_form invalid')
            return render(request, 'authentication/signup.html', {'user_form': user_form, 'teacher_form': PartialTeacherForm(request.POST)})

    else:
        return render(request, 'authentication/signup.html', {'user_form': UserForm(), 'teacher_form': PartialTeacherForm()})


def signout(request):
    logout(request)
    return redirect('signin')


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
        print(myuser.email)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        messages.success(request, 'Email Verified!')
        return render(request, 'authentication/email_verified.html')
    else:
        messages.success(request, 'Activation Failed! Please try again')
        return render(request, 'authentication/activation_failed.html')
