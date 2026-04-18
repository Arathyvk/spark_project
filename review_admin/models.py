from django.db import models
from django.utils import timezone
from django.db.models import Avg
from course_admin.models import Course

class Review(models.Model):
    STATUS_CHOICES = [
        ("pending",  "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("flagged",  "Flagged"),   
    ]
 
    user    = models.ForeignKey(
        "landing.User",
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    course  = models.ForeignKey(Course,on_delete=models.CASCADE,related_name="reviews")
 
    rating        = models.PositiveSmallIntegerField(
        help_text="Integer 1–5."
    )
    comment       = models.TextField()
 
    status        = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending",
        db_index=True,
        help_text="Only 'approved' reviews are shown publicly."
    )
    admin_note    = models.TextField(
        blank=True,
        help_text="Internal note visible only to admins (reason for rejection/flag etc.)."
    )
 
    helpful_count = models.PositiveIntegerField(
        default=0,
        help_text="Admin can edit this; users can increment it."
    )
 
    created_at    = models.DateTimeField(auto_now_add=True)
    approved_at   = models.DateTimeField(
        null=True, blank=True,
        help_text="Set automatically when status changes to 'approved'."
    )
    moderated_at  = models.DateTimeField(
        null=True, blank=True,
        help_text="Set automatically on any moderation action."
    )
 
    class Meta:
        ordering        = ["-created_at"]
        unique_together = ("user", "course")   
        verbose_name    = "review"
        verbose_name_plural = "reviews"
 
    def __str__(self):
        return f"{self.user.full_name} – {self.course.name} – {self.rating}★ [{self.status}]"
 
 
    def approve(self):
        now = timezone.now()
        self.status       = "approved"
        self.approved_at  = now
        self.moderated_at = now
        self.save(update_fields=["status", "approved_at", "moderated_at"])
 
    def reject(self, note=""):
        now = timezone.now()
        self.status       = "rejected"
        self.moderated_at = now
        if note:
            self.admin_note = note
        self.save(update_fields=["status", "moderated_at", "admin_note"])
 
    def flag(self, note=""):
        now = timezone.now()
        self.status       = "flagged"
        self.moderated_at = now
        if note:
            self.admin_note = note
        self.save(update_fields=["status", "moderated_at", "admin_note"])
 
 
    @classmethod
    def aggregate_stats(cls):
       
        qs    = cls.objects.filter(status="approved")
        agg   = qs.aggregate(avg=Avg("rating"), total=Count("id"))
        total = agg["total"] or 0
        avg   = round(agg["avg"] or 0, 1)
        rec   = qs.filter(rating__gte=4).count()
        pct   = int(rec / total * 100) if total else 0
        return {"avg_rating": avg, "total": total, "recommend_pct": pct}
 