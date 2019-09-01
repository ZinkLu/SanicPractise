from marshmallow import fields

from cat_and_dog.utils.async_schema.schema import Schema


class UserDetailSchema(Schema):
    nick_name = fields.String()
    # password_hash = fields.String()
    mobile = fields.String()
    avatar_url = fields.String()
    last_login = fields.DateTime()
    is_admin = fields.Boolean()
    signature = fields.String()
    gender = fields.String()
