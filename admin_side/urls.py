from django.urls import path
from . import views

urlpatterns = [
    path("",                           views.admin_login,  name="admin_login"),
    path("logout/",                    views.admin_logout, name="admin_logout"),
    path("dashboard/",                 views.dashboard,    name="admin_dashboard"),

    path("banners/",                      views.banner_list,   name="admin_banners"),
    path("banners/add/",                  views.banner_edit,   name="admin_banner_add"),
    path("banners/<int:pk>/edit/",        views.banner_edit,   name="admin_banner_edit"),
    path("banners/<int:pk>/toggle/",      views.banner_toggle, name="admin_banner_toggle"),


]