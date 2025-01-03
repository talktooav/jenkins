# Generated by Django 3.2.4 on 2021-07-16 10:48

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('jobrole', '0001_initial'),
        ('jobusers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PushNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('link', models.URLField(max_length=255)),
                ('description', models.TextField(verbose_name='Description')),
                ('sent_status', models.IntegerField(default=0)),
                ('schedule_date_time', models.CharField(default='', max_length=255)),
                ('is_deleted', models.BooleanField(default=False)),
                ('createdAt', models.DateTimeField(default=django.utils.timezone.now)),
                ('job_role', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='jobrole.jobroles')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='jobusers.jobusers')),
            ],
            options={
                'db_table': 'amrc_push_notification',
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('p_id', models.IntegerField(default=0)),
                ('n_type', models.CharField(choices=[('normal', 'Normal Notification'), ('update', 'Update Notification')], default='normal', max_length=30)),
                ('from_user_type', models.CharField(max_length=150)),
                ('to_user_id', models.IntegerField(default=0)),
                ('to_user_type', models.CharField(blank=True, max_length=150, null=True)),
                ('noti_type', models.CharField(max_length=50)),
                ('title', models.CharField(max_length=255)),
                ('sub_title', models.CharField(blank=True, max_length=255, null=True)),
                ('data', models.TextField(blank=True, null=True)),
                ('detail', models.JSONField(blank=True, null=True)),
                ('read_at', models.DateField(blank=True, null=True)),
                ('createdAt', models.DateTimeField(default=django.utils.timezone.now)),
                ('updatedAt', models.DateTimeField(auto_now_add=True, null=True)),
                ('from_user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jobusers.jobusers')),
            ],
            options={
                'db_table': 'amrc_notification',
            },
        ),
    ]