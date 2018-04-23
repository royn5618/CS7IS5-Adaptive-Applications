"""Celery inside django task manager."""
from __future__ import absolute_import, unicode_literals
import os

import django
from celery import Celery
import datetime


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsrecoapp.settings')

django.setup()

app = Celery('newsrecoapp')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


app.conf.update(
    CELERYBEAT_SCHEDULE={
        'update_news-every-2-minutes': {
            'task': 'application.tasks.periodic_update_news',
            'schedule': datetime.timedelta(seconds=300),
            'args': ()
        }
    }
)


# @app.task(bind=True)
# def debug_task(self):
#     """Print debug task."""
#     print('Request: {0!r}'.format(self.request))