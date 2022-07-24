# Generated by Django 4.0.2 on 2022-07-24 08:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('progoffice', '0017_alter_attendance_teacher_alter_teacher_user'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Course',
        ),
        migrations.RemoveField(
            model_name='enrollment',
            name='student',
        ),
        migrations.DeleteModel(
            name='Teacher_Course',
        ),
        migrations.RenameField(
            model_name='student',
            old_name='img1',
            new_name='face_img',
        ),
        migrations.RemoveField(
            model_name='student',
            name='email',
        ),
        migrations.RemoveField(
            model_name='student',
            name='img2',
        ),
        migrations.RemoveField(
            model_name='student',
            name='img3',
        ),
        migrations.DeleteModel(
            name='Enrollment',
        ),
    ]
