# -*- coding: utf-8 -*-
import logging.config

import ujson
from async_task import config
from celery import Celery
from kombu import serialization


def make_celery_app(mode: str):
    # 使用ujson来代替原生json模块
    serialization.register(
        'ujson', ujson.dumps, ujson.loads,
        content_type='application/x-ujson',
        content_encoding='utf-8',
    )

    if mode.lower() == "debug":
        app = Celery("cat_and_dogs")
    else:
        app = Celery("cat_and_dogs", log=config.MyLogging)
        logging.config.dictConfig(config.LOG_CONFIG)

    app.config_from_object(config)
    return app
