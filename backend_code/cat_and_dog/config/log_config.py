import logging

logconfig_dict = dict(
    version=1,
    disable_existing_loggers=False,
    loggers={
        "sanic.root": {"level": "INFO", "handlers": ["console"]},
        "sanic.error": {
            "level": "INFO",
            "handlers": ["error_console"],
            "propagate": True,
            "qualname": "sanic.error",
        },
        "sanic.access": {
            "level": "INFO",
            "handlers": ["access_console"],
            "propagate": True,
            "qualname": "sanic.access",
        },
    },
    handlers={
        "console": {
            "class": "logging.handlers.RotatingFileHandler",
            "maxBytes": 1024 * 1024 * 1024,
            "backupCount": 10,
            "formatter": "generic",
            'mode': 'w+',
            "filename": "/var/log/sanic_app/root.log"
        },
        "error_console": {
            "class": "logging.handlers.RotatingFileHandler",
            "maxBytes": 1024 * 1024 * 1024,
            "backupCount": 10,
            "formatter": "generic",
            'mode': 'w+',
            "filename": "/var/log/sanic_app/error.log"
        },
        "access_console": {
            "class": "logging.handlers.RotatingFileHandler",
            "maxBytes": 1024 * 1024 * 1024,
            "backupCount": 10,
            "formatter": "access",
            'mode': 'w+',
            "filename": "/var/log/sanic_app/access.log"
        },
    },
    formatters={
        "generic": {
            "format": "%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
            "class": "logging.Formatter",
        },
        "access": {
            "format": "%(asctime)s - (%(name)s)[%(levelname)s][%(host)s]: "
                      + "%(request)s %(message)s %(status)d %(byte)d",
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
            "class": "logging.Formatter",
        },
    },
)

logger = logging.getLogger("sanic.root")
error_logger = logging.getLogger("sanic.error")
access_logger = logging.getLogger("sanic.access")
