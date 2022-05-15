from dataclasses import field
import email
from tkinter import Widget
from django import forms
from .models import Student, Teacher


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ('teacher_name', 'teacher_designation', 'teacher_status', 'img1', 'img2', 'img3')
        # Widgets = {
        #     'teacher_name': forms.TextInput(attrs={'class': 'form-control', 'value': '{{ teacher.teacher_name }}', 'id': 'name'}),
        #     # 'teacher_designation': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
        #     # 'teacher_status': '',
        #     # 'img1': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
        # }


class StudentForm(forms.ModelForm):
    reg_no = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control form-control-lg'}
        ))
    student_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control form-control-lg'}
    ))
    father_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control form-control-lg'}
    ))
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'class': 'form-control form-control-lg'}
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