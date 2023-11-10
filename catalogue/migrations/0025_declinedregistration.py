# Generated by Django 3.2.20 on 2023-09-21 01:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0014_alter_user_email'),
        ('catalogue', '0024_emailmessage'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeclinedRegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=150)),
                ('first_name', models.CharField(max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(max_length=150, verbose_name='last name')),
                ('email', models.CharField(max_length=255)),
                ('contact_no', models.IntegerField(blank=True, null=True)),
                ('date_declined', models.DateField(auto_now_add=True)),
                ('number_loc', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='declined_register_patron_number_location', to='auth.usernumberlocation')),
            ],
        ),
    ]