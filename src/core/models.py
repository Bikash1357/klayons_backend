from django.db import models


class Society(models.Model):
    name = models.CharField(max_length=63, blank=False, null=False)
    city = models.CharField(max_length=63, blank=False, null=False)
    state = models.CharField(max_length=63, blank=False, null=False)
    zip_code = models.CharField(max_length=15, blank=False, null=False)
    # TODO(AbhilakshSinghReen): should city and state be choices?
    # TODO(AbhilakshSinghReen): add latitude and longitude fields, can this be put in a single point field

    class Meta:
        verbose_name = "Society"
        verbose_name_plural = "Societies"
        constraints = [
            models.UniqueConstraint(fields=['name', 'zip_code'], name='unique_society_name_zip'),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.zip_code})"


class ActivityCategory(models.Model):
    name = models.CharField(max_length=31, unique=True, blank=False, null=False)

    class Meta:
        verbose_name = "Activity Category"
        verbose_name_plural = "Activity Categories"
