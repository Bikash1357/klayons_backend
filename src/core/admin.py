from django.contrib import admin
from django.contrib.auth.models import Group
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

from core.models import Society, ActivityCategory


admin.site.site_title = "Klayons Administration"
admin.site.site_header = "Klayons Administration"
admin.site.index_title = "Admin Home"

admin.site.unregister(Group)

admin.site.unregister(BlacklistedToken)
admin.site.unregister(OutstandingToken)


@admin.register(Society)
class SocietyAdmin(admin.ModelAdmin):
    model = Society


@admin.register(ActivityCategory)
class ActivityCategoryAdmin(admin.ModelAdmin):
    model = ActivityCategory
