from django import forms

from progoffice.models import Teacher, Course, Timetable
from django.contrib.auth.models import User



class SearchStudentForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = ('course',)

    reg_no = forms.CharField(max_length=20)
    course = forms.ModelChoiceField(
        queryset=Course.objects.none(),
        label='Course',
        help_text='Please select a course.'
    )

    def __init__(self, *args, **kwargs):
        teacher = args[1] or None
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.fields['course'].queryset = Course.objects.filter(teacher=teacher)
        self.fields['reg_no'].required = False
        self.fields['course'].required = False


class SearchCourseForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = ('course',)

    reg_no = forms.CharField(max_length=20)
    course = forms.ModelChoiceField(
        queryset=Course.objects.none(),
        label='Course',
    )

    def __init__(self, *args, **kwargs):
        teacher = args[1] or None
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.fields['course'].queryset = Course.objects.filter(teacher=teacher)
        self.fields['reg_no'].required = False
        self.fields['course'].required = False


