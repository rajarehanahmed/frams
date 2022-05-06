# Generated by Django 4.0.2 on 2022-05-04 12:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('progoffice', '0004_teacher_img2_teacher_img3'),
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('room_no', models.IntegerField(max_length=3, primary_key=True, serialize=False)),
            ],
        ),
        migrations.RenameField(
            model_name='enrollment',
            old_name='student_id',
            new_name='student',
        ),
        migrations.RemoveField(
            model_name='enrollment',
            name='course_id',
        ),
        migrations.RemoveField(
            model_name='enrollment',
            name='teacher_id',
        ),
        migrations.AlterField(
            model_name='teacher',
            name='img1',
            field=models.ImageField(default='', upload_to='teacher'),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='img2',
            field=models.ImageField(default='', upload_to='teacher'),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='img3',
            field=models.ImageField(default='', upload_to='teacher'),
        ),
        migrations.CreateModel(
            name='Timetable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='progoffice.room')),
            ],
        ),
        migrations.CreateModel(
            name='Teacher_attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('checkin_time', models.DateTimeField()),
                ('checkout_time', models.DateTimeField()),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='progoffice.teacher')),
            ],
        ),
        migrations.CreateModel(
            name='Student_Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='progoffice.student')),
            ],
        ),
    ]
