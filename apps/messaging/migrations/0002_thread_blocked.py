# Generated by Django 2.1.2 on 2018-12-14 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='blocked',
            field=models.BooleanField(default=False),
        ),
    ]
