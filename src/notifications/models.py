from django.db import models

from backend_main.settings import AUTH_USER_MODEL


class Notification(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="notifications")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255, blank=False, null=False)
    content = models.TextField(blank=False, null=False)
    navigate_to_type = models.CharField(max_length=63, blank=True, null=True)
    navigate_to_id = models.CharField(max_length=63, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user} - {self.title}"
