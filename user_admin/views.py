from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import  Count, Sum, Q

from landing.models import User, Order,Enrollment
from course_admin.models import Course
from review_admin.models import Review

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect("admin_login")
        return view_func(request, *args, **kwargs)
    return _wrapped


@admin_required
def user_list(request):
    search = request.GET.get("q", "").strip()

    qs = (
        User.objects
        .filter(role="user")
        .annotate(
            enroll_count=Count(
                "enrollments", 
                filter=Q(enrollments__is_active=True)
            ),
            order_count=Count("orders"),
            paid_orders=Count(
                "orders",
                filter=Q(orders__status__in=["paid", "manual"])
            ),
        )
        .order_by("-created_at")
    )

    if search:
        qs = qs.filter(
            Q(email__icontains=search) |
            Q(full_name__icontains=search)
        )

    return render(request, "user_list.html", {
        "users": qs,
        "search": search,
        "total_users": User.objects.filter(role="user").count(),
        "total_enrolled": Enrollment.objects.filter(is_active=True).count(),
        "pending_reviews_count": Review.objects.filter(status="pending").count(),
    })


@admin_required
def user_detail(request, pk):
    user    = get_object_or_404(User, pk=pk, role="user")
    orders  = user.orders.select_related("course").order_by("-created_at")
    enrolls = user.enrollments.filter(is_active=True).select_related("course", "order")
    courses_not_enrolled = (
        Course.objects
        .filter(status="active")
        .exclude(enrollments__user=user, enrollments__is_active=True)
    )

    return render(request, "user_detail.html", {
        "usr":                   user,
        "orders":                orders,
        "enrollments":           enrolls,
        "courses_available":     courses_not_enrolled,
        "pending_reviews_count": Review.objects.filter(status="pending").count(),
    })


@admin_required
def grant_access(request, user_pk):
    user = get_object_or_404(User, pk=user_pk, role="user")
    if request.method == "POST":
        course_id = request.POST.get("course_id")
        note      = request.POST.get("note","").strip()
        course    = get_object_or_404(Course, pk=course_id)
        try:
            Enrollment.manual_grant(
                user=user, course=course,
                admin_user=request.user, note=note
            )
            messages.success(request, f"Access granted to '{course.name}' for {user.full_name}.")
        except ValueError as e:
            messages.error(request, str(e))
    return redirect("admin_user_detail", pk=user_pk)


@admin_required
def revoke_access(request, enrollment_pk):
    enrollment = get_object_or_404(Enrollment, pk=enrollment_pk)
    if request.method == "POST":
        user_pk = enrollment.user_id
        enrollment.is_active = False
        enrollment.save(update_fields=["is_active"])
        messages.info(request, f"Access to '{enrollment.course.name}' revoked.")
        return redirect("admin_user_detail", pk=user_pk)
    return redirect("admin_users")


@admin_required
def order_list(request):
    status_filter = request.GET.get("status","")
    qs = Order.objects.select_related("user","course").order_by("-created_at")
    if status_filter:
        qs = qs.filter(status=status_filter)

    return render(request, "order.html", {
        "orders":                qs,
        "status_filter":         status_filter,
        "status_choices":        Order.STATUS_CHOICES,
        "total_revenue":         qs.filter(status__in=["paid","manual"]).aggregate(s=Sum("amount"))["s"] or 0,
        "pending_reviews_count": Review.objects.filter(status="pending").count(),
    })


