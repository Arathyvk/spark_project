from datetime import timezone

from django.db import models
from course_admin.models import Course


class LiveClass(models.Model):
    TYPE_CHOICES = [("live", "Live"), ("recorded", "Recorded")]
    THUMB_CHOICES = [("ct1","Blue"),("ct2","Indigo"),("ct3","Teal"),("ct4","Pink")]
 
    course       = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="classes", null=True, blank=True)
    subject      = models.CharField(max_length=100)
    title        = models.CharField(max_length=200)
    thumb_label  = models.CharField(max_length=10)
    thumb_style  = models.CharField(max_length=5, choices=THUMB_CHOICES, default="ct1")
    class_type   = models.CharField(max_length=10, choices=TYPE_CHOICES, default="recorded")
    scheduled_at = models.DateTimeField()
    duration_min = models.PositiveIntegerField(null=True, blank=True, help_text="Duration in minutes")
    video_url    = models.URLField(blank=True)
    is_published = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        ordering = ["-scheduled_at"]
 
    def __str__(self):
        return self.title
 
    @property
    def is_live_now(self):
        if self.class_type != "live":
            return False
        from datetime import timedelta
        now = timezone.now()
        return abs((now - self.scheduled_at).total_seconds()) <= 900 