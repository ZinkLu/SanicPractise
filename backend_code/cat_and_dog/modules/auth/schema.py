from marshmallow import fields

from cat_and_dog.utils.async_schema.process import async_post_load
from cat_and_dog.utils.errors.exceptions import LOGIN_ERROR
from ..users.models import User

from cat_and_dog.utils.async_schema.schema import Schema


class AdminLogInSchema(Schema):
    mobile = fields.String(required=True)
    password = fields.String(required=True)

    @async_post_load
    async def login_as(self, data):
        """登录成功返回用户的实例"""
        user = await User.query.where(User.mobile == data['mobile']).gino.first()
        if not user or not await user.check_pwd(data['password']):
            raise LOGIN_ERROR
        return user
