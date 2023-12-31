# Generated by Django 3.2.20 on 2023-09-07 04:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0012_checkin_fine_amount'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_reserved', models.DateTimeField(auto_now_add=True)),
                ('books', models.ManyToManyField(blank=True, related_name='patron_books_reserve', to='catalogue.BriefTitle')),
                ('patron', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='patrons_reserve', to='catalogue.patron')),
            ],
            options={
                'ordering': ['-date_reserved'],
            },
        ),
    ]
