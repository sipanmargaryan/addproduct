# Generated by Django 2.2 on 2019-04-09 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0016_savedsearch'),
    ]

    operations = [
        migrations.AddField(
            model_name='ad',
            name='external_phone_number',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
