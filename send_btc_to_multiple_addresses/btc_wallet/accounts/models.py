from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Add any additional fields here if needed
    
    bitcoin_address = models.CharField(max_length=100, blank=True, null=True)
    wallet_name = models.CharField(max_length=100, blank=True, null=True)
    private_key = models.CharField(max_length=200, blank=True, null=True)

class BitcoinTransaction(models.Model):
    sender = models.ForeignKey(CustomUser, related_name='sent_transactions', on_delete=models.CASCADE)
    recipient_address = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=18, decimal_places=8)
    transaction_id = models.CharField(max_length=64, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)