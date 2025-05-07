from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from .models import Event, Announcement, EventRegistration, ClubRegistration
from django.contrib.auth.models import Group

# Helper function
def is_club_or_department(user):
    return hasattr(user, 'schoolclub') or hasattr(user, 'schooldepartment')

# Home page (everyone sees all events and announcements)
def home_page(request):
    events = Event.objects.all().order_by('date')
    announcements = Announcement.objects.all().order_by('-created_at')
    return render(request, 'home.html', {
        'events': events,
        'announcements': announcements,
    })

# Student event registration
@login_required
@permission_required('unievent_event_app.can_register_event', raise_exception=True)
def register_to_event(request, event_id):
    if not hasattr(request.user, 'student'):
        return redirect('home')

    student = request.user.student
    event = get_object_or_404(Event, id=event_id)

    # Prevent duplicate registration
    EventRegistration.objects.get_or_create(student=student, event=event)

    return redirect('home')

# Create Event (for SchoolClub and SchoolDepartment)
@login_required
@permission_required('unievent_event_app.add_event', raise_exception=True)
def create_event(request):
    if not is_club_or_department(request.user):
        return redirect('home')

    if request.method == 'POST':
        Event.objects.create(
            title=request.POST['title'],
            description=request.POST['description'],
            location=request.POST['location'],
            date=request.POST['date'],
            created_by=request.user
        )
        return redirect('my_events')

    return render(request, 'create_event.html')

# View own events
@login_required
def my_events(request):
    if not is_club_or_department(request.user):
        return redirect('home')

    events = Event.objects.filter(created_by=request.user)
    return render(request, 'my_events.html', {'events': events})

# Edit event (only if owner)
@login_required
@permission_required('unievent_event_app.change_event', raise_exception=True)
def update_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if event.created_by != request.user:
        return redirect('home')

    if request.method == 'POST':
        event.title = request.POST['title']
        event.description = request.POST['description']
        event.location = request.POST['location']
        event.date = request.POST['date']
        event.save()
        return redirect('my_events')

    return render(request, 'edit_event.html', {'event': event})

# Delete event (only if owner)
@login_required
@permission_required('unievent_event_app.delete_event', raise_exception=True)
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if event.created_by == request.user:
        event.delete()
    return redirect('my_events')

# Create Announcement
@login_required
@permission_required('unievent_event_app.add_announcement', raise_exception=True)
def create_announcement(request):
    if not is_club_or_department(request.user):
        return redirect('home')

    if request.method == 'POST':
        Announcement.objects.create(
            title=request.POST['title'],
            content=request.POST['content'],
            created_by=request.user
        )
        return redirect('my_announcements')

    return render(request, 'create_announcement.html')

# View own announcements
@login_required
def my_announcements(request):
    if not is_club_or_department(request.user):
        return redirect('home')

    announcements = Announcement.objects.filter(created_by=request.user)
    return render(request, 'my_announcements.html', {'announcements': announcements})

# Edit announcement
@login_required
@permission_required('unievent_event_app.change_announcement', raise_exception=True)
def update_announcement(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    if announcement.created_by != request.user:
        return redirect('home')

    if request.method == 'POST':
        announcement.title = request.POST['title']
        announcement.content = request.POST['content']
        announcement.save()
        return redirect('my_announcements')

    return render(request, 'edit_announcement.html', {'announcement': announcement})

# Delete announcement
@login_required
@permission_required('unievent_event_app.delete_announcements', raise_exception=True)
def delete_announcement(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    if announcement.created_by == request.user:
        announcement.delete()
    return redirect('my_announcements')

# Profile View
@login_required
def profile_view(request):
    registrations = EventRegistration.objects.filter(user=request.user)

    # Followed Clubs
    club_regs = ClubRegistration.objects.filter(
        user=request.user,
        club__groups__name="SchoolClub"
    ).select_related("club")
    followed_clubs = [reg.club for reg in club_regs]

    return render(request, 'profile.html', {
        'registrations': registrations,
        'followed_clubs': followed_clubs,
    })
