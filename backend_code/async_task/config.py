# -*- coding: utf-8 -*-
import logging

from celery.app.log import Logging


class MyLogging(Logging):

    def setup(self, loglevel=None, logfile=None, redirect_stdouts=False,
              redirect_level='WARNING', colorize=None, hostname=None):
        super().setup(LOGLEVEL, LOGFILE, redirect_stdouts,
                      redirect_level, colorize, hostname)


CELERY_ACCEPT_CONTENT = ['ujson']

CELERY_TASK_SERIALIZER = 'ujson'

CELERY_RESULT_SERIALIZER = 'ujson'

BROKER_URL = 'pyamqp://guest:guest@localhost//'

LOGFILE = '/var/log/celery/celery.log'

LOGLEVEL = logging.INFO

CELERYD_REDIRECT_STDOUTS_LEVEL = logging.INFO

CELERY_IMPORTS = ("async_task.tasks",)

LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            # 'datefmt': '%m-%d-%Y %H:%M:%S'
            'format': '"[%(asctime)s: %(levelname)s/%(processName)s] %(message)s"'
        }
    },
    'handlers': {
        'celery': {
            'level': 'INFO',
            # 'level': 'DEBUG',
            'formatter': 'simple',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGFILE,
            # 'when': 'midnight',
            "maxBytes": 1024 * 1024 * 1024,
            "backupCount": 10,
            'mode': 'w+',
        },
    },
    'celery_app': {
        'celery_info_log': {
            'handlers': ['celery'],
            'level': 'INFO',
            'propagate': True,
        }
    }
}
