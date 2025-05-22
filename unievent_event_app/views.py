from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.utils import timezone
from django.contrib.auth.models import User, Group
from .models import Event, Announcement, EventRegistration, ClubRegistration
from .forms import StudentCreationForm, ClubCreationForm, DepartmentCreationForm
from django.db.models import Q

# Helper function
def is_club_or_department(user):
    return hasattr(user, 'schoolclub') or hasattr(user, 'schooldepartment')

# Home page
def home_page(request):
    if request.user.is_authenticated:
        event_ids = EventRegistration.objects.filter(user=request.user).values_list('event_id', flat=True)
    else:
        event_ids = []

    now = timezone.now()
    today = now.date()

    todays_events = Event.objects.filter(start_datetime__date=today).order_by('-start_datetime')

    top_registered_events = (
        Event.objects
        .filter(start_datetime__gt=now)
        .annotate(registration_count=Count('eventregistration'))
        .order_by('-registration_count', '-start_datetime')[:5]
    )

    announcements = Announcement.objects.all().order_by('-created_at')[:5]

    return render(request, 'home.html', {
        'events': todays_events,
        'all_events': top_registered_events,
        'event_ids': event_ids,
        'announcements': announcements,
        'now': now,
        'today': today,
    })

# Event registration
@login_required
def register_to_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    user = request.user

    if not user.groups.filter(name="Student").exists():
        return render(request, 'not_allowed.html', {
            'message': "Only students can register for events.",
            'event': event
        })

    if event.start_datetime < timezone.now():
        return render(request, 'event_register.html', {
            'event': event,
            'registered': False,
            'error': "You cannot register for an event that has already ended.",
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

# Create Event
@login_required
def create_event(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        is_paid = 'is_paid' in request.POST

        Event.objects.create(
            title=request.POST['title'],
            description=request.POST['description'],
            location=request.POST['location'],
            start_datetime=request.POST['start_datetime'],
            end_datetime=request.POST.get('end_datetime') or None,
            capacity=request.POST.get('capacity') or None,
            image=image,
            is_paid=is_paid,
            price=request.POST.get('price') if is_paid else None,
            created_by=request.user
        )
        return redirect('profile')
    return render(request, 'create_event.html')

# Update Event
@login_required
def update_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        event.title = request.POST['title']
        event.description = request.POST['description']
        event.location = request.POST['location']
        event.start_datetime = request.POST['start_datetime']
        event.end_datetime = request.POST.get('end_datetime') or None
        event.capacity = request.POST.get('capacity') or None
        event.is_paid = 'is_paid' in request.POST
        event.price = request.POST.get('price') if event.is_paid else None

        if 'image' in request.FILES:
            event.image = request.FILES['image']

        event.save()
        return redirect('profile')
    return render(request, 'edit_event.html', {'event': event})

# Delete Event
@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if event.created_by == request.user:
        event.delete()
    return redirect('profile')

# Create Announcement
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

# Update Announcement
@login_required
def update_announcement(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    if request.method == 'POST':
        announcement.title = request.POST['title']
        announcement.content = request.POST['content']
        announcement.save()
        return redirect('profile')
    return render(request, 'edit_announcement.html', {'announcement': announcement})

# Delete Announcement
@login_required
def delete_announcement(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    if announcement.created_by == request.user:
        announcement.delete()
    return redirect('profile')

# Profile View
@login_required
def profile_view(request):
    registrations = EventRegistration.objects.filter(user=request.user).select_related("event")
    club_regs = ClubRegistration.objects.filter(
        user=request.user,
        club__groups__name="SchoolClub"
    ).select_related("club")
    followed_clubs = [reg.club for reg in club_regs]

    context = {
        'registrations': registrations,
        'followed_clubs': followed_clubs,
    }

    if request.user.is_superuser:
        students = User.objects.filter(groups__name="Student")
        clubs = User.objects.filter(groups__name="SchoolClub")
        departments = User.objects.filter(groups__name="SchoolDepartment")
        context.update({
            'all_students': students,
            'all_clubs': clubs,
            'all_departments': departments,
        })

    return render(request, 'profile.html', context)

# Yeni View: Add User (Admin Paneli)
@login_required
def add_user_view(request):
    if not request.user.is_superuser:
        return redirect('home')

    role = request.GET.get('role', 'student')  # default student

    form_class = {
        'student': StudentCreationForm,
        'club': ClubCreationForm,
        'department': DepartmentCreationForm,
    }.get(role, StudentCreationForm)

    form = form_class(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('profile')

    return render(request, 'add_user.html', {
        'form': form,
        'selected_role': role,
    })

# All Events View
def all_events(request):
    now = timezone.now()
    event_ids = []
    if request.user.is_authenticated:
        event_ids = EventRegistration.objects.filter(user=request.user).values_list('event_id', flat=True)
    events = Event.objects.all().order_by('-start_datetime')
    return render(request, 'all_events.html', {
        'events': events,
        'event_ids': event_ids,
        'today': now.date(),
        'now': now,
    })

# All Announcements
def all_announcements(request):
    announcements = Announcement.objects.all().order_by('-created_at')
    return render(request, 'all_announcements.html', {
        'announcements': announcements
    })

# All Clubs
def all_clubs(request):
    clubs = User.objects.filter(groups__name="SchoolClub")
    followed_ids = []
    if request.user.is_authenticated:
        followed_ids = ClubRegistration.objects.filter(user=request.user).values_list("club_id", flat=True)

    return render(request, 'all_clubs.html', {
        'clubs': clubs,
        'followed_ids': followed_ids
    })

# Follow Club
@login_required
def follow_club(request, club_id):
    if not request.user.groups.filter(name="Student").exists():
        return render(request, 'not_allowed.html', {
            'message': "Only students can join (follow) clubs."
        })
    ClubRegistration.objects.get_or_create(user=request.user, club_id=club_id)
    return redirect(request.META.get('HTTP_REFERER', 'all_clubs'))

# Unfollow Club
@login_required
def unfollow_club(request, club_id):
    if not request.user.groups.filter(name="Student").exists():
        return render(request, 'not_allowed.html', {
            'message': "Only students can leave (unfollow) clubs."
        })
    ClubRegistration.objects.filter(user=request.user, club_id=club_id).delete()
    return redirect(request.META.get('HTTP_REFERER', 'all_clubs'))

# Club Profile
def club_profile(request, club_id):
    now = timezone.now()
    club = get_object_or_404(User, id=club_id, groups__name="SchoolClub")
    events = Event.objects.filter(created_by=club).order_by('-start_datetime')
    announcements = Announcement.objects.filter(created_by=club).order_by('-created_at')

    event_ids = []
    if request.user.is_authenticated:
        event_ids = EventRegistration.objects.filter(user=request.user).values_list('event_id', flat=True)

    return render(request, 'club_profile.html', {
        'club': club,
        'events': events,
        'announcements': announcements,
        'event_ids': event_ids,
        'today': now.date(),
        'now': now,
    })

# Search
def search_view(request):
    query = request.GET.get('q', '').strip()

    if not query:
        return redirect('home')

    # Event, Announcement ve Club için arama
    event_results = Event.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    )

    announcement_results = Announcement.objects.filter(
        Q(title__icontains=query) | Q(content__icontains=query)
    )

    club_results = User.objects.filter(
        groups__name="SchoolClub",
        username__icontains=query
    )

    # Kullanıcının kayıtlı olduğu etkinliklerin ID'leri
    event_ids = []
    if request.user.is_authenticated:
        event_ids = EventRegistration.objects.filter(user=request.user).values_list('event_id', flat=True)

    # Eğer kullanıcı öğrenciyse takip ettiği kulüplerin ID'leri
    followed_ids = []
    if request.user.is_authenticated and request.user.groups.filter(name="Student").exists():
        followed_ids = ClubRegistration.objects.filter(user=request.user).values_list("club_id", flat=True)

    return render(request, 'search_results.html', {
        'query': query,
        'event_results': event_results,
        'announcement_results': announcement_results,
        'club_results': club_results,
        'event_ids': event_ids,
        'followed_ids': followed_ids,
        'now': timezone.now(),
    })

# Delete User
@login_required
def delete_user(request, user_id):
    if not request.user.is_superuser:
        return redirect('home')
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('profile')
    return redirect('profile')

# Edit User
@login_required
def edit_user(request, user_id):
    if not request.user.is_superuser:
        return redirect('home')

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()
        return redirect('profile')

    return render(request, 'edit_user.html', {'edit_user': user})

