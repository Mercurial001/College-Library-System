# Generated by Django 3.2.20 on 2023-10-03 01:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0030_auto_20231002_2356'),
    ]

    operations = [
        migrations.AddField(
            model_name='brieftitle',
            name='date_borrowed',
            field=models.DateField(null=True),
        ),
    ]
