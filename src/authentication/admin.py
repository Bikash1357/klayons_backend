from django.contrib import admin

from authentication.models import CustomUser, ParentUser, InstructorUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    model = CustomUser


@admin.register(ParentUser)
class ParentUserAdmin(admin.ModelAdmin):
    model = ParentUser


@admin.register(InstructorUser)
class InstructorUserAdmin(admin.ModelAdmin):
    model = InstructorUser
