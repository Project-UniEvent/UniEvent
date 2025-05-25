from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from unievent_event_app.models import Event, Announcement, EventRegistration

class Command(BaseCommand):
    help = 'Create groups and assign default permissions'

    def handle(self, *args, **kwargs):
        groups = {
            "Student": [
                "can_register_event", "can_follow_club"
            ],
            "SchoolClub": [
                "add_event", "change_event", "delete_event",
                "add_announcement", "change_announcement", "delete_announcement"
            ],
            "SchoolDepartment": [
                "add_event", "change_event", "delete_event",
                "add_announcement", "change_announcement", "delete_announcement"
            ]
        }

        for group_name, perm_codes in groups.items():
            group, created = Group.objects.get_or_create(name=group_name)
            permissions = [Permission.objects.get(codename=code) for code in perm_codes]
            group.permissions.set(permissions)
            self.stdout.write(self.style.SUCCESS(
                f"{'Created' if created else 'Updated'} group '{group_name}' with {len(permissions)} permissions."
            ))
