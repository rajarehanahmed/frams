from dataclasses import field
import email
from tkinter import Widget
from django import forms
from .models import Student, Teacher
from django.contrib.auth.models import User


class UserForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control form-control-sm'}
    ))
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'class': 'form-control form-control-sm'}
    ))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control form-control-sm'}
    ))
    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def clean(self):
        cd = self.cleaned_data
        if User.objects.filter(username=cd.get('username')).exists():
            self.add_error('username', 'Username is taken!')
        if User.objects.filter(email=cd.get('email')).exists():
            self.add_error('email', 'Email already exists!')
        return cd


class TeacherForm(forms.ModelForm):
    Teacher_Statuses = (
        ('V', 'visiting'),
        ('P', 'permanent'),
    )
    Teacher_Designations = (
        ('P', 'professor'),
        ('AP', 'asst. professor')
    )
    teacher_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control form-control-sm'}
    ))
    teacher_designation = forms.CharField(widget=forms.Select(
        attrs={'class': 'form-select form-control-sm'},
        choices=Teacher_Designations
    ))
    teacher_status = forms.CharField(widget=forms.Select(
        attrs={'class': 'form-select form-control-sm'},
        choices=Teacher_Statuses
    ))
    
    
    class Meta:
        model = Teacher
        fields = ('teacher_name', 'teacher_designation', 'teacher_status', 'img1', 'img2', 'img3')
        # Widgets = {
        #     'teacher_name': forms.TextInput(attrs={'class': 'form-control', 'value': '{{ teacher.teacher_name }}', 'id': 'name'}),
        #     # 'teacher_designation': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
        #     # 'teacher_status': '',
        #     # 'img1': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
        # }


class PartialTeacherForm(forms.ModelForm):
    Teacher_Statuses = (
        ('V', 'visiting'),
        ('P', 'permanent'),
    )
    Teacher_Designations = (
        ('P', 'professor'),
        ('AP', 'asst. professor')
    )
    teacher_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control form-control-sm'}
    ))
    teacher_designation = forms.CharField(widget=forms.Select(
        attrs={'class': 'form-select form-control-sm'},
        choices=Teacher_Designations
    ))
    teacher_status = forms.CharField(widget=forms.Select(
        attrs={'class': 'form-select form-control-sm'},
        choices=Teacher_Statuses
    ))
    
    
    class Meta:
        model = Teacher
        fields = ('teacher_name', 'teacher_designation', 'teacher_status')


class StudentForm(forms.ModelForm):
    reg_no = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control form-control-sm'}
        ))
    student_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control form-control-sm'}
    ))
    father_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control form-control-sm'}
    ))
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'class': 'form-control form-control-sm'}
    ))
    # img1 = forms.ImageField(widget=forms.Media(
    #     attrs={'class': 'form-control form-control-lg'}
    # ))
    # img2 = forms.ImageField(widget=forms.ImageField(
    #     attrs={'class': 'form-control form-control-lg'}
    # ))
    # img3 = forms.ImageField(widget=forms.ImageField(
    #     attrs={'class': 'form-control form-control-lg'}
    # ))
    class Meta:
        model = Student
        fields =  '__all__'

    def clean(self):
        cd = self.cleaned_data
        if Student.objects.filter(reg_no=cd.get('reg_no')).exists():
            self.add_error('reg_no', 'Reg# is already present!')

        if not ' ' in cd.get('student_name'):
            print('Incomplete Name')
            self.add_error('student_name', 'Please Enter Full Student Name')
        return cd

    # def clean_reg_no(self, *args, **kwargs):
    #     reg_no = self.cleaned_data.get('reg_no')
    #     if Student.objects.filter(reg_no=reg_no).exists():
    #         raise forms.ValidationError('Reg# is already present!')
    #         print('clean_rog_no is already present')
    #     return reg_no