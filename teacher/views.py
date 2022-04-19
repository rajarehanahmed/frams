from django.http import HttpResponse
from django.shortcuts import render, redirect
from progoffice.models import Teacher

# Create your views here.


def home(request):
    if request.user.is_authenticated:
        return render(request, 'teacher/index.html')
    else:
        return redirect('/signin')


def profile(request):
    teacher = Teacher.objects.get(user_id=request.user)
    context = {
        'teacher_name':  teacher.teacher_name,
        'teacher_designation': teacher.teacher_designation,
        'teacher_status': teacher.teacher_status,
        'created_at': teacher.created_at
    }
    return render(request, 'teacher/profile.html', context)