from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class App(models.Model):
    SCREEN_CHANGED_CHOICES = [
        ('yes', _('Yes')),
        ('no', _('No')),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    apk_file_path = models.FileField(upload_to='apks/')
    first_screen_screenshot_path = models.ImageField(upload_to='screenshots/', null=True, blank=True)
    second_screen_screenshot_path = models.ImageField(upload_to='screenshots/', null=True, blank=True)
    video_recording_path = models.FileField(upload_to='videos/', null=True, blank=True)
    ui_hierarchy = models.TextField(null=True, blank=True)
    screen_changed = models.CharField(
        max_length=3,
        choices=SCREEN_CHANGED_CHOICES,
        default='no',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
