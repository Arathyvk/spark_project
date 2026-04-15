from django.db import models
from django.utils import timezone
 
 
 
class FreeContent(models.Model):
    TYPE_CHOICES = [
        ("video", "Video"),
        ("pdf",   "PDF"),
    ]
 
    course       = models.ForeignKey(
        "course_admin.Course",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="free_content",
        help_text="Leave blank for standalone free content not tied to any course."
    )
 
    title        = models.CharField(max_length=200)
    description  = models.TextField(
        blank=True,
        help_text="Short description shown on the free content listing page."
    )
    content_type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        help_text="Video = YouTube/embed link.  PDF = direct file URL or Google Drive share link."
    )
    url          = models.URLField(
        max_length=500,
        help_text="YouTube link, embed URL, or direct PDF/Drive URL."
    )
    thumbnail_url = models.URLField(
        max_length=500, blank=True,
        help_text="Optional thumbnail image URL (YouTube thumbnail, cover image)."
    )
    duration_min = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="Duration (minutes)",
        help_text="For videos only — shown as '45m' or '1h 20m' on listing cards."
    )
    is_active    = models.BooleanField(
        default=True,
        help_text="Inactive items are hidden from users but kept in the database."
    )
    sort_order   = models.PositiveIntegerField(
        default=0,
        help_text="Lower = shown first in the listing."
    )
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)
 
    class Meta:
        ordering     = ["sort_order", "-created_at"]
        verbose_name = "free content item"
        verbose_name_plural = "free content items"
 
    def __str__(self):
        return f"[{self.get_content_type_display()}] {self.title}"
 
    @property
    def duration_display(self):
        if not self.duration_min:
            return ""
        h = self.duration_min // 60
        m = self.duration_min % 60
        if h and m:
            return f"{h}h {m}m"
        if h:
            return f"{h}h"
        return f"{m}m"
 
    @classmethod
    def video_count(cls):
        return cls.objects.filter(content_type="video", is_active=True).count()
 
    @classmethod
    def pdf_count(cls):
        return cls.objects.filter(content_type="pdf", is_active=True).count()
 