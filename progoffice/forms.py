from dataclasses import fields
import re
from django import forms
from .models import Attendance, BulkAttendance, Course, SearchStudent, Student, Teacher, Timetable
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# from validate_email_address import validate_email
# from pyisemail import is_email
from email_validator import validate_email, EmailNotValidError
# from validate_email import validate_email


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
        try:
            if User.objects.filter(username=cd.get('username')).exists():
                self.add_error('username', 'Username is taken!')
            if User.objects.filter(email=cd.get('email')).exists():
                self.add_error('email', 'Email already exists!')
        except:
            pass
        # try:
        #     mail = validate_email(cd.get('email')).email
        # except:
        #     self.add_error('email', 'Invalid email address!')
        return cd


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ('teacher_name', 'teacher_designation', 'teacher_status', 'face_img', 'right_thumb_img', 'right_index_img', 'right_middle_img', 'right_ring_img', 'right_little_img')

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
    
    def __init__(self, *args, **kwargs):
        super(TeacherForm, self).__init__(*args, **kwargs)
        self.fields['face_img'].required = False
        self.fields['right_thumb_img'].required = False
        self.fields['right_index_img'].required = False
        self.fields['right_middle_img'].required = False
        self.fields['right_ring_img'].required = False
        self.fields['right_little_img'].required = False


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


class TeacherAttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ('checkin_img',)
    
    def __init__(self, *args, **kwargs):
        super(TeacherAttendanceForm, self).__init__(*args, **kwargs)
        self.fields['checkin_img'].label = ""


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields =  ('reg_no', 'student_name', 'father_name', 'face_img', 'courses_enrolled')

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


# class StudentUptionForm(forms.ModelForm):
#     def clean(self):
#         cd = self.cleaned_data
#         img = cd.get('face_img')
#         cv2.imshow('IMG', img)
#         cv2.waitKey(0)
#         cv2.destroyAllWindows()


class BulkAttendanceForm(forms.ModelForm):
    class Meta:
        model = BulkAttendance
        fields = '__all__'


class SearchStudentForm(forms.ModelForm):
    class Meta:
        model = SearchStudent
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super(SearchStudentForm, self).__init__(*args, **kwargs)
        self.fields['reg_no'].required = False
        self.fields['course'].required = False


class SearchCourseForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = ('course',)

    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        label='Course',
    )