# Gerated by Django 3.2.4 on 2021-07-16 10:48

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [

        ('jobrole', '0001_initial'),
        ('userentity', '0001_initial'),    ]

    operations = [
        migrations.CreateModel(
            name='Job_User_Login_Log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(default=0)),
                ('enterprise_id', models.IntegerField(default=0)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('login_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('createdAt', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'amrc_job_user_login_logs',
            },
        ),
        migrations.CreateModel(
            name='JobUsers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee_code', models.CharField(max_length=30, unique=True)),
                ('employee_name', models.CharField(blank=True, max_length=50, null=True)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('U', 'Unisex/Parody')], max_length=1)),
                ('market', models.CharField(blank=True, max_length=50, null=True)),
                ('city', models.CharField(blank=True, max_length=50, null=True)),
                ('nationality', models.CharField(blank=True, max_length=50, null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('hire_date', models.CharField(blank=True, max_length=50, null=True)),
                ('cc_code', models.CharField(blank=True, max_length=30, null=True)),
                ('cost_name', models.CharField(blank=True, max_length=50, null=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('created_by', models.IntegerField(default=0)),
                ('updated_by', models.IntegerField(default=0)),
                ('reg_id', models.TextField(blank=True, max_length=50, null=True)),
                ('status', models.BooleanField(default=True)),
                ('is_logged', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False, verbose_name='active')),
                ('logged_in_time', models.DateField(blank=True, null=True)),
                ('userProfileImage', models.ImageField(blank=True, null=True, upload_to='profile_pic')),
                ('user_point', models.IntegerField(default=50, help_text='User total point')),
                ('createdAt', models.DateTimeField(default=django.utils.timezone.now)),
                ('updatedAt', models.DateTimeField(auto_now_add=True, null=True)),
                ('entity', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='userentity.userentity')),
                ('job_role', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='jobrole.jobroles')),
            ],
            options={
                'db_table': 'amrc_job_users',
            },
        ),
        migrations.CreateModel(
            name='PhoneOTP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=10, unique=True, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+999999999'. Up to 14 digits allowed.", regex='^\\+?1?\\d{9,10}$')])),
                ('otp', models.CharField(blank=True, max_length=9, null=True)),
                ('count', models.IntegerField(default=0, help_text='Number of otp sent')),
                ('verified', models.BooleanField(default=False, help_text='If otp verification got successful')),
            ],
            options={
                'db_table': 'amrc_phone_otp',
            },
        ),
        migrations.CreateModel(
            name='UserActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option_name', models.CharField(max_length=255)),
                ('option_val', models.TextField()),
                ('extra', models.CharField(blank=True, max_length=255, null=True)),
                ('createdAt', models.DateTimeField(default=django.utils.timezone.now)),
                ('updatedAt', models.DateTimeField(auto_now_add=True, null=True)),
                ('by_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='jobusers.jobusers')),
            ],
            options={
                'db_table': 'amrc_job_user_activity',
            },
        ),
    ]
