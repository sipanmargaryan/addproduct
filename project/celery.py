import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('project')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'featured-every-hour': {
        'task': 'ads.tasks.featured',
        'schedule': crontab(hour='*', minute=1),
    },
    'notify-me-twice-in-hour': {
        'task': 'ads.tasks.notify_me',
        'schedule': crontab(hour='*', minute="01,31"),
    },
    'currency-every-day': {
        'task': 'ads.tasks.currency',
        'schedule': crontab(hour=9, minute=0),
    },
}

app.autodiscover_tasks()
