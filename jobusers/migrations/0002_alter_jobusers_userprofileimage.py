# Generated by Django 3.2.4 on 2021-08-06 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobusers', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobusers',
            name='userProfileImage',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]