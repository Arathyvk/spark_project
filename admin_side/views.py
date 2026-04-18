from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from django.contrib import messages
from functools import wraps
from django.contrib.auth import authenticate, login



from landing.models import User
from banner_admin.models import Banner
from course_admin.models import Course
from class_admin.models import LiveClass
from landing.models import Order, Enrollment
from review_admin.models import Review



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

        user = authenticate(request, username=email, password=password)        
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




