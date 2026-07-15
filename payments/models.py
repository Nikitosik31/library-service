from django.db import models

from borrowing.models import Borrowing


class Status(models.TextChoices):
    PENDING = "Pending"
    PAID = "Paid"


class Type(models.TextChoices):
    PAYMENT = "Payment"
    FINE = "Fine"


class Payment(models.Model):
    status = models.CharField(max_length=10, choices=Status.choices)
    type = models.CharField(max_length=10, choices=Type.choices)
    borrowing = models.ForeignKey(
        Borrowing, on_delete=models.CASCADE, related_name="payments"
    )
    session_url = models.URLField()
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)
