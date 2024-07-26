from django.contrib import admin
from .models import CustomUser , BitcoinTransaction
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(BitcoinTransaction)
