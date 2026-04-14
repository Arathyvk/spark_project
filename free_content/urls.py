from django.urls import path
from . import views

urlpatterns = [
    path("",                                     views.free_content_list,   name="admin_free_content"),
    path("free-content/add/",                    views.free_content_add,    name="admin_free_content_add"),
    path("free-content/<int:pk>/edit/",          views.free_content_edit,   name="admin_free_content_edit"),
    path("free-content/<int:pk>/delete/",        views.free_content_delete, name="admin_free_content_delete"),
    path("free-content/<int:pk>/toggle/",        views.free_content_toggle, name="admin_free_content_toggle"),

]