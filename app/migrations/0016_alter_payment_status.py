# Generated by Django 4.0.2 on 2022-03-08 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_rename_created_at_bookingdetail_booking_dt_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(auto_created=True, blank=True, default='Paid', max_length=50, null=True),
        ),
    ]
