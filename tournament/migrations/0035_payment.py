# Generated by Django 4.2 on 2023-09-04 13:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0034_alter_participant_approval'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('tournament.participant',),
        ),
    ]