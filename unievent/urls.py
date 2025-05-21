from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from unievent_event_app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Home page
    path('', views.home_page, name='home'),

    # Admin page
    path('admin/', admin.site.urls),

    # Event Urls
    path('event/<int:event_id>/register/', views.register_to_event, name='register_event'),
    path('events/create/', views.create_event, name='create_event'),
    path('events/<int:event_id>/edit/', views.update_event, name='edit_event'),
    path('events/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('events/all/', views.all_events, name='all_events'),

    # Announcement Urls
    path('announcements/create/', views.create_announcement, name='create_announcement'),
    path('announcements/<int:announcement_id>/edit/', views.update_announcement, name='edit_announcement'),
    path('announcements/<int:announcement_id>/delete/', views.delete_announcement, name='delete_announcement'),
    path('announcements/all/', views.all_announcements, name='all_announcements'),

    # Club Urls
    path('clubs/all/', views.all_clubs, name='all_clubs'),
    path('clubs/follow/<int:club_id>/', views.follow_club, name='follow_club'),
    path('clubs/unfollow/<int:club_id>/', views.unfollow_club, name='unfollow_club'),
    path('clubs/<int:club_id>/', views.club_profile, name='club_profile'),

    # Profile Page
    path('profile/', views.profile_view, name='profile'),

    # Login & Logout
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/accounts/login/?logout=1'), name='logout'),

	path('search/', views.search_results, name='search_results'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
