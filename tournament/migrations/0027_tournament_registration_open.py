# Generated by Django 4.2 on 2023-08-27 03:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0026_tournament_round_robin'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='registration_open',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]