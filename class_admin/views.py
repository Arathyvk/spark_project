from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from django.contrib import messages
from django.utils.text import slugify
from functools import wraps
 
from landing.models import (Course, LiveClass,)
from admin_side.views import admin_required



@admin_required
def class_list(request):
    type_filter = request.GET.get("type", "")
    pub_filter  = request.GET.get("published", "")
    qs = LiveClass.objects.select_related("course").order_by("-scheduled_at")
 
    if type_filter:
        qs = qs.filter(class_type=type_filter)
    if pub_filter == "1":
        qs = qs.filter(is_published=True)
    elif pub_filter == "0":
        qs = qs.filter(is_published=False)
 
    return render(request, "class_list.html", {
        "classes":      qs,
        "type_filter":  type_filter,
        "pub_filter":   pub_filter,
        "type_choices": LiveClass.TYPE_CHOICES,
    })
 
 
@admin_required
def class_add(request):
    courses = Course.objects.filter(status="active")
    errors  = {}
 
    if request.method == "POST":
        data   = request.POST
        errors = _validate_class(data)
 
        if not errors:
            cls = LiveClass(
                subject      = data["subject"].strip(),
                title        = data["title"].strip(),
                thumb_label  = data["thumb_label"].strip(),
                thumb_style  = data["thumb_style"],
                class_type   = data["class_type"],
                scheduled_at = data["scheduled_at"],
                duration_min = int(data["duration_min"]) if data.get("duration_min") else None,
                video_url    = data.get("video_url","").strip(),
                is_published = "is_published" in data,
            )
            cid = data.get("course")
            if cid:
                cls.course_id = cid
            cls.save()
            messages.success(request, f"Class '{cls.title}' created.")
            return redirect("admin_classes")
 
    return render(request, "class_form.html", {
        "cls":           None,
        "courses":       courses,
        "type_choices":  LiveClass.TYPE_CHOICES,
        "thumb_choices": LiveClass.THUMB_CHOICES,
        "errors":        errors,
        "post":          request.POST,
    })
 
 
@admin_required
def class_edit(request, pk):
    cls     = get_object_or_404(LiveClass, pk=pk)
    courses = Course.objects.filter(status="active")
    errors  = {}
 
    if request.method == "POST":
        data   = request.POST
        errors = _validate_class(data)
 
        if not errors:
            cls.subject      = data["subject"].strip()
            cls.title        = data["title"].strip()
            cls.thumb_label  = data["thumb_label"].strip()
            cls.thumb_style  = data["thumb_style"]
            cls.class_type   = data["class_type"]
            cls.scheduled_at = data["scheduled_at"]
            cls.duration_min = int(data["duration_min"]) if data.get("duration_min") else None
            cls.video_url    = data.get("video_url","").strip()
            cls.is_published = "is_published" in data
            cid = data.get("course")
            cls.course_id    = cid if cid else None
            cls.save()
            messages.success(request, f"Class '{cls.title}' updated.")
            return redirect("admin_classes")
 
    return render(request, "class_form.html", {
        "cls":           cls,
        "courses":       courses,
        "type_choices":  LiveClass.TYPE_CHOICES,
        "thumb_choices": LiveClass.THUMB_CHOICES,
        "errors":        errors,
        "post":          request.POST if request.method == "POST" else None,
    })
 
 
@admin_required
def class_delete(request, pk):
    cls = get_object_or_404(LiveClass, pk=pk)
    if request.method == "POST":
        title = cls.title
        cls.delete()
        messages.success(request, f"Class '{title}' deleted.")
    return redirect("admin_classes")
 
 
def _validate_class(data):
    errors = {}
    if not data.get("subject","").strip():
        errors["subject"] = "Subject is required."
    if not data.get("title","").strip():
        errors["title"] = "Title is required."
    if not data.get("thumb_label","").strip():
        errors["thumb_label"] = "Thumbnail label is required (e.g. PSC, GK)."
    if not data.get("class_type"):
        errors["class_type"] = "Select a type (Live or Recorded)."
    if not data.get("scheduled_at"):
        errors["scheduled_at"] = "Date and time is required."
    if data.get("duration_min"):
        try:
            d = int(data["duration_min"])
            if d < 1:
                raise ValueError
        except (ValueError, TypeError):
            errors["duration_min"] = "Enter a valid duration in minutes (e.g. 60)."
    return errors
 
 