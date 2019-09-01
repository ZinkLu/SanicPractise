# -*- coding: utf-8 -*-
from sanic.request import Request


class MyRequest(Request):

    @property
    def single_args(self):
        """只取第一个值作为值"""
        return {k: v[0] for k, v in self.args.items()}
