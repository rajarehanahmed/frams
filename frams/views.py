from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from . import settings
from . tokens import generate_token
from django.contrib import messages

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.core.mail import EmailMessage, send_mail

from progoffice.models import Teacher, PendingRegistration

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
        username = request.POST['username']
        p = request.POST['pass']
        user = authenticate(username=username, password=p)
        if user is not None:
            login(request, user)
            # messages.success(request, 'Successfully Logged in.')
            return redirect('index')
        else:
            # context = {'message': 'Please Confirm Your Email Address or Enter Correct Credentials'}
            # return render(request, 'authentication/signin.html', context)
            messages.error(request, 'Please Confirm Your Email Address or Enter Correct Credentials')
            return redirect('signin')
    return render(request, 'authentication/signin.html')


def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        name = request.POST['name']
        email = request.POST['email']
        designation = request.POST['desig']
        status = request.POST['status']
        p = request.POST['pass']
        p1 = request.POST['pass1']
        if not User.objects.filter(username=username).exists(): # Checks if username doesn't already exists
            if not User.objects.filter(email=email).exists(): # Checks if email doesn't already exists
                if p == p1: # Checks if the passwords are same
                    # Creat a new User object
                    user = User.objects.create_user(username=username, email=email, password=p)
                    user.is_active = False
                    user.save()

                    # Create a new Teacher object
                    teacher = Teacher(user_id=user, teacher_name=name, teacher_designation=designation, teacher_status=status)
                    teacher.save()

                    # Create a PendingRegistration object
                    pr = PendingRegistration(teacher_id=teacher)
                    pr.save()

                    # Welcome Email
                    # subject = "Welcome to FRAMS - Login!"
                    # message = "Hello " + email + "!! \n" + \
                    #     "Welcome to FRAMS!! \n We have sent you a confirmation email, please confirm your email address in order to activate your account. \n\n Thanking You\n Team FRAMS"
                    # from_email = settings.EMAIL_HOST_USER
                    # to_list = [email]
                    # send_mail(subject, message, from_email, to_list, fail_silently=True)

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

                    print(username, email, status, designation, p, p1)
                    messages.success(request, 'Account Created, Please Check Your Email Inbox to Verify your Email. Thank you!')
                    return render(request, 'authentication/signup_completed.html')
                else:
                    messages.error(request, 'Passwords does not match!')
                    return redirect('signup')
            else:
                messages.error(request, 'Email already exists!')
                return redirect('signup')
        else:
            messages.error(request, 'Username is taken! Please Try Another One.')
            return redirect('signup')
    else:
        return render(request, 'authentication/signup.html')


def signout(request):
    logout(request)
    return redirect('signin')


def activate(request, uidb64, token):
    print('Entered activate')
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
        return render(request, 'authentication/activation_failed.html')


def pendingRegistrations(request):
    if request.method == "POST":
        email = request.POST['email']
        teacher_user = User.objects.get(email__exact=email)
        teacher = Teacher.objects.get(user_id=teacher_user)
        context = {
            'teacher': teacher,
            'user': teacher_user
        }
        return render(request, 'authentication/complete_signup.html', context)
        
    pendingRegs = PendingRegistration.objects.all()
    return render(request, 'authentication/pending_registration.html', {'pendingRegs': pendingRegs})