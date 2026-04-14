from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Avg, Count, Sum
from django.utils import timezone
from functools import wraps
 
from landing.models import (Course,FreeContent)
from admin_side.views import admin_required


@admin_required
def free_content_list(request):
    type_filter   = request.GET.get("type", "")
    active_filter = request.GET.get("active", "")
 
    qs = FreeContent.objects.select_related("course").order_by("sort_order", "-created_at")
    if type_filter in ("video", "pdf"):
        qs = qs.filter(content_type=type_filter)
    if active_filter == "1":
        qs = qs.filter(is_active=True)
    elif active_filter == "0":
        qs = qs.filter(is_active=False)
 
    return render(request, "free_content_list.html", {
        "items":         qs,
        "type_filter":   type_filter,
        "active_filter": active_filter,
        "video_count": FreeContent.objects.filter(content_type="video").count(),
        "pdf_count": FreeContent.objects.filter(content_type="pdf").count(),
    })
 
 
@admin_required
def free_content_add(request):
    courses = Course.objects.filter(status="active")
    errors  = {}
 
    if request.method == "POST":
        data   = request.POST
        errors = _validate_free_content(data)
 
        if not errors:
            item = FreeContent(
                title         = data["title"].strip(),
                description   = data.get("description", "").strip(),
                content_type  = data["content_type"],
                url           = data["url"].strip(),
                thumbnail_url = data.get("thumbnail_url", "").strip(),
                is_active     = "is_active" in data,
                sort_order    = int(data.get("sort_order") or 0),
            )
            if data.get("duration_min") and data["content_type"] == "video":
                item.duration_min = int(data["duration_min"])
            cid = data.get("course")
            if cid:
                item.course_id = cid
            item.save()
            messages.success(request, f"'{item.title}' added successfully.")
            return redirect("admin_free_content")
 
    return render(request, "free_content_form.html", {
        "item":    None,
        "courses": courses,
        "errors":  errors,
        "post":    request.POST,
    })
 
 
@admin_required
def free_content_edit(request, pk):
    item    = get_object_or_404(FreeContent, pk=pk)
    courses = Course.objects.filter(status="active")
    errors  = {}
 
    if request.method == "POST":
        data   = request.POST
        errors = _validate_free_content(data)
 
        if not errors:
            item.title         = data["title"].strip()
            item.description   = data.get("description", "").strip()
            item.content_type  = data["content_type"]
            item.url           = data["url"].strip()
            item.thumbnail_url = data.get("thumbnail_url", "").strip()
            item.is_active     = "is_active" in data
            item.sort_order    = int(data.get("sort_order") or 0)
            item.duration_min  = int(data["duration_min"]) if data.get("duration_min") and data["content_type"] == "video" else None
            cid = data.get("course")
            item.course_id = cid if cid else None
            item.save()
            messages.success(request, f"'{item.title}' updated.")
            return redirect("admin_free_content")
 
    return render(request, "free_content_form.html", {
        "item":    item,
        "courses": courses,
        "errors":  errors,
        "post":    request.POST if request.method == "POST" else None,
    })
 
 
@admin_required
def free_content_delete(request, pk):
    item = get_object_or_404(FreeContent, pk=pk)
    if request.method == "POST":
        title = item.title
        item.delete()
        messages.success(request, f"'{title}' deleted.")
    return redirect("admin_free_content")
 
 
@admin_required
def free_content_toggle(request, pk):
    """Quick active/inactive toggle from the list view."""
    item = get_object_or_404(FreeContent, pk=pk)
    item.is_active = not item.is_active
    item.save(update_fields=["is_active"])
    state = "activated" if item.is_active else "deactivated"
    messages.success(request, f"'{item.title}' {state}.")
    return redirect("admin_free_content")
 
 
def _validate_free_content(data):
    errors = {}
    if not data.get("title", "").strip():
        errors["title"] = "Title is required."
    if not data.get("content_type"):
        errors["content_type"] = "Select Video or PDF."
    if not data.get("url", "").strip():
        errors["url"] = "URL is required."
    if data.get("duration_min"):
        try:
            d = int(data["duration_min"])
            if d < 1:
                raise ValueError
        except (ValueError, TypeError):
            errors["duration_min"] = "Enter a valid duration in minutes."
    return errors