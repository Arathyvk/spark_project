from django.urls import path
from . import views

urlpatterns = [
  

    path("banners/",                    views.banner_list,    name="admin_banners"),
    path("banners/add/",                views.banner_add,     name="admin_banner_add"),
    path("banners/<int:pk>/edit/",      views.banner_edit,    name="admin_banner_edit"),
    path("banners/<int:pk>/delete/",    views.banner_delete,  name="admin_banner_delete"),
    path("banners/<int:pk>/toggle/",    views.banner_toggle,  name="admin_banner_toggle"),
    path("banners/reorder/",            views.banner_reorder, name="admin_banner_reorder"),

]