import base64
import csv
from datetime import datetime
import datetime as dt
import pickle
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from .forms import SearchStudentForm
from progoffice.models import Attendance, ClassTiming, Course, DataCSV, Student, StudentAttendance, Teacher
from django.contrib import messages
from django.db.models import Q
import calendar


def home(request):
    if request.user.is_authenticated and not request.user.is_superuser:
        # try:
        now = datetime.now()
        teacher = Teacher.objects.get(user=request.user)
        courses = Course.objects.filter(teacher=teacher)
        lastDay = calendar.monthrange(now.year, now.month)[1]
        startDate = dt.date(now.year, now.month, 1)
        firstDay = startDate.weekday()
        endDate = dt.date(now.year, now.month, lastDay)
        delta = dt.timedelta(days=1)
        monthAttendance = []
        while startDate <= endDate:
            day = startDate.weekday()
            if day > 4:
                monthAttendance.append('N')
            else:
                if startDate > now.date():
                    monthAttendance.append('N')
                else:
                    attendance = Attendance.objects.filter(checkin_time__year=now.year, checkin_time__month=now.month, checkin_time__day=startDate.day, teacher=teacher)
                    if attendance.count() > 1:
                        messages.warning(request, f'Attendance is not correct. Multiple attendance instances found on {startDate}')
                        monthAttendance = []
                        break
                    elif attendance.count() == 1:
                        monthAttendance.append('P')
                    else:
                        monthAttendance.append('A')
            startDate += delta
        print(monthAttendance)
        # except:
        #     teacher = None
        context = {
            'teacher': teacher,
            'courses': courses,
            'month': now.strftime("%B"),
            'year': now.year,
            'first_day': firstDay,
            'month_attendance': monthAttendance,
        }
        return render(request, 'teacher/index.html', context)
    elif request.user.is_authenticated and request.user.is_superuser:
        return redirect('index')
    else:
        return redirect('signin')


