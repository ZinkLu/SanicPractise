# -*- coding: utf-8 -*-
from async_task.app import app


@app.task
def a(x, y):
    print("doing x + y")
    return x + y
