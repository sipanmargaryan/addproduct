# Generated by Django 2.1.2 on 2019-01-07 14:02

import core.utils.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='cover',
            field=models.ImageField(default='', upload_to=core.utils.utils.get_file_path),
            preserve_default=False,
        ),
    ]
