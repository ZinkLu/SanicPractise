# -*- coding: utf-8 -*-
import functools

from sanic.exceptions import abort


def login_validator(validator):
    def method_compact(wrapper):
        @functools.wraps(wrapper)
        async def method_wrapper(self, request, *args, **kwargs):
            validator(request)
            return await wrapper(self, request, *args, **kwargs)

        @functools.wraps(wrapper)
        async def function_wrapper(request, *args, **kwargs):
            validator(request)
            return await wrapper(request, *args, **kwargs)

        if "." in wrapper.__qualname__:  # `.` means a inner-class function
            return method_wrapper

        return function_wrapper

    return method_compact


@login_validator
def login_required(request):
    user = request.user
    if not all((not user.is_ambiguous, user.is_active, user.is_authorized)):
        abort(401, "Please login to access this api")


@login_validator
def admin_required(request):
    user = request.user
    if not all((not user.is_ambiguous, user.is_active, user.is_authorized, user.is_admin)):
        abort(401, "Admin is required to this api")
