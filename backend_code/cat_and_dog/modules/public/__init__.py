# -*- coding: utf-8 -*-

from sanic import Blueprint

from ..api_version import api_prefix

public_bp = Blueprint("public", url_prefix=api_prefix)


from . import upload
