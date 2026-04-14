from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone



class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("role", "admin")
        return self.create_user(email, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [("user", "User"), ("admin", "Admin")]

    email      = models.EmailField(unique=True)
    full_name  = models.CharField(max_length=150)
    phone      = models.CharField(max_length=15, blank=True)
    district   = models.CharField(max_length=100, blank=True)
    role       = models.CharField(max_length=10, choices=ROLE_CHOICES, default="user")
    is_active  = models.BooleanField(default=True)
    is_staff   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_users',  
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_users_permissions', 
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["full_name"]
    objects = UserManager()

    def __str__(self):
        return self.email



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
    icon       = models.CharField(max_length=10, default="📚")   # emoji
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
 
 
 
class Banner(models.Model):
    title        = models.CharField(max_length=100)
    accent_word  = models.CharField(max_length=40, blank=True, help_text="Word highlighted in yellow")
    subtitle_ml  = models.TextField(blank=True, help_text="Malayalam subtitle line")
    cta_primary  = models.CharField(max_length=50, default="Get This Course")
    cta_secondary= models.CharField(max_length=50, default="Know More")
    course       = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    badge_price  = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    badge_original=models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    tags         = models.CharField(max_length=200, blank=True, help_text="Comma-separated e.g. Live Class,Free Content")
    is_active    = models.BooleanField(default=False)
    sort_order   = models.PositiveIntegerField(default=0)
    created_at   = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        ordering = ["sort_order"]
 
    def __str__(self):
        return self.title
 
    @property
    def badge_discount(self):
        if self.badge_original and self.badge_price and self.badge_original > self.badge_price:
            return int((1 - self.badge_price / self.badge_original) * 100)
        return None
 
    @property
    def tag_list(self):
        return [t.strip() for t in self.tags.split(",") if t.strip()]
 
 
 
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
 
 
 
class FreeContent(models.Model):
    TYPE_CHOICES = [("video", "Video"), ("pdf", "PDF")]
 
    course      = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name="free_content")
    title       = models.CharField(max_length=200)
    content_type= models.CharField(max_length=10, choices=TYPE_CHOICES)
    url         = models.URLField()
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        ordering = ["-created_at"]
 
    def __str__(self):
        return self.title
 
 
 
class Order(models.Model):
    STATUS_CHOICES = [("pending","Pending"),("paid","Paid"),("failed","Failed"),("refunded","Refunded")]
 
    user            = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    course          = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="orders")
    amount          = models.DecimalField(max_digits=8, decimal_places=2)
    status          = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    razorpay_order_id   = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    paid_at         = models.DateTimeField(null=True, blank=True)
 
    class Meta:
        ordering = ["-created_at"]
 
    def __str__(self):
        return f"{self.user.email} – {self.course.name} – {self.status}"
 
 
 
class Enrollment(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrollments")
    course     = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    order      = models.OneToOneField(Order, on_delete=models.CASCADE)
    enrolled_at= models.DateTimeField(auto_now_add=True)
    is_active  = models.BooleanField(default=True)
 
    class Meta:
        unique_together = ("user", "course")
 
    def __str__(self):
        return f"{self.user.email} enrolled in {self.course.name}"
 
  
class Review(models.Model):
    STATUS_CHOICES = [("pending","Pending"),("approved","Approved"),("rejected","Rejected")]
 
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    course      = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="reviews")
    rating      = models.PositiveSmallIntegerField()   # 1-5
    comment     = models.TextField()
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    helpful_count = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
 
    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user", "course")
 
    def __str__(self):
        return f"{self.user.full_name} – {self.course.name} – {self.rating}★"
 

