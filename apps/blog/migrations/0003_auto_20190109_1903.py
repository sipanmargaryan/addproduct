# Generated by Django 2.1.2 on 2019-01-09 19:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_article_cover'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name_plural': 'Blog Categories'},
        ),
    ]
