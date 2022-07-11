from django.db.models.signals import post_delete
from .models import Teacher, Student, StudentAttendance
from django.dispatch import receiver

@receiver(post_delete, sender=Teacher)
def delete_images(sender, instance, **kwargs):
    try:
        instance.img1.delete(save=False)
        instance.img2.delete(save=False)
        instance.img3.delete(save=False)
    except:
        pass


@receiver(post_delete, sender=Student)
def delete_images(sender, instance, **kwargs):
    try:
        instance.img1.delete(save=False)
        instance.img2.delete(save=False)
        instance.img3.delete(save=False)
    except:
        pass