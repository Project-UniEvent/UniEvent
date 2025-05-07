from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Event, Announcement, EventRegistration, ClubRegistration

# Helper function
def is_club_or_department(user):
    return hasattr(user, 'schoolclub') or hasattr(user, 'schooldepartment')

# Home page
def home_page(request):
    if request.user.is_authenticated:
        event_ids = EventRegistration.objects.filter(user=request.user).values_list('event_id', flat=True)
    else:
        event_ids = []

    events = Event.objects.all().order_by('date')
    announcements = Announcement.objects.all().order_by('-created_at')

    return render(request, 'home.html', {
        'events': events,
        'event_ids': event_ids,
        'announcements': announcements,
    })

# Event registration (only students)
@login_required
def register_to_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    user = request.user

    if not user.groups.filter(name="Student").exists():
        return render(request, 'not_allowed.html', {
            'message': "Only students can register for events.",
            'event': event
        })

    registered = EventRegistration.objects.filter(user=user, event=event).exists()

    if 'register' in request.GET and not registered:
        EventRegistration.objects.create(user=user, event=event)
        registered = True
    elif 'unregister' in request.GET and registered:
        EventRegistration.objects.filter(user=user, event=event).delete()
        if request.META.get('HTTP_REFERER', '').endswith('/profile/'):
            return redirect('profile')
        registered = False

    return render(request, 'event_register.html', {
        'event': event,
        'registered': registered,
    })

# Create Event → redirect to profile
@login_required
def create_event(request):
    if request.method == 'POST':
        Event.objects.create(
            title=request.POST['title'],
            description=request.POST['description'],
            location=request.POST['location'],
            date=request.POST['date'],
            created_by=request.user
        )
        return redirect('profile')
    return render(request, 'create_event.html')

# View own events
@login_required
def my_events(request):
    events = Event.objects.filter(created_by=request.user)
    return render(request, 'my_events.html', {'events': events})

# Edit Event → redirect to profile
@login_required
def update_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        event.title = request.POST['title']
        event.description = request.POST['description']
        event.location = request.POST['location']
        event.date = request.POST['date']
        event.save()
        return redirect('profile')
    return render(request, 'edit_event.html', {'event': event})

# Delete Event → redirect to profile ✅
@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if event.created_by == request.user:
        event.delete()
    return redirect('profile')

# Create Announcement → redirect to profile
@login_required
def create_announcement(request):
    if request.method == 'POST':
        Announcement.objects.create(
            title=request.POST['title'],
            content=request.POST['content'],
            created_by=request.user
        )
        return redirect('profile')
    return render(request, 'create_announcement.html')

# View own announcements
@login_required
def my_announcements(request):
    announcements = Announcement.objects.filter(created_by=request.user)
    return render(request, 'my_announcements.html', {'announcements': announcements})

# Edit Announcement → redirect to profile
@login_required
def update_announcement(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    if request.method == 'POST':
        announcement.title = request.POST['title']
        announcement.content = request.POST['content']
        announcement.save()
        return redirect('profile')
    return render(request, 'edit_announcement.html', {'announcement': announcement})

# Delete Announcement → redirect to profile ✅
@login_required
def delete_announcement(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    if announcement.created_by == request.user:
        announcement.delete()
    return redirect('profile')

# Profile View
def profile_view(request):
    registrations = EventRegistration.objects.filter(user=request.user).select_related("event")
    club_regs = ClubRegistration.objects.filter(
        user=request.user,
        club__groups__name="SchoolClub"
    ).select_related("club")
    followed_clubs = [reg.club for reg in club_regs]

    return render(request, 'profile.html', {
        'registrations': registrations,
        'followed_clubs': followed_clubs,
    })
