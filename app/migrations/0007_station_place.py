# Generated by Django 4.0.2 on 2022-02-15 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_remove_contactnumber_contact_for_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='station',
            name='place',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
