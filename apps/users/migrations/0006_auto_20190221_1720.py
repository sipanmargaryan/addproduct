# Generated by Django 2.1.2 on 2019-02-21 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_user_device_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='device_id',
            field=models.CharField(editable=False, max_length=200, null=True),
        ),
    ]