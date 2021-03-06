# Generated by Django 2.1.2 on 2018-12-04 20:54

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ads', '0003_ad_publish_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdReview',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(default=5, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('feedback', models.TextField(max_length=1000)),
                ('saved_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ['-saved_at'],
            },
        ),
        migrations.AddField(
            model_name='ad',
            name='views',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='adreview',
            name='ad',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ads.Ad'),
        ),
        migrations.AddField(
            model_name='adreview',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='adreview',
            unique_together={('ad', 'user')},
        ),
    ]
