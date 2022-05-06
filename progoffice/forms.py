from dataclasses import field
from tkinter import Widget
from django import forms
from django.forms import ModelForm
from .models import Teacher


class TeacherForm(ModelForm):
    class Meta:
        model = Teacher
        fields = ('teacher_name', 'teacher_designation', 'teacher_status', 'img1', 'img2', 'img3')
        # Widgets = {
        #     'teacher_name': forms.TextInput(attrs={'class': 'form-control', 'value': '{{ teacher.teacher_name }}', 'id': 'name'}),
        #     # 'teacher_designation': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
        #     # 'teacher_status': '',
        #     # 'img1': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
        # }