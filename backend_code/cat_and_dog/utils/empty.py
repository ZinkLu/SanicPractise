# -*- coding: utf-8 -*-


class Empty:
    """为了和None区分开"""

    def __bool__(self):
        return False

    def __str__(self):
        return "Empty"
