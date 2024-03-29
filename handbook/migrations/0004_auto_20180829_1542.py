# Generated by Django 2.1 on 2018-08-29 06:42

import address.models
from django.db import migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0002_auto_20160213_1726'),
        ('handbook', '0003_auto_20180829_1512'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='address1',
            field=address.models.AddressField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='address.Address'),
        ),
        migrations.AddField(
            model_name='user',
            name='address2',
            field=address.models.AddressField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='address.Address'),
        ),
    ]