def teacherReport(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('index')
    elif request.user.is_authenticated and not request.user.is_superuser:
        if request.method == 'POST':
            date_from = request.POST['date_from']
            date_to = request.POST['date_to']

            res = None
            today = datetime.today().strftime('%Y-%m-%d')
            today_obj = datetime.strptime(today, '%Y-%m-%d')


            if date_from and date_to:
                start_date = datetime.strptime(date_from, "%Y-%m-%d")
                end_date = datetime.strptime(date_to, "%Y-%m-%d")
                try:
                    teacher=Teacher.objects.get(user=request.user)
                except:
                    pass
                if start_date > end_date or start_date > today_obj or end_date > today_obj:
                    messages.error(request, 'Invalid Date! Please note that "Date to" must be greater than or equal to "Date From".')
                    context = {
                        'search': res,
                        'date_from': date_from,
                        'date_to': date_to,
                    }
                    return render(request, 'teacher/teacher_report.html', context)
                
                elif start_date == end_date:
                    res = Attendance.objects.filter(teacher=teacher).filter(Q(checkin_time__year=start_date.year) and Q(checkin_time__month=start_date.month) and Q(checkin_time__day=start_date.day)).order_by('-checkin_time')
                else:
                    try:
                        res = Attendance.objects.filter(teacher=teacher).filter(Q(checkin_time__range=[date_from, f'{date_to} 23:59:59'])).order_by('-checkin_time')
                    except:
                        res = None

            elif date_from and not date_to:
                start_date = datetime.strptime(date_from, "%Y-%m-%d")
                try:
                    teacher=Teacher.objects.get(user=request.user)
                except:
                    pass
                if start_date > today_obj:
                    messages.error(request, 'Invalid Date! Ensure date is not greater than today. Please note that "Date to" must be greater than or equal to "Date From".')
                    context = {
                        'search': res,
                        'date_from': date_from,
                        'date_to': date_to,
                    }
                    return render(request, 'teacher/teacher_report.html', context)
                elif start_date == today_obj:
                    try:
                        res = Attendance.objects.filter(teacher=teacher).filter(Q(checkin_time__year=start_date.year) and Q(checkin_time__month=start_date.month) and Q(checkin_time__day=start_date.day)).order_by('-checkin_time')
                    except:
                        res = None
                else:
                    try:
                        res = Attendance.objects.filter(teacher=teacher).filter(Q(checkin_time__range=[date_from, f'{today} 23:59:59'])).order_by('-checkin_time')
                    except:
                        res = None

            elif not date_from and not date_to:
                try:
                    teacher=Teacher.objects.get(user=request.user)
                    res = Attendance.objects.filter(teacher=teacher).order_by('-checkin_time')
                except:
                    res = None
            
            elif not date_from and date_to:
                messages.error(request, 'Invalid Date! Ensure date is not greater than today.  Please note that "Date to" must be greater than or equal to "Date From".')
                return redirect('teacher_report')
            
            if res:
                data_csv = DataCSV()
                np_bytes = pickle.dumps(res)
                np_base64 = base64.b64encode(np_bytes)
                data_csv.data = np_base64
                data_csv.save()
                print('PRIMARY KEY: ***************************', data_csv.pk)
                print('TYPE: ', type(data_csv.pk))
                context = {
                    'search': res,
                    'date_from': date_from,
                    'date_to': date_to,
                    'data_obj_pk': data_csv.pk,
                }
            else:
                context = {
                    'search': res,
                    'date_from': date_from,
                    'date_to': date_to,
                }
            return render(request, 'teacher/teacher_report.html', context)
        else:
            return render(request, 'teacher/teacher_report.html')
    else:
        return redirect('index')


def generateTeacherCSV(request):
    if request.user.is_authenticated:
        pk = request.GET['pk']
        print(pk)
        try:
            data_obj = DataCSV.objects.get(pk=pk)
            np_bytes = base64.b64decode(data_obj.data)
            query_set = pickle.loads(np_bytes)
        except:
            messages.warning(request, 'No dat found!')
            return redirect('teacher_report')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=teacher_report.csv'

        # Create a CSV writer
        writer = csv.writer(response)

        writer.writerow(['Sr No', 'Teacher Name', 'Email', 'Check In', 'Check Out'])

        for count, obj in enumerate(query_set):
            writer.writerow([count+1, obj.teacher.teacher_name, obj.teacher.user.email, obj.checkin_time, obj.checkout_time])

        print(query_set)
        return response
    else:
        return redirect('index')


def studentReport(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('index')
    elif request.user.is_authenticated and not request.user.is_superuser:
        if request.method == 'POST':
            try:
                teacher = Teacher.objects.get(user=request.user)
                print(teacher)
            except:
                messages.error(request, 'Error fetching the form, Please try again!!!')
                return render(request, 'teacher/student_report.html', {'form': SearchStudentForm(request.POST or None, teacher)})
            
            form = SearchStudentForm(request.POST, teacher)
            date_from = request.POST['date_from']
            date_to = request.POST['date_to']
            if form.is_valid():
                reg_no = form.cleaned_data['reg_no']
                course = form.cleaned_data['course']
    
                res = None
                today = datetime.today().strftime('%Y-%m-%d')
                today_obj = datetime.strptime(today, '%Y-%m-%d')
                if reg_no and course and date_from and date_to:
                    start_date = datetime.strptime(date_from, "%Y-%m-%d")
                    end_date = datetime.strptime(date_to, "%Y-%m-%d")
                    try:
                        student = Student.objects.get(reg_no=reg_no)
                    except:
                        pass
                    if start_date > end_date or start_date > today_obj or end_date > today_obj:
                        messages.error(request, 'Invalid Date! Please note that "Date to" must be greater than or equal to "Date From".')
                        context = {
                            'search': res,
                            'form': form,
                            'date_from': date_from,
                            'date_to': date_to,
                        }
                        return render(request, 'teacher/student_report.html', context)
                    
                    elif start_date == end_date:
                        res = StudentAttendance.objects.filter(student=student, course=course).filter(Q(time__year=start_date.year) and Q(time__month=start_date.month) and Q(time__day=start_date.day)).order_by('-time')
                    else:
                        try:
                            res = StudentAttendance.objects.filter(student=student, course=course).filter(Q(time__range=[date_from, f'{date_to} 23:59:59'])).order_by('-time')
                        except:
                            res = None
                
                elif reg_no and not course and date_from and date_to:
                    # print('***********************************:LJ:LFHD*****************************************')
                    start_date = datetime.strptime(date_from, "%Y-%m-%d")
                    end_date = datetime.strptime(date_to, "%Y-%m-%d")
                    try:
                        student = Student.objects.get(reg_no=reg_no)
                        teacher = Teacher.objects.get(user=request.user)
                        courses = list(Course.objects.filter(teacher=teacher))
                    except:
                        pass
                    if start_date > end_date or start_date > today_obj or end_date > today_obj:
                        messages.error(request, 'Invalid Date! Please note that "Date to" must be greater than or equal to "Date From".')
                        context = {
                            'search': res,
                            'form': form,
                            'date_from': date_from,
                            'date_to': date_to,
                        }
                        return render(request, 'teacher/student_report.html', context)
                    
                    elif start_date == end_date:
                        res = StudentAttendance.objects.filter(course__in=courses, student=student).filter(Q(time__year=start_date.year) and Q(time__month=start_date.month) and Q(time__day=start_date.day)).order_by('course', '-time')
                    else:
                        try:
                            res = StudentAttendance.objects.filter(course__in=courses, student=student).filter(Q(time__range=[date_from, f'{date_to} 23:59:59'])).order_by('course', '-time')
                        except:
                            res = None

                elif not reg_no and not course and date_from and date_to:
                    start_date = datetime.strptime(date_from, "%Y-%m-%d")
                    end_date = datetime.strptime(date_to, "%Y-%m-%d")
                    try:
                        teacher = Teacher.objects.get(user=request.user)
                        courses = list(Course.objects.filter(teacher=teacher))
                    except:
                        pass
                    if start_date > end_date or start_date > today_obj or end_date > today_obj:
                        messages.error(request, 'Invalid Date! Please note that "Date to" must be greater than or equal to "Date From".')
                        context = {
                            'search': res,
                            'form': form,
                            'date_from': date_from,
                            'date_to': date_to,
                        }
                        return render(request, 'teacher/student_report.html', context)
                    
                    elif start_date == end_date:
                        try:
                            res = StudentAttendance.objects.filter(course__in=courses).filter(Q(time__year=start_date.year) and Q(time__month=start_date.month) and Q(time__day=start_date.day)).order_by('student', 'course', '-time')
                        except:
                            res = None
                    else:
                        try:
                            res = StudentAttendance.objects.filter(course__in=courses).filter(Q(time__range=[date_from, f'{date_to} 23:59:59'])).order_by('student', 'course', '-time')
                        except:
                            res = None
                
                elif not reg_no and not course and not date_to and date_from:
                    start_date = datetime.strptime(date_from, "%Y-%m-%d")
                    try:
                        teacher = Teacher.objects.get(user=request.user)
                        courses = list(Course.objects.filter(teacher=teacher))
                    except:
                        pass
                    if start_date > today_obj:
                        messages.error(request, 'Invalid Date! Ensure date is not greater than today. Please note that "Date to" must be greater than or equal to "Date From".')
                        context = {
                            'search': res,
                            'form': form,
                            'date_from': date_from,
                            'date_to': date_to,
                        }
                        return render(request, 'teacher/student_report.html', context)
                    elif start_date == today_obj:
                        try:
                            res = StudentAttendance.objects.filter(course__in=courses).filter(Q(time__year=start_date.year) and Q(time__month=start_date.month) and Q(time__day=start_date.day)).order_by('student', 'course', '-time')
                        except:
                            res = None
                    else:
                        try:
                            res = StudentAttendance.objects.filter(course__in=courses).filter(Q(time__range=[date_from, f'{today} 23:59:59'])).order_by('student', 'course', '-time')
                        except:
                            res = None

                elif reg_no and not course and date_from and not date_to:
                    start_date = datetime.strptime(date_from, "%Y-%m-%d")
                    try:
                        student=Student.objects.get(reg_no=reg_no)
                        teacher = Teacher.objects.get(user=request.user)
                        courses = list(Course.objects.filter(teacher=teacher))
                    except:
                        pass
                    if start_date > today_obj:
                        messages.error(request, 'Invalid Date! Ensure date is not greater than today.  Please note that "Date to" must be greater than or equal to "Date From".')
                        context = {
                            'search': res,
                            'form': form,
                            'date_from': date_from,
                            'date_to': date_to,
                        }
                        return render(request, 'teacher/student_report.html', context)
                    
                    elif start_date == today_obj:
                        try:
                            res = StudentAttendance.objects.filter(course__in=courses, student=student).filter(Q(time__year=start_date.year) and Q(time__month=start_date.month) and Q(time__day=start_date.day)).order_by('course', '-time')
                        except:
                            res = None
                    else:
                        try:
                            res = StudentAttendance.objects.filter(course__in=courses, student=student).filter(Q(time__range=[date_from, f'{today} 23:59:59'])).order_by('course', '-time')
                        except:
                            res = None

                elif reg_no and not course and not date_from and not date_to:
                    try:
                        student=Student.objects.get(reg_no=reg_no)
                        teacher = Teacher.objects.get(user=request.user)
                        courses = list(Course.objects.filter(teacher=teacher))
                        res = StudentAttendance.objects.filter(course__in=courses, student=student).order_by('course', '-time')
                    except:
                        res = None
                
                elif not reg_no and course and not date_from and not date_to:
                    try:
                        res = StudentAttendance.objects.filter(course=course).order_by('student', 'course', '-time')
                    except:
                        res = None
                
                elif not reg_no and course and date_from and not date_to:
                    start_date = datetime.strptime(date_from, "%Y-%m-%d")
                    if start_date > today_obj:
                        messages.error(request, 'Invalid Date! Ensure date is not greater than today.  Please note that "Date to" must be greater than or equal to "Date From".')
                        context = {
                            'search': res,
                            'form': form,
                            'date_from': date_from,
                            'date_to': date_to,
                        }
                        return render(request, 'teacher/student_report.html', context)
                    
                    elif start_date == today_obj:
                        try:
                            res = StudentAttendance.objects.filter(course=course).filter(Q(time__year=start_date.year) and Q(time__month=start_date.month) and Q(time__day=start_date.day)).order_by('student', '-time')
                        except:
                            res = None
                    else:
                        try:
                            res = StudentAttendance.objects.filter(course=course).filter(Q(time__range=[date_from, f'{today} 23:59:59'])).order_by('student', 'course', '-time')
                        except:
                            res = None
                
                elif not reg_no and course and date_from and date_to:
                    start_date = datetime.strptime(date_from, "%Y-%m-%d")
                    end_date = datetime.strptime(date_to, "%Y-%m-%d")
                    if start_date > end_date or start_date > today_obj or end_date > today_obj:
                        messages.error(request, 'Invalid Date! Please note that "Date to" must be greater than or equal to "Date From".')
                        context = {
                            'search': res,
                            'form': form,
                            'date_from': date_from,
                            'date_to': date_to,
                        }
                        return render(request, 'teacher/student_report.html', context)
                    
                    elif start_date == end_date:
                        res = StudentAttendance.objects.filter(course=course).filter(Q(time__year=start_date.year) and Q(time__month=start_date.month) and Q(time__day=start_date.day)).order_by('student', '-time')
                    else:
                        try:
                            res = StudentAttendance.objects.filter(course=course).filter(Q(time__range=[date_from, f'{date_to} 23:59:59'])).order_by('student', '-time')
                        except:
                            res = None
                
                elif reg_no and course and date_from and not date_to:
                    start_date = datetime.strptime(date_from, "%Y-%m-%d")
                    try:
                        student = Student.objects.get(reg_no=reg_no)
                    except:
                        pass
                    if start_date > today_obj:
                        messages.error(request, 'Invalid Date! Ensure date is not greater than today.  Please note that "Date to" must be greater than or equal to "Date From".')
                        context = {
                            'search': res,
                            'form': form,
                            'date_from': date_from,
                            'date_to': date_to,
                        }
                        return render(request, 'teacher/student_report.html', context)
                    
                    elif start_date == today_obj:
                        try:
                            res = StudentAttendance.objects.filter(student=student, course=course).filter(Q(time__year=start_date.year) and Q(time__month=start_date.month) and Q(time__day=start_date.day)).order_by('-time')
                        except:
                            res = None
                    else:
                        try:
                            res = StudentAttendance.objects.filter(student=student, course=course).filter(Q(time__range=[date_from, f'{today} 23:59:59'])).order_by('-time')
                        except:
                            res = None
                
                elif reg_no and course and not date_from and not date_to:
                    try:
                        student=Student.objects.get(reg_no=reg_no)
                        res = StudentAttendance.objects.filter(student=student, course=course).order_by('-time')
                    except:
                        res = None
                
                elif not reg_no and course and not date_from and not date_to:
                    try:
                        res = StudentAttendance.objects.filter(course=course).order_by('course', '-time')
                    except:
                        res = None
                
                elif not date_from and date_to:
                    messages.error(request, 'Invalid Date! Ensure date is not greater than today.  Please note that "Date to" must be greater than or equal to "Date From".')
                
                if res:
                    data_csv = DataCSV()
                    np_bytes = pickle.dumps(res)
                    np_base64 = base64.b64encode(np_bytes)
                    data_csv.data = np_base64
                    data_csv.save()
                    # print('PRIMARY KEY: ***************************', data_csv.pk)
                    # print('TYPE: ', type(data_csv.pk))
                    context = {
                        'search': res,
                        'form': form,
                        'date_from': date_from,
                        'date_to': date_to,
                        'data_obj_pk': data_csv.pk,
                    }
                else:
                    context = {
                        'search': res,
                        'form': form,
                        'date_from': date_from,
                        'date_to': date_to,
                    }
                return render(request, 'teacher/student_report.html', context)

            else:
                messages.error(request, 'Error fetching the form, please try again!!')
                return redirect('course_report')

        else:
            try:
                teacher = Teacher.objects.get(user=request.user)
                print(teacher)
            except:
                messages.error(request, 'Teacher object not found!!!')
            return render(request, 'teacher/student_report.html', {'form': SearchStudentForm(request.POST or None, teacher)})
    else:
        redirect('index')


def generateStudentCSV(request):
    if request.user.is_authenticated:
        pk = request.GET['pk']
        print(pk)
        try:
            data_obj = DataCSV.objects.get(pk=pk)
            np_bytes = base64.b64decode(data_obj.data)
            query_set = pickle.loads(np_bytes)
        except:
            messages.warning(request, 'No dat found!')
            return redirect('student_report')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=student_report.csv'

        # Create a CSV writer
        writer = csv.writer(response)

        writer.writerow(['Sr No', 'Reg No', 'Name', 'Course', 'Date', 'Attendance'])

        for count, obj in enumerate(query_set):
            writer.writerow([count+1, obj.student.reg_no, obj.student.student_name, obj.course, obj.time, obj.status ])

        print(query_set)
        return response
    else:
        return redirect('index')


def courseReport(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('index')
    elif request.user.is_authenticated and not request.user.is_superuser:
        if request.method == 'GET':
            pk = request.GET['pk']
            try:
                course = Course.objects.get(pk=pk)
            except:
                messages.error(request, 'Course not found, please try again!')
                return redirect('index')


            classDates = StudentAttendance.objects.filter(course=course).dates('time', kind='day', order='ASC')
            
            classTimings = []
            totalClasses = 0
            for date in classDates:
                pkTimings = StudentAttendance.objects.filter(course=course, time__year=date.year, time__month=date.month, time__day=date.day).values('class_timing').distinct()
                classTimesDay = []
                for pk in pkTimings:
                    classTimesDay.append(ClassTiming.objects.get(pk=pk['class_timing']))
                classTimings.append(classTimesDay)
                totalClasses += len(classTimesDay)
                    
            attendanceSheet = []
            attendancePercentage = []
            studentsEnrolled = course.student_set.all().order_by('reg_no')
            if classDates.count() > 0:
                for student in studentsEnrolled:
                    presentCount = 0
                    studentAttendance = []
                    counter = 0
                    for date in classDates:
                        for timing in classTimings[counter]:
                            try:
                                data = StudentAttendance.objects.get(student=student, course=course, time__year=date.year, time__month=date.month, time__day=date.day, class_timing=timing)
                            except:
                                data = None
                            
                            print('Data: ', data)
                            if data is not None:
                                studentAttendance.append(data.status)
                                if data.status == 'P':
                                    presentCount += 1
                            else:
                                studentAttendance.append('A')
                        counter += 1
                    attendancePercentage.append(round(presentCount/totalClasses*100, 2))
                    attendanceSheet.append(studentAttendance)
            
            counter = 0
            classes = []
            for date in classDates:
                for timing in classTimings[counter]:
                    classes.append(f'{date} | {timing}')
                counter += 1

            if len(attendanceSheet) > 0:
                data_csv = DataCSV()
                data = {
                    'course': course,
                    'class_times': classes,
                    'attendance_sheet': zip(attendanceSheet, studentsEnrolled, attendancePercentage)
                }
                np_bytes = pickle.dumps(data)
                np_base64 = base64.b64encode(np_bytes)
                data_csv.data = np_base64
                data_csv.save()
                context = {
                    'course': course,
                    'class_times': classes,
                    'attendance_sheet': zip(attendanceSheet, studentsEnrolled, attendancePercentage),
                    'data_obj_pk': data_csv.pk,
                }
            else:
                data_csv = DataCSV()
                data = {
                    'course': course,
                    'students_enrolled': studentsEnrolled,
                }
                np_bytes = pickle.dumps(data)
                np_base64 = base64.b64encode(np_bytes)
                data_csv.data = np_base64
                data_csv.save()
                context = {
                    'course': course,
                    'students_enrolled': studentsEnrolled,
                    'data_obj_pk': data_csv.pk,
                }
            
            return render(request, 'teacher/course_report.html', context)

        else:
            raise Http404('Page not found')
        
    else:
        return redirect('index')


def generateCourseCSV(request):
    if request.user.is_authenticated:
        if not request.user.is_superuser:
            pk = request.GET['pk']
            print(pk)
            try:
                data_obj = DataCSV.objects.get(pk=pk)
                np_bytes = base64.b64decode(data_obj.data)
                dict = pickle.loads(np_bytes)
            except:
                messages.warning(request, 'No data found!')
                return redirect('course_report')
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=course_report.csv'

            # Create a CSV writer
            writer = csv.writer(response)
            
            try:
                course = dict['course']
                writer.writerow([course])
                if 'students_enrolled' in dict.keys():
                    writer.writerow(['Sr No', 'Reg#', 'Student Name', 'Percentage'])
                    studentsEnrolled = dict['students_enrolled']
                    for count, student in enumerate(studentsEnrolled):
                        writer.writerow([count+1, student.reg_no, student.student_name])
                else:
                    attendanceSheet = dict['attendance_sheet']
                    classTimes = list(dict['class_times'])
                    writer.writerow(['Sr No', 'Reg#', 'Student Name'] + classTimes + ['Percentage'])
                    count = 0
                    for attendance, student, percentage in attendanceSheet:
                        count += 1
                        writer.writerow([count, student.reg_no, student.student_name] + list(attendance) + [percentage])
                
            except:
                messages.error(request, 'Error fetching data, please try again')
                return redirect('course_report')

            return response
        else:
            raise Http404()
    else:
        return redirect('index')