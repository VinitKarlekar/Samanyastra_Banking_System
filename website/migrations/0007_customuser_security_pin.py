# Generated by Django 5.1.7 on 2025-03-23 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0006_bankingmessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='security_pin',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
    ]
