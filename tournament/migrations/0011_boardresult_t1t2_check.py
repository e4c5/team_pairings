# Generated by Django 4.1.7 on 2023-02-15 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0010_alter_participant_unique_together'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='boardresult',
            constraint=models.CheckConstraint(check=models.Q(('team1_id__lt', models.F('team2_id'))), name='t1t2_check'),
        ),
    ]