from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from face_auth import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create-post/', views.create_post, name='create_post'),
    path('edit-post/<int:post_id>/', views.edit_post, name='edit_post'),
    path('delete-post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('api/capture-face/', views.capture_face_ajax, name='capture_face'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)