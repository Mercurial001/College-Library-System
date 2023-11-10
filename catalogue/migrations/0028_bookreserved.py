# Generated by Django 3.2.20 on 2023-09-22 10:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('catalogue', '0027_registrations'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookReserved',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_reserved', models.DateField(auto_now_add=True)),
                ('books', models.ManyToManyField(related_name='book_reserved', to='catalogue.BriefTitle')),
                ('patron', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='book_reserved_for', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]