# Generated by Django 2.1.7 on 2019-03-21 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0010_auto_20190227_1136'),
    ]

    operations = [
        migrations.AddField(
            model_name='ad',
            name='internal_url',
            field=models.URLField(null=True, unique=True),
        ),
    ]
