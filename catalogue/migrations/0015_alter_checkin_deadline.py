# Generated by Django 3.2.19 on 2023-09-09 01:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0014_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkin',
            name='deadline',
            field=models.DateField(null=True),
        ),
    ]
