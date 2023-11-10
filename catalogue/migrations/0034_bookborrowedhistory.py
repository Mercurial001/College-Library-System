# Generated by Django 3.2.20 on 2023-10-24 10:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('catalogue', '0033_brieftitle_date_reserved'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookBorrowedHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_borrowed', models.DateTimeField(auto_now_add=True)),
                ('books', models.ManyToManyField(related_name='books_borrowed_history', to='catalogue.BriefTitle')),
                ('patron', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='patron_borrows_history', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
