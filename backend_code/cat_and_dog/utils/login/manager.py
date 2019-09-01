# -*- coding: utf-8 -*-
from cat_and_dog.utils.login.loginRequest import LoginRequest
from .mixins import AmbiguousUser


class LoginManager:
    def __init__(self, app=None):
        self.user_callback = None
        self.ambiguous_class = AmbiguousUser
        if app:
            self.init_app(app)

    def init_app(self, app):
        # replace the request class
        origin = app.request_class
        login_class = type("LoginClass",
                           (origin, LoginRequest),
                           {"login_manager": self})

        app.request_class = login_class

        # the hook must register `after` session
        # Sanic-Session will not `appendleft` the session function
        # into the request_middleware until the app has been fully inited.
        app.request_middleware.appendleft(self.get_current_user)

    def user_loader(self, callback):
        """callback is an async function"""
        self.user_callback = callback
        return callback

    @staticmethod
    async def get_current_user(request):
        """load user, make request.user available;
        consider CACHE?
        """
        await request.load_user()
