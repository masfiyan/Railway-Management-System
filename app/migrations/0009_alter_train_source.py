# Generated by Django 4.0.2 on 2022-02-20 07:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_train'),
    ]

    operations = [
        migrations.AlterField(
            model_name='train',
            name='source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.station'),
        ),
    ]
