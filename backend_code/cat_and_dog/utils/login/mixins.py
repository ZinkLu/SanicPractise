# -*- coding: utf-8 -*-


class UserMixin:
    @property
    def is_ambiguous(self):
        return False

    @property
    def is_active(self):
        return True

    @property
    def is_authorized(self):
        return True


class AmbiguousUser:
    @property
    def is_ambiguous(self):
        return True

    @property
    def is_active(self):
        return False

    @property
    def is_authorized(self):
        return False

    @property
    def is_admin(self):
        return False
