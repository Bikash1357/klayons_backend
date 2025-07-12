from django.db import models
from django.core.validators import MinValueValidator


from authentication.models import ParentUser


class Order(models.Model):
    parent_user = models.ForeignKey(ParentUser, on_delete=models.PROTECT, blank=False, null=False)
    amount = models.IntegerField(validators=[MinValueValidator(0)], blank=False, null=False)
    currency = models.CharField(max_length=7, blank=False, null=False)
    razorpay_order_id = models.CharField(max_length=255, unique=True, blank=False, null=False)
    razorpay_receipt = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.id} by {self.parent_user}"
