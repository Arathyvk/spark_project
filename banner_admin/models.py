from django.db import models
from django.utils import timezone
from django.utils.text import slugify
 
 
 
class Banner(models.Model):
 
    title        = models.CharField(
        max_length=120,
        help_text="Main headline. Use | to split into two lines e.g. 'Mission|SCERT PSC 2025'."
    )
    accent_word  = models.CharField(
        max_length=40, blank=True,
        help_text="Word inside the title to highlight in yellow. Must match a word in title exactly."
    )
    subtitle_ml  = models.TextField(
        blank=True,
        verbose_name="Subtitle (Malayalam)",
        help_text="Displayed in Noto Serif Malayalam below the title."
    )
 
    image        = models.ImageField(
        upload_to="banners/",
        blank=True, null=True,
        help_text="Optional background image. If omitted, the dark blue gradient is used."
    )
 
    cta_primary   = models.CharField(max_length=60, default="Get This Course")
    cta_secondary = models.CharField(max_length=60, default="Know More", blank=True)
 
    course        = models.ForeignKey(
        "course_admin.Course",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="banners",
        help_text="CTA buttons link to this course's detail page."
    )
 
    badge_price    = models.DecimalField(
        max_digits=8, decimal_places=2,
        null=True, blank=True,
        help_text="Sale price shown on the red badge."
    )
    badge_original = models.DecimalField(
        max_digits=8, decimal_places=2,
        null=True, blank=True,
        help_text="Crossed-out original price on the badge."
    )
 
    tags           = models.CharField(
        max_length=200, blank=True,
        help_text="Comma-separated chip labels e.g. Live Class,Free Content,Mock Tests"
    )
 
    is_active      = models.BooleanField(
        default=False,
        help_text="Only active banners appear in the homepage carousel."
    )
    sort_order     = models.PositiveIntegerField(
        default=0,
        help_text="Lower number = shown first in the carousel."
    )
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)
 
    class Meta:
        ordering = ["sort_order", "-created_at"]
 
    def __str__(self):
        return self.title
 
 
    @property
    def badge_discount_pct(self):
        if self.badge_original and self.badge_price and self.badge_original > self.badge_price:
            return int((1 - self.badge_price / self.badge_original) * 100)
        return None
 
    @property
    def tag_list(self):
        return [t.strip() for t in self.tags.split(",") if t.strip()]
 
    @property
    def title_parts(self):
        parts = self.title.split("|", 1)
        return parts if len(parts) == 2 else ("", self.title)
 
