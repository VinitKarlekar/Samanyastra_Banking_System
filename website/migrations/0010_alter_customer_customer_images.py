# Generated by Django 5.0.6 on 2025-03-24 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0009_alter_customer_customer_images'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='customer_images',
            field=models.ImageField(blank=True, default='customer_images/default.jpeg', null=True, upload_to='customer_images/'),
        ),
    ]
