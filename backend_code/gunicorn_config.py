import multiprocessing
from gunicorn.glogging import Logger
import os

# os.makedirs("/var/log/sanic_app/")


bind = '127.0.0.1:5000'

debug = False

# 启动的进程数
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sanic.worker.GunicornWorker'
# worker_class = 'uvicorn.workers.UvicornWorker'


# TODO: 什么意思?
x_forwarded_for_header = 'X-FORWARDED-FOR'

# timeout
timeout = 30

# logging
# logger_class = "gunicorn.glogging.Logger"
# loglevel = "warning"
# errorlog = "/var/log/sanic_app/app.log"
# capture_output = True

# logconfig_dict = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'loggers': {
#         "gunicorn.error": {
#             "level": "DEBUG",  # 打日志的等级可以换的，下面的同理
#             "handlers": ["error_file"],  # 对应下面的键
#             "propagate": 1,
#             "qualname": "gunicorn.error"
#         },

#         "gunicorn.access": {
#             "level": "DEBUG",
#             "handlers": ["access_file"],
#             "propagate": 0,
#             "qualname": "gunicorn.access"
#         }
#     },
#     'handlers': {
#         "error_file": {
#             "class": "logging.handlers.RotatingFileHandler",
#             "maxBytes": 1024*1024*1024,  # 打日志的大小，我这种写法是1个G
#             "backupCount": 10,  # 备份多少份，经过测试，最少也要写1，不然控制不住大小
#             "formatter": "generic",  # 对应下面的键
#             # 'mode': 'w+',
#             "filename": "/var/log/sanic_app/gunicorn.error.log"  # 打日志的路径
#         },
#         "access_file": {
#             "class": "logging.handlers.RotatingFileHandler",
#             "maxBytes": 1024*1024*1024,
#             "backupCount": 1,
#             "formatter": "generic",
#             "filename": "/var/log/sanic_app/gunicorn.access.log",
#         }
#     },
#     'formatters': {
#         "generic": {
#             # 打日志的格式
#             "format": "'[%(process)d] [%(asctime)s] %(levelname)s [%(filename)s:%(lineno)s] %(message)s'",
#             "datefmt": "[%Y-%m-%d %H:%M:%S %z]",  # 时间显示方法
#             "class": "logging.Formatter"
#         },
#         "access": {
#             "format": "'[%(process)d] [%(asctime)s] %(levelname)s [%(filename)s:%(lineno)s] %(message)s'",
#             "class": "logging.Formatter"
#         }
#     }
# }
