"""
URL configuration for unievent project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.contrib import admin
from unievent_event_app import views

urlpatterns = [
    # Home page
    path('', views.home_page, name='home'),

	# Admin page
	path('admin/', admin.site.urls),

    # Event registration (for Students)
    path('event/<int:event_id>/register/', views.register_to_event, name='register_event'),

    # Event CRUD (for School Clubs and Departments)
    path('events/create/', views.create_event, name='create_event'),
    path('events/', views.my_events, name='my_events'),
    path('events/<int:event_id>/edit/', views.update_event, name='edit_event'),
    path('events/<int:event_id>/delete/', views.delete_event, name='delete_event'),

    # Announcement CRUD (for School Clubs and Departments)
    path('announcements/create/', views.create_announcement, name='create_announcement'),
    path('announcements/', views.my_announcements, name='my_announcements'),
    path('announcements/<int:announcement_id>/edit/', views.update_announcement, name='edit_announcement'),
    path('announcements/<int:announcement_id>/delete/', views.delete_announcement, name='delete_announcement'),

	# Login page
	path('login/', views.user_login, name='login'),

	# Logout page
	path('logout/', views.user_logout, name='logout'),
]
