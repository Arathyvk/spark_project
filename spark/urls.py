from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('landing.urls')),
    path('newadmin/', include('admin_side.urls')),
    path('course_admin/', include('course_admin.urls')),
    path('class_admin/', include('class_admin.urls')),
    path('free_content/', include('free_content.urls')),
    path('review_admin/', include('review_admin.urls')),
    path('banner_admin/', include('banner_admin.urls')),
    path('user_admin/', include('user_admin.urls')),
]
