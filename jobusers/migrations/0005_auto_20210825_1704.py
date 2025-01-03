# Generated by Django 3.2.4 on 2021-08-25 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobusers', '0004_job_user_points_log'),
    ]

    operations = [
        migrations.RenameField(
            model_name='job_user_points_log',
            old_name='point_slug',
            new_name='point_action',
        ),
        migrations.AddField(
            model_name='job_user_points_log',
            name='action_type',
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
    ]