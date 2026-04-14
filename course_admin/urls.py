from django.urls import path
from . import views

urlpatterns = [
    path("",                         views.course_list,   name="admin_courses"),
    path("courses/add/",             views.course_add,    name="admin_course_add"),
    path("courses/<int:pk>/edit/",   views.course_edit,   name="admin_course_edit"),
    path("courses/<int:pk>/delete/", views.course_delete, name="admin_course_delete"),

   
]