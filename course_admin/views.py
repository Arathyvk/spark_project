from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.text import slugify
 
from course_admin.models import  Category, Course
from admin_side.views import admin_required
 


@admin_required
def course_list(request):
    status_filter = request.GET.get("status", "")
    qs = Course.objects.select_related("category").order_by("sort_order", "-created_at")
    if status_filter:
        qs = qs.filter(status=status_filter)
 
    return render(request, "course_list.html", {
        "courses":        qs,
        "status_filter":  status_filter,
        "status_choices": Course.STATUS_CHOICES,
    })
 
 
@admin_required
def course_add(request):
    categories = Category.objects.all()
    errors     = {}
 
    if request.method == "POST":
        data   = request.POST
        errors = _validate_course(data)
 
        if not errors:
            course = Course(
                name          = data["name"].strip(),
                slug          = data.get("slug","").strip() or slugify(data["name"]),
                level         = data["level"],
                description   = data.get("description","").strip(),
                short_label   = data["short_label"].strip(),
                sub_label     = data["sub_label"].strip(),
                thumb_style   = data["thumb_style"],
                price         = data["price"],
                original_price= data.get("original_price") or None,
                tag_new       = "tag_new"    in data,
                tag_live      = "tag_live"   in data,
                tag_free      = "tag_free"   in data,
                is_featured   = "is_featured" in data,
                sort_order    = int(data.get("sort_order") or 0),
                status        = data["status"],
            )
            cat_id = data.get("category")
            if cat_id:
                course.category_id = cat_id
            course.save()
            messages.success(request, f"Course '{course.name}' created successfully.")
            return redirect("admin_courses")
 
    return render(request, "course_form.html", {
        "course":           None,
        "categories":       categories,
        "level_choices":    Category.LEVEL_CHOICES,
        "thumb_choices":    Course.THUMB_CHOICES,
        "status_choices":   Course.STATUS_CHOICES,
        "errors":           errors,
        "post":             request.POST,
    })
 
 
@admin_required
def course_edit(request, pk):
    course     = get_object_or_404(Course, pk=pk)
    categories = Category.objects.all()
    errors     = {}
 
    if request.method == "POST":
        data   = request.POST
        errors = _validate_course(data, existing=course)
 
        if not errors:
            course.name          = data["name"].strip()
            course.slug          = data.get("slug","").strip() or slugify(data["name"])
            course.level         = data["level"]
            course.description   = data.get("description","").strip()
            course.short_label   = data["short_label"].strip()
            course.sub_label     = data["sub_label"].strip()
            course.thumb_style   = data["thumb_style"]
            course.price         = data["price"]
            course.original_price= data.get("original_price") or None
            course.tag_new       = "tag_new"    in data
            course.tag_live      = "tag_live"   in data
            course.tag_free      = "tag_free"   in data
            course.is_featured   = "is_featured" in data
            course.sort_order    = int(data.get("sort_order") or 0)
            course.status        = data["status"]
            cat_id = data.get("category")
            course.category_id   = cat_id if cat_id else None
            course.save()
            messages.success(request, f"Course '{course.name}' updated.")
            return redirect("admin_courses")
 
    return render(request, "course_form.html", {
        "course":           course,
        "categories":       categories,
        "level_choices":    Course.LEVEL_CHOICES,
        "thumb_choices":    Course.THUMB_CHOICES,
        "status_choices":   Course.STATUS_CHOICES,
        "errors":           errors,
        "post":             request.POST if request.method == "POST" else None,
    })
 
 
@admin_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == "POST":
        name = course.name
        course.delete()
        messages.success(request, f"Course '{name}' deleted.")
    return redirect("admin_courses")
 
 
def _validate_course(data, existing=None):
    errors = {}
    if not data.get("name","").strip():
        errors["name"] = "Course name is required."
    if not data.get("short_label","").strip():
        errors["short_label"] = "Thumbnail label is required."
    if not data.get("sub_label","").strip():
        errors["sub_label"] = "Thumbnail sub-label is required."
    try:
        p = float(data.get("price",""))
        if p < 0:
            raise ValueError
    except (ValueError, TypeError):
        errors["price"] = "Enter a valid price (0 or more)."
    if data.get("original_price"):
        try:
            op = float(data["original_price"])
            if op < 0:
                raise ValueError
        except (ValueError, TypeError):
            errors["original_price"] = "Enter a valid original price."
    if not data.get("level"):
        errors["level"] = "Select a level."
    if not data.get("status"):
        errors["status"] = "Select a status."
    slug = data.get("slug","").strip() or slugify(data.get("name",""))
    qs = Course.objects.filter(slug=slug)
    if existing:
        qs = qs.exclude(pk=existing.pk)
    if qs.exists():
        errors["slug"] = f"Slug '{slug}' is already in use by another course."
    return errors