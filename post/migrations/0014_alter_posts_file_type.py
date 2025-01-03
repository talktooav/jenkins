# Generated by Django 3.2.4 on 2021-09-02 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0013_auto_20210902_1129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='posts',
            name='file_type',
            field=models.CharField(blank=True, choices=[('image', 'Image'), ('video', 'Video'), ('file', 'File')], max_length=30, null=True),
        ),
    ]