from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from django.http import JsonResponse
from django.contrib import messages
from functools import wraps

from landing.models import (User, Banner, Category, Course, LiveClass,FreeContent, Order, Enrollment, Review)



def admin_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect("admin_login")
        return view_func(request, *args, **kwargs)
    return _wrapped



def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("admin_dashboard")

    error = None
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, email=email, password=password)
        print(user)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect(request.GET.get("next", "admin_dashboard"))

        error = "Invalid credentials or insufficient permissions."

    return render(request, "admin_login.html", {"error": error})


def admin_logout(request):
    logout(request)
    return redirect("admin_login")



@admin_required
def dashboard(request):
    today = timezone.now().date()

    total_revenue  = Order.objects.filter(status="paid").aggregate(s=Sum("amount"))["s"] or 0
    total_enroll   = Enrollment.objects.filter(is_active=True).count()
    avg_rating     = Review.objects.filter(status="approved").aggregate(a=Avg("rating"))["a"] or 0
    pending_reviews= Review.objects.filter(status="pending").count()

    recent_courses = Course.objects.select_related("category").order_by("-created_at")[:5]
    recent_classes = LiveClass.objects.select_related("course").order_by("-created_at")[:5]
    pending_rev_list = Review.objects.filter(status="pending").select_related("user","course")[:5]
    banners        = Banner.objects.all().order_by("sort_order")[:5]

    context = {
        "total_revenue":   total_revenue,
        "total_enroll":    total_enroll,
        "avg_rating":      round(avg_rating, 1),
        "pending_reviews": pending_reviews,
        "recent_courses":  recent_courses,
        "recent_classes":  recent_classes,
        "pending_rev_list":pending_rev_list,
        "banners":         banners,
    }
    return render(request, "dashboard.html", context)




@admin_required
def banner_list(request):
    banners = Banner.objects.select_related("course").order_by("sort_order")
    return render(request, "banners.html", {"banners": banners})


@admin_required
def banner_toggle(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    banner.is_active = not banner.is_active
    banner.save()
    return redirect("admin_banners")


@admin_required
def banner_edit(request, pk=None):
    banner  = get_object_or_404(Banner, pk=pk) if pk else None
    courses = Course.objects.filter(status="active")

    if request.method == "POST":
        data = request.POST
        if not banner:
            banner = Banner()
        banner.title         = data.get("title","")
        banner.accent_word   = data.get("accent_word","")
        banner.subtitle_ml   = data.get("subtitle_ml","")
        banner.cta_primary   = data.get("cta_primary","Get This Course")
        banner.cta_secondary = data.get("cta_secondary","Know More")
        cid = data.get("course")
        banner.course_id     = cid if cid else None
        banner.badge_price   = data.get("badge_price") or None
        banner.badge_original= data.get("badge_original") or None
        banner.tags          = data.get("tags","")
        banner.is_active     = "is_active" in data
        banner.sort_order    = data.get("sort_order") or 0
        banner.save()
        messages.success(request, "Banner saved.")
        return redirect("admin_banners")

    return render(request, "banner_form.html", {"banner": banner, "courses": courses})


# ─── REVIEWS ─────────────────────────────────────────────────────────────────

@admin_required
def review_list(request):
    status_filter = request.GET.get("status","pending")
    reviews = Review.objects.filter(status=status_filter).select_related("user","course").order_by("-created_at")
    return render(request, "reviews.html", {"reviews": reviews, "status_filter": status_filter})


@admin_required
def review_action(request, pk):
    review = get_object_or_404(Review, pk=pk)
    action = request.POST.get("action")
    if action == "approve":
        review.status      = "approved"
        review.approved_at = timezone.now()
        review.save()
        messages.success(request, "Review approved.")
    elif action == "reject":
        review.status = "rejected"
        review.save()
        messages.info(request, "Review rejected.")
    return redirect(request.META.get("HTTP_REFERER", "admin_reviews"))


# ─── CLASSES ─────────────────────────────────────────────────────────────────

@admin_required
def class_list(request):
    classes = LiveClass.objects.select_related("course").order_by("-scheduled_at")
    return render(request, "spark_admin/classes.html", {"classes": classes})


@admin_required
def class_edit(request, pk=None):
    cls     = get_object_or_404(LiveClass, pk=pk) if pk else None
    courses = Course.objects.filter(status="active")

    if request.method == "POST":
        data = request.POST
        if not cls:
            cls = LiveClass()
        cid = data.get("course")
        cls.course_id    = cid if cid else None
        cls.subject      = data.get("subject","")
        cls.title        = data.get("title","")
        cls.thumb_label  = data.get("thumb_label","")
        cls.thumb_style  = data.get("thumb_style","ct1")
        cls.class_type   = data.get("class_type","recorded")
        cls.scheduled_at = data.get("scheduled_at")
        cls.duration_min = data.get("duration_min") or None
        cls.video_url    = data.get("video_url","")
        cls.is_published = "is_published" in data
        cls.save()
        messages.success(request, "Class saved.")
        return redirect("admin_classes")

    return render(request, "class_form.html", {"cls": cls, "courses": courses})


# ─── USERS ───────────────────────────────────────────────────────────────────

@admin_required
def user_list(request):
    users = User.objects.filter(role="user").annotate(
        enroll_count=Count("enrollments"),
        order_count=Count("orders"),
    ).order_by("-created_at")
    return render(request, "users.html", {"users": users})