# Generated by Django 4.2.7 on 2023-11-30 04:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('uploadsapp', '0003_modeluploads_is_uploaded'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='modeluploads',
            name='is_uploaded',
        ),
    ]