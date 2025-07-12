from django.contrib import admin

from activities.models import Child, Activity, ActivityInstance, ActivitySession, ActivityBooking


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    model = Child


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    model = Activity


@admin.register(ActivityInstance)
class ActivityInstanceAdmin(admin.ModelAdmin):
    model = ActivityInstance


@admin.register(ActivitySession)
class ActivitySessionAdmin(admin.ModelAdmin):
    model = ActivitySession


@admin.register(ActivityBooking)
class ActivityBookingAdmin(admin.ModelAdmin):
    model = ActivityBooking
