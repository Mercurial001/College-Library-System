# Generated by Django 3.2.20 on 2023-08-22 06:51

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0009_auto_20230804_1942'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='brieftitle',
            options={'ordering': ['-date_inputted_added'], 'verbose_name_plural': 'Books'},
        ),
        migrations.AddField(
            model_name='checkin',
            name='deadline',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
