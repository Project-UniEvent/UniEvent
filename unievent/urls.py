from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from unievent_event_app import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('admin/', admin.site.urls),

    # Event İşlemleri
    path('event/<int:event_id>/register/', views.register_to_event, name='register_event'),
    path('events/create/', views.create_event, name='create_event'),
    path('events/', views.my_events, name='my_events'),
    path('events/<int:event_id>/edit/', views.update_event, name='edit_event'),
    path('events/<int:event_id>/delete/', views.delete_event, name='delete_event'),

    # Announcement İşlemleri
    path('announcements/create/', views.create_announcement, name='create_announcement'),
    path('announcements/', views.my_announcements, name='my_announcements'),
    path('announcements/<int:announcement_id>/edit/', views.update_announcement, name='edit_announcement'),
    path('announcements/<int:announcement_id>/delete/', views.delete_announcement, name='delete_announcement'),

    # Profil Sayfası
    path('profile/', views.profile_view, name='profile'),

    # Authentication
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

]
