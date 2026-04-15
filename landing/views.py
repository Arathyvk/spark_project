from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.contrib import messages

from landing.models import User
from banner_admin.models import Banner
from course_admin.models import Course, Category
from free_content.models import FreeContent
from class_admin.models import LiveClass
from landing.models import  Enrollment
from review_admin.models import Review


def landing(request):
    banners        = Banner.objects.filter(is_active=True).order_by("sort_order")
    categories     = Category.objects.all()
    featured       = Course.objects.filter(status="active", is_featured=True).order_by("sort_order")[:4]
    latest_classes = LiveClass.objects.filter(is_published=True).select_related("course")[:4]
    free_videos_count = FreeContent.objects.filter(content_type="video", is_active=True).count()
    free_pdf_count    = FreeContent.objects.filter(content_type="pdf",   is_active=True).count()

    approved_reviews  = Review.objects.filter(status="approved").select_related("user", "course")[:4]
    review_stats      = Review.objects.filter(status="approved").aggregate(
        avg_rating=Avg("rating"),
        total=Count("id"),
    )

    context = {
        "banners":          banners,
        "categories":       categories,
        "featured_courses": featured,
        "latest_classes":   latest_classes,
        "free_videos":      free_videos_count,
        "free_pdfs":        free_pdf_count,
        "reviews":          approved_reviews,
        "avg_rating":       round(review_stats["avg_rating"] or 0, 1),
        "total_reviews":    review_stats["total"],
        "recommend_pct":    98,  
    }
    return render(request, "landing.html", context)



def courses(request):
    cat_slug = request.GET.get("category", "")
    qs = Course.objects.filter(status="active").select_related("category")
    if cat_slug:
        qs = qs.filter(category__slug=cat_slug)
    context = {
        "courses":    qs,
        "categories": Category.objects.all(),
        "active_cat": cat_slug,
    }
    return render(request, "courses.html", context)



def course_detail(request, slug):
    course  = get_object_or_404(Course, slug=slug, status="active")
    reviews = course.reviews.filter(status="approved").select_related("user")
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(
            user=request.user, course=course, order__status="paid"
        ).exists()
    context = {
        "course":      course,
        "reviews":     reviews,
        "is_enrolled": is_enrolled,
    }
    return render(request, "course_detail.html", context)



@login_required
def submit_review(request, course_id):
    if request.method != "POST":
        return redirect("landing")

    course = get_object_or_404(Course, pk=course_id, status="active")

    enrolled = Enrollment.objects.filter(
        user=request.user, course=course, order__status="paid"
    ).exists()
    if not enrolled:
        messages.error(request, "You must be enrolled to review this course.")
        return redirect("course_detail", slug=course.slug)

    if Review.objects.filter(user=request.user, course=course).exists():
        messages.info(request, "You have already submitted a review for this course.")
        return redirect("course_detail", slug=course.slug)

    rating  = int(request.POST.get("rating", 0))
    comment = request.POST.get("comment", "").strip()

    if not (1 <= rating <= 5) or not comment:
        messages.error(request, "Please provide a valid rating and comment.")
        return redirect("course_detail", slug=course.slug)

    Review.objects.create(
        user=request.user, course=course,
        rating=rating, comment=comment, status="pending"
    )
    messages.success(request, "Thank you! Your review is under moderation.")
    return redirect("course_detail", slug=course.slug)