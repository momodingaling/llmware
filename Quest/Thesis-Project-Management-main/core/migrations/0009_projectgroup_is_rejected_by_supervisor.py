# Generated by Django 5.0.6 on 2024-05-16 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_project_is_application_selected'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectgroup',
            name='is_rejected_by_supervisor',
            field=models.BooleanField(default=False),
        ),
    ]
