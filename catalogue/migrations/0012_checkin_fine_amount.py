# Generated by Django 3.2.20 on 2023-09-03 00:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0011_alter_checkin_deadline'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkin',
            name='fine_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
