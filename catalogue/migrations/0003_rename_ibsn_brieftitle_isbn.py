# Generated by Django 3.2.20 on 2023-07-29 10:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0002_auto_20230729_1714'),
    ]

    operations = [
        migrations.RenameField(
            model_name='brieftitle',
            old_name='ibsn',
            new_name='isbn',
        ),
    ]