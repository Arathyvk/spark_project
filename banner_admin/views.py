from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from admin_side.views import admin_required
from django.http import JsonResponse

import json
from datetime import timedelta
from functools import wraps
 
 
from banner_admin.models import Banner
from course_admin.models import Course
from review_admin.models import Review
 


@admin_required
def banner_list(request):
    banners = Banner.objects.select_related("course").order_by("sort_order")
    return render(request, "banner_list.html", {
        "banners":               banners,
        "active_count":          banners.filter(is_active=True).count(),
        "pending_reviews_count": Review.objects.filter(status="pending").count(),
    })
 
 
@admin_required
def banner_add(request):
    courses = Course.objects.filter(status="active")
    errors  = {}
 
    if request.method == "POST":
        data   = request.POST
        files  = request.FILES
        errors = _validate_banner(data)
 
        if not errors:
            banner = Banner(
                title         = data["title"].strip(),
                accent_word   = data.get("accent_word","").strip(),
                subtitle_ml   = data.get("subtitle_ml","").strip(),
                cta_primary   = data.get("cta_primary","Get This Course").strip(),
                cta_secondary = data.get("cta_secondary","Know More").strip(),
                badge_price   = data.get("badge_price") or None,
                badge_original= data.get("badge_original") or None,
                tags          = data.get("tags","").strip(),
                is_active     = "is_active" in data,
                sort_order    = int(data.get("sort_order") or 0),
            )
            cid = data.get("course")
            if cid:
                banner.course_id = cid
            if "image" in files:
                banner.image = files["image"]
            banner.save()
            messages.success(request, f"Banner '{banner.title}' created.")
            return redirect("admin_banners")
 
    return render(request, "banner_form.html", {
        "banner":  None,
        "courses": courses,
        "errors":  errors,
        "post":    request.POST,
        "pending_reviews_count": Review.objects.filter(status="pending").count(),
    })
 
 
@admin_required
def banner_edit(request, pk):
    banner  = get_object_or_404(Banner, pk=pk)
    courses = Course.objects.filter(status="active")
    errors  = {}
 
    if request.method == "POST":
        data   = request.POST
        files  = request.FILES
        errors = _validate_banner(data)
 
        if not errors:
            banner.title         = data["title"].strip()
            banner.accent_word   = data.get("accent_word","").strip()
            banner.subtitle_ml   = data.get("subtitle_ml","").strip()
            banner.cta_primary   = data.get("cta_primary","Get This Course").strip()
            banner.cta_secondary = data.get("cta_secondary","Know More").strip()
            banner.badge_price   = data.get("badge_price") or None
            banner.badge_original= data.get("badge_original") or None
            banner.tags          = data.get("tags","").strip()
            banner.is_active     = "is_active" in data
            banner.sort_order    = int(data.get("sort_order") or 0)
            cid = data.get("course")
            banner.course_id = cid if cid else None
            if "image" in files:
                banner.image = files["image"]
            elif "image_clear" in data:
                banner.image = None
            banner.save()
            messages.success(request, f"Banner '{banner.title}' updated.")
            return redirect("admin_banners")
 
    return render(request, "banners_form.html", {
        "banner":  banner,
        "courses": courses,
        "errors":  errors,
        "post":    request.POST if request.method == "POST" else None,
        "pending_reviews_count": Review.objects.filter(status="pending").count(),
    })
 
 
@admin_required
def banner_delete(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    if request.method == "POST":
        title = banner.title
        banner.delete()
        messages.success(request, f"Banner '{title}' deleted.")
    return redirect("admin_banners")
 
 
@admin_required
def banner_toggle(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    banner.is_active = not banner.is_active
    banner.save(update_fields=["is_active"])
    messages.success(request, f"Banner '{ banner.title }' {'activated' if banner.is_active else 'deactivated'}.")
    return redirect("admin_banners")
 
 
@admin_required
def banner_reorder(request):
   
    if request.method == "POST":
        try:
            items = json.loads(request.body)
            for item in items:
                Banner.objects.filter(pk=item["id"]).update(sort_order=item["sort_order"])
            return JsonResponse({"ok": True})
        except Exception as e:
            return JsonResponse({"ok": False, "error": str(e)}, status=400)
    return redirect("admin_banners")
 
 
def _validate_banner(data):
    errors = {}
    if not data.get("title","").strip():
        errors["title"] = "Title is required."
    if data.get("badge_price"):
        try:
            float(data["badge_price"])
        except ValueError:
            errors["badge_price"] = "Enter a valid price."
    if data.get("badge_original"):
        try:
            float(data["badge_original"])
        except ValueError:
            errors["badge_original"] = "Enter a valid price."
    return errors