from dataclasses import field
import email
from operator import contains
import re
from tkinter import Widget
from django import forms
from numpy import number
from .models import Student, Teacher
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Username'}
    ))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Password'}
    ))
    
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = ""
        self.fields['password'].label = ""


class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean(self):
        cd = self.cleaned_data
        if User.objects.filter(username=cd.get('username')).exists():
            self.add_error('username', 'Username is taken!')
        if User.objects.filter(email=cd.get('email')).exists():
            self.add_error('email', 'Email already exists!')
        return cd



class TeacherForm(forms.ModelForm):
    # Teacher_Statuses = (
    #     ('V', 'visiting'),
    #     ('P', 'permanent'),
    # )
    # Teacher_Designations = (
    #     ('P', 'professor'),
    #     ('AP', 'asst. professor')
    # )
    # teacher_name = forms.CharField(widget=forms.TextInput(
    #     attrs={'class': 'form-control form-control-sm'}
    # ))
    # teacher_designation = forms.CharField(widget=forms.Select(
    #     attrs={'class': 'form-select form-control-sm'},
    #     choices=Teacher_Designations
    # ))
    # teacher_status = forms.CharField(widget=forms.Select(
    #     attrs={'class': 'form-select form-control-sm'},
    #     choices=Teacher_Statuses
    # ))
    
    
    class Meta:
        model = Teacher
        fields = ('teacher_name', 'teacher_designation', 'teacher_status', 'img1', 'img2', 'img3')

    def clean(self):
        cd = self.cleaned_data
        regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')

        name = cd.get('teacher_name')
        nameWithNoDigit = ''.join([i for i in name if not i.isdigit()])
        if any(char.isdigit() for char in name):
            self.add_error('teacher_name', 'Name contains digit(s)!')
        if not (regex.search(nameWithNoDigit) == None):
            self.add_error('teacher_name', 'Name contains special character(s)!')

        return cd


class PartialTeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ('teacher_name', 'teacher_designation', 'teacher_status')

    def clean(self):
        cd = self.cleaned_data
        regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')

        name = cd.get('teacher_name')
        nameWithNoDigit = ''.join([i for i in name if not i.isdigit()])
        if any(char.isdigit() for char in name):
            self.add_error('teacher_name', 'Name contains digit(s)!')
        if not (regex.search(nameWithNoDigit) == None):
            self.add_error('teacher_name', 'Name contains special character(s)!')

        return cd


class StudentForm(forms.ModelForm):
    # reg_no = forms.CharField(widget=forms.TextInput(
    #     attrs={'class': 'form-control form-control-sm'}
    #     ))
    # student_name = forms.CharField(widget=forms.TextInput(
    #     attrs={'class': 'form-control form-control-sm'}
    # ))
    # father_name = forms.CharField(widget=forms.TextInput(
    #     attrs={'class': 'form-control form-control-sm'}
    # ))
    # email = forms.EmailField(widget=forms.EmailInput(
    #     attrs={'class': 'form-control form-control-sm'}
    # ))
    class Meta:
        model = Student
        fields =  '__all__'

    def clean(self):
        cd = self.cleaned_data
        regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')

        reg_no = cd.get('reg_no')
        regWithNoDigit = ''.join([i for i in reg_no if not i.isdigit()])
        if Student.objects.filter(reg_no=reg_no).exists():
            self.add_error('reg_no', 'A Student with this Reg# already exists!')
        if not (regex.search(regWithNoDigit) == None):
            self.add_error('reg_no', 'Reg# contains special character(s)!')

        name = cd.get('student_name')
        nameWithNoDigit = ''.join([i for i in name if not i.isdigit()])
        if any(char.isdigit() for char in name):
            self.add_error('student_name', 'Student Name contains digit(s)!')
        if not (regex.search(nameWithNoDigit) == None):
            self.add_error('student_name', 'Student Name contains special character(s)!')

        father_name = cd.get('father_name')
        nameWithNoDigit = ''.join([i for i in father_name if not i.isdigit()])
        if any(char.isdigit() for char in father_name):
            self.add_error('father_name', 'Father Name contains digit(s)!')
        if not (regex.search(nameWithNoDigit) == None):
            self.add_error('father_name', 'Father Name contains special character(s)!')
        return cd