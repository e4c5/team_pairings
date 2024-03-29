# Generated by Django 4.2 on 2023-07-14 07:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import profiles.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Audit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.SmallIntegerField()),
                ('user_id', models.IntegerField()),
                ('data', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('player_id', models.CharField(max_length=5)),
                ('about_me', models.CharField(blank=True, max_length=512, null=True)),
                ('website_url', models.URLField(blank=True, max_length=128, null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('U', '')], default='U', max_length=1)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('is_public', models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False, verbose_name='Make profile public')),
                ('user_preferences', models.JSONField(default=dict)),
                ('national_list_name', models.CharField(blank=True, max_length=128, null=True)),
                ('wespa_list_name', models.CharField(blank=True, max_length=128, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Avatar',
            fields=[
                ('id', models.BigIntegerField(default=profiles.fields.make_id, primary_key=True, serialize=False)),
                ('photo_link', models.CharField(blank=True, max_length=250, null=True)),
                ('is_main', models.BooleanField(default=False)),
                ('user', models.ForeignKey(blank=True, db_column='userId', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PhoneNumber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.BigIntegerField(unique=True)),
                ('verified', models.BooleanField(default=False)),
                ('primary', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'number')},
            },
        ),
    ]
