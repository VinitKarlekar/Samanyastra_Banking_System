# Generated by Django 5.0.7 on 2025-03-22 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_transaction_transfer'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='customer_images',
            field=models.ImageField(null=True, upload_to='static/'),
        ),
    ]
