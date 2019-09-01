# -*- coding: utf-8 -*-

from .status_code import *


class ApiException(Exception):
    """
    api接口抛出的异常
    """
    __slots__ = ("msg", "code")

    def __init__(self, msg: str, code: int):
        self.msg = msg
        self.code = code
        super().__init__(str(code) + ": " + msg)


class SchemaException(Exception):
    """
    验证参数时应该抛出的错误, 不使用ValidateError的原因是其无法在第一时间抛出异常
    """
    __slots__ = ()


LOGIN_ERROR = ApiException("用户名或密码不正确", UNAUTHORIZED)
