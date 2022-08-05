from django.db.models.signals import post_delete, pre_save
from .models import Attendance, BulkAttendance, Teacher, Student
from django.dispatch import receiver

@receiver(post_delete, sender=Teacher)
def delete_images(sender, instance, **kwargs):
    try:
        instance.face_img.delete(save=False)
        instance.right_thumb_img.delete(save=False)
        instance.right_index_img.delete(save=False)
        instance.right_middle_img.delete(save=False)
        instance.right_ring_img.delete(save=False)
        instance.right_little_img.delete(save=False)
    except:
        pass

# @receiver(pre_save, sender=Teacher)
# def delete_images(sender,instance,*args,**kwargs):
#     try:
#         instance.face_img.delete(save=False)
#         instance.right_thumb_img.delete(save=False)
#         instance.right_index_img.delete(save=False)
#         instance.right_middle_img.delete(save=False)
#         instance.right_ring_img.delete(save=False)
#         instance.right_little_img.delete(save=False)
#     except:
#         pass


@receiver(post_delete, sender=Student)
def delete_images(sender, instance, **kwargs):
    try:
        instance.img1.delete(save=False)
        instance.img2.delete(save=False)
        instance.img3.delete(save=False)
    except:
        pass


@receiver(post_delete, sender=Attendance)
def delete_images(sender, instance, **kwargs):
    try:
        instance.checkin_img.delete(save=False)
        instance.checkout_img.delete(save=False)
    except:
        pass


@receiver(post_delete, sender=BulkAttendance)
def delete_images(sender, instance, **kwargs):
    try:
        instance.room1_img.delete(save=False)
        instance.room2_img.delete(save=False)
    except:
        pass