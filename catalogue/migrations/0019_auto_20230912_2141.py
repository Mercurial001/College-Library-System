# Generated by Django 3.2.20 on 2023-09-12 13:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('catalogue', '0018_course_numberlocation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkin',
            name='patron',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='patrons', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='patron',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='patrons_reserve', to=settings.AUTH_USER_MODEL),
        ),
    ]
