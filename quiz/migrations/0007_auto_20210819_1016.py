# Generated by Django 3.2.4 on 2021-08-19 04:46

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0006_remove_quizes_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quizresult',
            name='ip_address',
        ),
        migrations.AddField(
            model_name='quizresult',
            name='createdAt',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='quizresult',
            name='updatedAt',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
