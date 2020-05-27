# -*- coding: utf-8 -*-
import logging
import multiprocessing

import uvicorn

logging.getLogger("gino").setLevel(logging.WARNING)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "[%(process)d] [%(asctime)s] %(levelname)s [%(filename)s:%(lineno)s] %(message)s %(message)s",
            "use_colors": True,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            # "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
            "fmt": '[%(process)d] [%(asctime)s] %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {"handlers": ["default"], "level": "INFO"},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    },
}

if __name__ == '__main__':
    uvicorn.run("app:app",
                port=5000,
                log_level="info",
                access_log=True,
                reload=True,
                log_config=LOGGING_CONFIG,
                workers=multiprocessing.cpu_count() * 2 + 1
                )
