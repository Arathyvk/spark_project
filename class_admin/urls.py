from django.urls import path
from . import views

urlpatterns = [

    path("",              views.class_list,   name="admin_classes"),
    path("classes/add/",          views.class_add,   name="admin_class_add"),
    path("classes/<int:pk>/edit/",views.class_edit,   name="admin_class_edit"),

]