from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm

class StudentCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            student_group, _ = Group.objects.get_or_create(name="Student")
            user.groups.add(student_group)
        return user

class ClubCreationForm(StudentCreationForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            club_group, _ = Group.objects.get_or_create(name="SchoolClub")
            user.groups.add(club_group)
        return user

class DepartmentCreationForm(StudentCreationForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            dept_group, _ = Group.objects.get_or_create(name="SchoolDepartment")
            user.groups.add(dept_group)
        return user
