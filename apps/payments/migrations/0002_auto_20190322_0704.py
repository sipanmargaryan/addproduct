# Generated by Django 2.1.7 on 2019-03-22 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='per_day',
        ),
        migrations.AddField(
            model_name='payment',
            name='premium_days',
            field=models.IntegerField(default=0),
        ),
    ]
