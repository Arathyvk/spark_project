from django.urls import path
from . import views

urlpatterns = [
    path("",                          views.landing,       name="landing"),
    path("courses/",                  views.courses,       name="courses"),
    path("courses/<slug:slug>/",      views.course_detail, name="course_detail"),
    path("review/<int:course_id>/",   views.submit_review, name="submit_review"),
]