from django.db import models


class Category(models.Model):
    LEVEL_CHOICES = [
        ("10th",    "10th Level"),
        ("plus2",   "+2 Level"),
        ("degree",  "Degree Level"),
        ("special", "Special Topics"),
        ("tech",    "Technical"),
        ("other",   "Others"),
    ]
    name       = models.CharField(max_length=100)
    slug       = models.SlugField(unique=True)
    level      = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    icon       = models.CharField(max_length=10, default="📚")   
    sort_order = models.PositiveIntegerField(default=0)
 
    class Meta:
        ordering = ["sort_order"]
 
    def __str__(self):
        return self.name
 
    @property
    def course_count(self):
        return self.courses.filter(status="active").count()


class Course(models.Model):
    STATUS_CHOICES = [("active", "Active"), ("draft", "Draft"), ("archived", "Archived")]
    THUMB_CHOICES  = [
        ("thumb1", "Blue Dark"),
        ("thumb2", "Indigo"),
        ("thumb3", "Teal"),
        ("thumb4", "Pink"),
    ]
 
    category      = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="courses")
    name          = models.CharField(max_length=200)
    slug          = models.SlugField(unique=True)
    short_label   = models.CharField(max_length=10, help_text="Shown on thumbnail e.g. PSC")
    sub_label     = models.CharField(max_length=40, help_text="Under short_label e.g. Mission SCERT")
    description   = models.TextField(blank=True)
    price         = models.DecimalField(max_digits=8, decimal_places=2)
    original_price= models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    thumb_style   = models.CharField(max_length=10, choices=THUMB_CHOICES, default="thumb1")
    tag_new       = models.BooleanField(default=False)
    tag_live      = models.BooleanField(default=False)
    tag_free      = models.BooleanField(default=False)
    is_featured   = models.BooleanField(default=False)
    status        = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")
    sort_order    = models.PositiveIntegerField(default=0)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)
 
    class Meta:
        ordering = ["sort_order", "-created_at"]
 
    def __str__(self):
        return self.name
 
    @property
    def discount_percent(self):
        if self.original_price and self.original_price > self.price:
            return int((1 - self.price / self.original_price) * 100)
        return None
 
    @property
    def enrollment_count(self):
        return self.enrollments.filter(order__status="paid").count()
 