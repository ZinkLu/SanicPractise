from inspect import isawaitable

import aioredis
from asyncpg.exceptions import PostgresError
from marshmallow import ValidationError
from sanic import Sanic as _Sanic
from sanic.exceptions import SanicException
from sanic.handlers import ErrorHandler
from sanic.response import json, HTTPResponse
from sanic_session import Session, AIORedisSessionInterface

from cat_and_dog.config.log_config import logconfig_dict, error_logger
from cat_and_dog.modules import db
from cat_and_dog.modules.auth import auth_bp, login_manager
from cat_and_dog.modules.product import product_bp
from cat_and_dog.modules.public import public_bp
from cat_and_dog.utils.errors.exceptions import SchemaException, ApiException
from cat_and_dog.utils.request.request import MyRequest
from .config import log_config, dev, pro


class Sanic(_Sanic):
    async def send_signal(self, signal_name, *args, **kwargs):
        res = list()
        handle_list = self.listeners.get(signal_name)
        for handler in handle_list:
            result = handler(self, *args, **kwargs)
            if isawaitable(result):
                result = await result
            res.append((handler, result))
        return res


def set_session(app: Sanic):
    @app.listener('before_server_start')
    async def server_init(app, loop):
        app.redis = await aioredis.create_redis_pool(app.config["REDIS"], loop=loop, db=15)
        Session(app, interface=AIORedisSessionInterface(app.redis))

    @app.listener("my_signal")
    async def signal(sender, data):
        print(data)
        print("1111111")
        return None


def register_bp(app: Sanic) -> None:
    app.blueprint([product_bp, auth_bp, public_bp])


def error_handle(app: Sanic):
    handler = ErrorHandler()

    handler.add(
        ValidationError, lambda r, e: json({"message": str(e.messages)}, status=400)
    )
    handler.add(
        SanicException, lambda r, e: json({"message": e.__str__()}, status=e.status_code)
    )
    handler.add(
        SchemaException, lambda r, e: json({"message": e.__str__()}, 400)
    )
    handler.add(
        ApiException, lambda r, e: json({"message": e.msg}, status=e.code)
    )
    handler.add(
        PostgresError, lambda r, e: json({"message": e.__str__()}, status=500)
    )

    def handler_exception(r, e):
        error_logger.exception(e)
        return json({"message": e.__str__()}, status=500)

    handler.add(
        Exception, handler_exception
    )

    app.error_handler = handler


def middleware(app: Sanic):
    @app.middleware("response")
    async def format_data(_, response):
        if 200 <= response.status < 300 and getattr(response, 'content_type', None) == "application/json":
            data = f'{{"message": "ok", "data": {response.body.decode()} }}'
            response.body = data.encode()


def create_app(mode: str) -> Sanic:
    if mode == "dev":
        app = Sanic(__name__, log_config={}, request_class=MyRequest)
        app.config.from_object(dev)
        app.static('/static', './static')
    else:
        app = Sanic(__name__, request_class=MyRequest, log_config=logconfig_dict)
        app.config.from_object(pro)

    # session
    set_session(app)

    # 登录
    login_manager.init_app(app)

    # 关联db
    db.init_app(app)

    # 注册蓝图
    register_bp(app)

    # 处理异常
    error_handle(app)

    # 中间件
    middleware(app)

    @app.route("/signal")
    async def send_a_signal(request: MyRequest):
        a = await request.app.send_signal("my_signal", request)
        print(a)
        return HTTPResponse("Signal Sent")
        pass

    @app.route("/")
    async def wait_a_minute(request):
        # import asyncio
        # await asyncio.sleep(1)
        # request.session["user_id"] = 1
        from async_task.tasks.test import a
        a.delay(1, 2)
        return HTTPResponse("123")

    @app.route("/login")
    async def login(request):
        from cat_and_dog.modules.users.models import User
        request.login(
            await User.get(1)
        )
        return HTTPResponse(1)

    @app.route("/logout")
    async def logout(request):
        # from cat_and_dog.modules.users.models import User
        request.logout()
        return HTTPResponse(1)

    @app.websocket('/feed')
    async def feed(request, ws):
        while True:
            print(ws)
            data = 'hello!'
            print('Sending: ' + data)
            await ws.send(data)
            data = await ws.recv()
            # 有些recv返回None表示连接断开
            if data is None:
                # print(f"lose connection with {request.url}")
                break
            print('Received: ' + data)
        await ws.close()

    return app
