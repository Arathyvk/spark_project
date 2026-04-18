from django.urls import path
from . import views

urlpatterns = [
  
    path("users/",                         views.user_list,     name="admin_users"),
    path("users/<int:pk>/",                views.user_detail,   name="admin_user_detail"),
    path("users/<int:user_pk>/grant/",     views.grant_access,  name="admin_grant_access"),
    path("enrollments/<int:enrollment_pk>/revoke/", views.revoke_access, name="admin_revoke_access"),
    path("orders/",                        views.order_list,    name="admin_orders"),
]