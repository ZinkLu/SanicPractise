from sanic.response import json
from sanic.views import HTTPMethodView

from cat_and_dog.modules.auth.schema import AdminLogInSchema
from cat_and_dog.modules.users.schema import UserDetailSchema


class Auth(HTTPMethodView):
    async def get(self, request):
        """登出"""
        request.logout()
        return json({})

    async def post(self, request):
        """登录"""
        user_load_schema = AdminLogInSchema(strict=True)
        user, error = await user_load_schema.async_load(request.json)
        request.login(user)  # 使用login_user状态保持

        user_dump_schema = UserDetailSchema()
        user_info = user_dump_schema.dump(user).data

        return json(user_info)
