from django.db import models

from authentication.models import ParentUser, InstructorUser
from core.models import Society, ActivityCategory
from payments.models import Order


class Child(models.Model):
    GENDER_MALE = 'MALE'
    GENDER_FEMALE = 'FEMALE'
    GENDER_OTHER = 'OTHER'

    GENDER_CHOICES = [
        (GENDER_MALE, GENDER_MALE),
        (GENDER_FEMALE, GENDER_FEMALE),
        (GENDER_OTHER, GENDER_OTHER),
    ]
    
    parent_user = models.ForeignKey(ParentUser, on_delete=models.PROTECT, blank=False, null=False)
    full_name = models.EmailField(blank=False, null=False)
    date_of_birth = models.DateField(blank=False, null=False)
    gender = models.CharField(max_length=7, choices=GENDER_CHOICES, null=False, blank=False)
    interested_in_activity_categories = models.ManyToManyField(ActivityCategory, blank=True, related_name='+')
    # TODO(AbhilakshSinghReen): add these in later
    # display_image = models.ImageField(upload_to='user_images/', blank=True, null=True)

    class Meta:
        verbose_name = "Child"
        verbose_name_plural = "Children"
        constraints = [
            models.UniqueConstraint(fields=['parent_user', 'full_name'], name='unique_parent_child'),
        ]
    

class Activity(models.Model):
    RECOMMENDED_GENDER_MALE = 'MALE'
    RECOMMENDED_GENDER_FEMALE = 'FEMALE'
    RECOMMENDED_GENDER_ANY = 'ANY'

    RECOMMENDED_GENDER_CHOICES = [
        (RECOMMENDED_GENDER_MALE, RECOMMENDED_GENDER_MALE),
        (RECOMMENDED_GENDER_FEMALE, RECOMMENDED_GENDER_FEMALE),
        (RECOMMENDED_GENDER_ANY, RECOMMENDED_GENDER_ANY),
    ]

    category = models.ForeignKey(ActivityCategory, on_delete=models.PROTECT)
    instructor_user = models.ForeignKey(InstructorUser, on_delete=models.PROTECT)
    title = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    recommended_min_age = models.IntegerField(default=1, blank=False, null=False)
    recommended_max_age = models.IntegerField(blank=True, null=True)
    recommended_gender = models.CharField(
        max_length=7,
        default=RECOMMENDED_GENDER_ANY,
        choices=RECOMMENDED_GENDER_CHOICES,
        null=False,
        blank=False
    )
    # TODO: Add these in later
    # thumbnail_images = 
    # gallery_images = 

    class Meta:
        verbose_name = "Activity"
        verbose_name_plural = "Activities"
    
    def __str__(self):
        return f"{self.title} by Instructor {str(self.instructor_user)}"


class ActivityInstance(models.Model):
    RECURRENCE_FREQUENCY_DAILY = 'DAILY'
    RECURRENCE_FREQUENCY_WEEKLY = 'WEEKLY'
    RECURRENCE_FREQUENCY_MONTHLY = 'MONTHLY'
    RECURRENCE_FREQUENCY_ONCE_PER_TWO_WEEKS = 'ONCE_PER_TWO_WEEKS'
    RECURRENCE_FREQUENCY_TWICE_PER_WEEK = 'TWICE_PER_WEEK'
    RECURRENCE_FREQUENCY_CUSTOM = 'CUSTOM'

    RECURRENCE_FREQUENCY_CHOICES = [
        (RECURRENCE_FREQUENCY_DAILY, RECURRENCE_FREQUENCY_DAILY),
        (RECURRENCE_FREQUENCY_WEEKLY, RECURRENCE_FREQUENCY_WEEKLY),
        (RECURRENCE_FREQUENCY_MONTHLY, RECURRENCE_FREQUENCY_MONTHLY),
        (RECURRENCE_FREQUENCY_ONCE_PER_TWO_WEEKS, RECURRENCE_FREQUENCY_ONCE_PER_TWO_WEEKS),
        (RECURRENCE_FREQUENCY_TWICE_PER_WEEK, RECURRENCE_FREQUENCY_TWICE_PER_WEEK),
        (RECURRENCE_FREQUENCY_CUSTOM, RECURRENCE_FREQUENCY_CUSTOM)
    ]

    activity = models.ForeignKey(Activity, on_delete=models.PROTECT)
    society = models.ForeignKey(Society, on_delete=models.PROTECT)
    start_date = models.DateField(blank=False, null=False)
    end_date = models.DateField() # optional
    sessions_repeat = models.BooleanField(default=False)
    recurrence_frequency = models.CharField(
        max_length=31,
        choices=RECURRENCE_FREQUENCY_CHOICES,
        null=False,
        blank=False
    )
    cost = models.FloatField(blank=False, null=False)
    capacity = models.IntegerField(default=1, blank=False, null=False)
    # TODO: Add these in later
    # thumbnail_images = 
    # gallery_images = 

    class Meta:
        verbose_name = "Activity Instance"
        verbose_name_plural = "Activity Instances"
    
    def __str__(self):
        return f"{str(self.activity)} at {str(self.society)}"


class ActivitySession(models.Model):
    activity_instance = models.ForeignKey(
        ActivityInstance,
        related_name='sessions',
        on_delete=models.CASCADE
    )
    start_date_time = models.DateTimeField(blank=False, null=False)
    duration = models.DurationField(blank=False, null=False)
    title = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField()
    number = models.IntegerField(default=1, blank=False, null=False)

    class Meta:
        verbose_name = "Activity Session"
        verbose_name_plural = "Activity Sessions"
        constraints = [
            models.UniqueConstraint(fields=['activity_instance', 'number'], name='unique_activity_instance_session_number'),
        ]
    
    def __str__(self):
        return f"Session {self.number} for {str(self.activity_instance)}"


class PaymentPendingActivityBooking(models.Model):
    parent_user = models.ForeignKey(ParentUser, on_delete=models.PROTECT)
    activity_instance = models.ForeignKey(
        ActivityInstance,
        related_name='payment_pending_bookings',
        on_delete=models.PROTECT
    )
    children = models.ManyToManyField(Child, related_name='payment_pending_bookings')
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='payment_pending_bookings')

    class Meta:
        verbose_name = "Activity Booking"
        verbose_name_plural = "Activity Bookings"


class ActivityBooking(models.Model):
    parent_user = models.ForeignKey(ParentUser, on_delete=models.PROTECT)
    activity_instance = models.ForeignKey(
        ActivityInstance,
        related_name='bookings',
        on_delete=models.PROTECT
    )
    children = models.ManyToManyField(Child, related_name='bookings')
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='bookings')

    class Meta:
        verbose_name = "Activity Booking"
        verbose_name_plural = "Activity Bookings"
