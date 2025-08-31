from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import WithdrawRequest

@receiver(post_save, sender=WithdrawRequest)
def deduct_vendor_balance(sender, instance, created, **kwargs):
    if not created and instance.status == 'approved':
        vendor = instance.vendor
        vendor.balance -= instance.amount
        vendor.save()