from django.http import HttpResponse
from django.shortcuts import redirect, render

# Create your views here.


def home(request):
    if request.user.is_authenticated:
        return render(request, 'progoffice/index.html')
    else:
        return redirect('/signin')