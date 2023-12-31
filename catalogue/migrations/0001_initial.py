# Generated by Django 3.2.20 on 2023-07-29 08:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MaterialType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField()),
            ],
        ),
        migrations.CreateModel(
            name='Subtype',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField()),
            ],
        ),
        migrations.CreateModel(
            name='BriefTitle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_inputted_added', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(max_length=255)),
                ('subtitle', models.CharField(max_length=255)),
                ('authors', models.CharField(max_length=255)),
                ('edition', models.CharField(max_length=255)),
                ('lccn', models.CharField(blank=True, max_length=255, null=True)),
                ('ibsn', models.CharField(blank=True, max_length=255, null=True)),
                ('issn', models.CharField(blank=True, max_length=255, null=True)),
                ('author_name', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('info_place', models.CharField(max_length=255)),
                ('publisher', models.CharField(max_length=255)),
                ('info_date', models.DateField()),
                ('info_copyright', models.CharField(max_length=255)),
                ('extent', models.TextField(blank=True, null=True)),
                ('other_details', models.TextField(blank=True, null=True)),
                ('size', models.CharField(blank=True, max_length=255, null=True)),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='material', to='catalogue.materialtype')),
                ('sub_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub_type', to='catalogue.subtype')),
            ],
            options={
                'ordering': ['-date_inputted_added'],
            },
        ),
    ]
