from django.urls import path
from . import views

urlpatterns = [
    path("",                            views.review_list,   name="admin_reviews"),
    path("reviews/<int:pk>/",           views.review_detail, name="admin_review_detail"),
    path("reviews/<int:pk>/action/",    views.review_action, name="admin_review_action"),
]