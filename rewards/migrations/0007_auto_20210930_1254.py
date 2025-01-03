# Generated by Django 3.2.4 on 2021-09-30 07:24

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('rewards', '0006_auto_20210825_1609'),
    ]

    operations = [
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store_id', models.CharField(max_length=30)),
                ('name', models.CharField(max_length=255)),
                ('createdAt', models.DateTimeField(default=django.utils.timezone.now)),
                ('updatedAt', models.DateTimeField(auto_now_add=True, null=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('brand_id', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'amrc_store',
            },
        ),
        migrations.AddField(
            model_name='starofthemonth',
            name='store',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='rewards.store'),
        ),
    ]