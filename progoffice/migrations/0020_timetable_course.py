# Generated by Django 4.0.2 on 2022-07-24 08:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('progoffice', '0019_course_student_courses_enrolled_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='timetable',
            name='course',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='progoffice.course'),
        ),
    ]
