# -*- coding: utf-8 -*-


class LoginRequest:
    """the login request
    """
    _user = None
    login_manager: 'LoginManager'

    async def load_user(self):
        """every time the request"""
        if self.login_manager.user_callback is None:
            raise Exception("set the `user_loader` first")

        user = self.login_manager.ambiguous_class
        if self._user is None:
            user_id = self.session.get("user_id")
            if user_id:
                user = await self.login_manager.user_callback(user_id)

        self._user = self.login_manager.ambiguous_class() if user is self.login_manager.ambiguous_class else user
        return self._user

    @property
    def user(self):
        """实现request的User"""
        if self._user is None:
            assert "must await `load_user` before access to user"
        return self._user

    @property
    def session(self):
        return self["session"]

    def login(self, user):
        self.session["user_id"] = user.id

    def logout(self):
        user = self.user
        if user.is_ambiguous:
            return
        try:
            self.session.pop("user_id")
        except KeyError:
            pass
