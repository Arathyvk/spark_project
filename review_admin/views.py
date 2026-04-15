from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Avg, Count, Sum
from django.utils import timezone
from functools import wraps
 
from review_admin.models import Review
from admin_side.views import admin_required

@admin_required
def review_list(request):
    status_filter = request.GET.get("status", "pending")
 
    qs = (
        Review.objects
        .filter(status=status_filter)
        .select_related("user", "course")
        .order_by("-created_at")
    )
 
    agg = Review.objects.aggregate(
        total_approved  = Count("id", filter=__import__('django.db.models', fromlist=['Q']).Q(status="approved")),
        total_pending   = Count("id", filter=__import__('django.db.models', fromlist=['Q']).Q(status="pending")),
        total_rejected  = Count("id", filter=__import__('django.db.models', fromlist=['Q']).Q(status="rejected")),
        total_flagged   = Count("id", filter=__import__('django.db.models', fromlist=['Q']).Q(status="flagged")),
        avg_rating      = Avg("rating", filter=__import__('django.db.models', fromlist=['Q']).Q(status="approved")),
    )
 
    return render(request, "review_list.html", {
        "reviews":        qs,
        "status_filter":  status_filter,
        "status_choices": Review.STATUS_CHOICES,
        "agg":            agg,
    })
 
 
@admin_required
def review_action(request, pk):
    review = get_object_or_404(Review, pk=pk)
    action = request.POST.get("action", "")
    note   = request.POST.get("admin_note", "").strip()
 
    if action == "approve":
        review.approve()
        messages.success(request, f"Review by {review.user.full_name} approved ✓")
 
    elif action == "reject":
        review.reject(note=note)
        messages.info(request, f"Review by {review.user.full_name} rejected.")
 
    elif action == "flag":
        review.flag(note=note)
        messages.warning(request, f"Review by {review.user.full_name} flagged for inspection.")
 
    elif action == "edit_helpful":
        try:
            new_count = int(request.POST.get("helpful_count", review.helpful_count))
            if new_count < 0:
                raise ValueError
            review.helpful_count = new_count
            review.save(update_fields=["helpful_count"])
            messages.success(request, f"Helpful count updated to {new_count}.")
        except (ValueError, TypeError):
            messages.error(request, "Invalid helpful count value.")
 
    return redirect(request.META.get("HTTP_REFERER") or "admin_reviews")
 
 
@admin_required
def review_detail(request, pk):
    review = get_object_or_404(Review, pk=pk)
    return render(request, "review_detail.html", {"review": review})
 