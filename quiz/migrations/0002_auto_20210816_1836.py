# Generated by Django 3.2.4 on 2021-08-16 13:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quizes',
            name='options',
        ),
        migrations.RemoveField(
            model_name='quizquestions',
            name='user',
        ),
    ]
