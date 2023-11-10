# Generated by Django 3.2.20 on 2023-11-04 08:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0014_alter_user_email'),
        ('catalogue', '0035_auto_20231104_0852'),
    ]

    operations = [
        migrations.AddField(
            model_name='paidfines',
            name='course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='paid_fines_patron_course', to='auth.usercourse'),
        ),
        migrations.AddField(
            model_name='paidfines',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='paid_fines_patron_department', to='auth.userdepartment'),
        ),
        migrations.AddField(
            model_name='paidfines',
            name='position',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='paid_fines_patron_position', to='auth.userposition'),
        ),
    ]
