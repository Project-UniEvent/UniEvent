from django.contrib import admin
from .models import Student, SchoolClub, SchoolDepartment, Event, Announcement

admin.site.register(Student)
admin.site.register(SchoolClub)
admin.site.register(SchoolDepartment)
admin.site.register(Event)
admin.site.register(Announcement)
