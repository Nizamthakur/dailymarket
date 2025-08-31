from django.db import models
from django.utils.text import slugify
from accounts.models import CustomUser


class VendorStore(models.Model):
    user = models.ForeignKey(CustomUser, verbose_name=("vendor_user"), on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    slug = models.CharField(max_length=115,unique=True, blank=True)
    logo = models.ImageField( upload_to='media/vendoreStore/logo/', height_field=None, width_field=None, max_length=None,blank=True,null=True)
    cover_photo = models.ImageField( upload_to='media/vendoreStore/coverPhoto/', height_field=None, width_field=None, max_length=None,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0) 

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(VendorStore,self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
class WithdrawRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    vendor = models.ForeignKey(VendorStore, on_delete=models.CASCADE, related_name="withdraw_requests")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vendor.name} - {self.amount} ৳ - {self.status}"
