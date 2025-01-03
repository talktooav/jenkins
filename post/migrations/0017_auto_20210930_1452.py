# Generated by Django 3.2.4 on 2021-09-30 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0016_auto_20210927_1852'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='posts',
            name='height',
        ),
        migrations.RemoveField(
            model_name='posts',
            name='taggedusers',
        ),
        migrations.RemoveField(
            model_name='posts',
            name='width',
        ),
        migrations.AddField(
            model_name='posts',
            name='post_author',
            field=models.CharField(default='', max_length=6),
        ),
        migrations.AlterField(
            model_name='posts',
            name='description',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='posts',
            name='title',
            field=models.JSONField(default=dict),
        ),
    ]