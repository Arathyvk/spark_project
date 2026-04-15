from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

from course_admin.models import Course

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", "admin")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("user", "User"),
        ("admin", "Admin"),
    )

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15, blank=True)
    district = models.CharField(max_length=100, blank=True)

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="user")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = UserManager()

    def __str__(self):
        return self.email


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
 