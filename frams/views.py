from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed, HttpResponseServerError
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
from progoffice.forms import TeacherForm, UserForm, PartialTeacherForm

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
            messages.success(request, 'Successfully Logged in.')
            return redirect('index')
        else:
            messages.error(request, 'Please Confirm Your Email Address or Enter Correct Credentials')
            return redirect('signin')
    return render(request, 'authentication/signin.html')


def signup(request):
    if request.method == 'POST':
        p1 = request.POST['pass1']

        user_form = UserForm(request.POST)
        if user_form.is_valid():
            if user_form.cleaned_data['password'] == p1:
                user_form.save()

                try:
                    user = User.objects.get(username=user_form.cleaned_data['username'])
                except(User.DoesNotExist):
                    messages.error(request, 'Error creating user: User Object does not exist!')
                    return redirect('signup')
                else:
                    try:
                        teacher  = Teacher(user_id=user)
                    except(Teacher.DoesNotExist):
                        messages.error(request, 'Error creating user: Teacher Object dost not exist')
                        return redirect('signup')
                    else:
                        teacher_form = PartialTeacherForm(request.POST, instance=teacher)

                        if teacher_form.is_valid():
                            teacher_form.save()

                            pr = PendingRegistration(teacher_id=teacher)
                            pr.save()

                            messages.success(request, 'Account Created, Please go to Admin for completing the Registration Process. Thank you!')
                            return render(request, 'authentication/signup_completed.html')

                        else:
                            print('teacher_form invalid')
                            user.delete()
                            return render(request, 'authentication/signup.html', {'user_form': user_form, 'teacher_form': teacher_form})

            else:
                print('Passwords Mismatch')
                messages.error(request, 'Passwords do not match')
                return render(request, 'authentication/signup.html', {'user_form': user_form, 'teacher_form': PartialTeacherForm()})

        else:
            print('user_form invalid')
            return render(request, 'authentication/signup.html', {'user_form': user_form, 'teacher_form': PartialTeacherForm()})

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
        return render(request, 'authentication/activation_failed.html')


# def pendingRegistrations(request):
#     if request.user.is_authenticated:
#         if request.user.is_superuser:
#             if request.method == "POST":
#                 email = request.POST['email']
#                 teacher_user = User.objects.get(email__exact=email)
#                 teacher = Teacher.objects.get(user_id=teacher_user)
#                 form = TeacherForm(instance=teacher)
#                 context = {
#                     'teacher': teacher,
#                     't_user': teacher_user,
#                     'form': form
#                 }
#                 return render(request, 'authentication/complete_signup.html', context)
            
#             pendingRegs = PendingRegistration.objects.all()
#             return render(request, 'authentication/pending_registration.html', {'pendingRegs': pendingRegs})
#         else:
#             return HttpResponse('404 - Page Not Found')
#     else:
#         return redirect('index')


# def deletePendingReg(request):
#     if request.user.is_authenticated:
#         if request.user.is_superuser and request.method == 'POST':
#             email = request.POST['email']
#             try:
#                 user = User.objects.get(email=email)
#             except(User.DoesNotExist):
#                 messages.error(request, 'User does not exist!')
#                 return redirect('pending_registrations')
#             else:
#                 user.delete()
#                 messages.success(request, 'Registration Deleted Successfully')
#                 return redirect('pending_registrations')
#         else:
#             return HttpResponse('404 - Page Not Found')
#     else:
#         return redirect('index')

# def completeSignup(request):
#     if request.user.is_authenticated:
#         if request.user.is_superuser and request.method == 'POST':
#             email = request.POST['email']
#             try: 
#                 user = User.objects.get(email=email)
#             except(User.DoesNotExist):
#                 messages.error(request, 'Email does not exist')
#                 return redirect('pending_registrations')
#             else:
#                 teacher = Teacher.objects.get(user_id=user)
#                 form = TeacherForm(request.POST, request.FILES, instance=teacher)
#                 if form.is_valid():
#                     form.save()
#                     try:
#                         pendingReg = PendingRegistration.objects.get(teacher_id=teacher)
#                     except(PendingRegistration.DoesNotExist):
#                         messages.warning(request, 'Pending Registration is not present!')
#                     else:
#                         pendingReg.delete()
#                     # Email Address Confirmation Email
#                     current_site = get_current_site(request)
#                     email_subject = "Confirm your email @ FRAMS - Login!!"
#                     message2 = render_to_string("authentication/email_confirmation.html", {
#                         'email': user.email,
#                         'domain': current_site.domain,
#                         'uid': force_str(urlsafe_base64_encode(force_bytes(user.pk))),
#                         'token': generate_token.make_token(user)
#                     })
#                     email = EmailMessage(email_subject, message2, settings.EMAIL_HOST_USER, [user.email])
#                     email.fail_silently = True
#                     email.send()

#                     messages.success(request, 'Registration Completed Successfully, Please Ask the Teacher to Verify their Email. Thank you!')
#                     return redirect('pending_registrations')
#                 else:
#                     messages.error(request, 'Errors in form data')
#                     return redirect('pending_registrations')
#         else:
#             return HttpResponse('404 - Page Not Found')
#     else:
#         return redirect('index')



