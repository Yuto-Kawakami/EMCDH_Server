# Generated by Django 2.1 on 2018-12-19 02:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('handbook', '0012_auto_20181218_1838'),
    ]

    operations = [
        migrations.AddField(
            model_name='accesscontrol',
            name='suggest_history',
            field=models.TextField(blank=True),
        ),
    ]
