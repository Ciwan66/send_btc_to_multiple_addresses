# Generated by Django 5.0.6 on 2024-07-21 19:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_customuser_bitcoin_address_customuser_private_key'),
    ]

    operations = [
        migrations.CreateModel(
            name='BitcoinTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipient_address', models.CharField(max_length=100)),
                ('amount', models.DecimalField(decimal_places=8, max_digits=18)),
                ('transaction_id', models.CharField(blank=True, max_length=64, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_transactions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
