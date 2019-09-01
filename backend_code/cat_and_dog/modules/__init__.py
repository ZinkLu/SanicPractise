from contextlib import asynccontextmanager
from datetime import datetime

import ujson
from gino.ext.sanic import Gino as _Gino
from marshmallow import fields
from sqlalchemy import *

from cat_and_dog.utils.async_schema.schema import Schema
from cat_and_dog.utils.relations.orm_relations import setup_base


class Gino(_Gino):
    @asynccontextmanager
    async def auto_commit(self):
        async with self.transaction() as tx:
            try:
                yield
                await tx.raise_commit()
            except Exception as e:
                try:
                    await tx.rollback()
                except AssertionError:
                    pass
                raise e


db = Gino()


@setup_base
class Base(db.Model):
    # 这是一个基类表, 不需要创建实体表
    __abstract__ = True

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)


class RecordingMixin:
    # 表示状态, 商品是否上架, 用户是否激活等
    status = Column(SmallInteger, default=1, doc='表示状态, 商品是否上架, 用户是否激活等, 1表示启用, 0表示未启用')
    create_time = Column(DateTime, default=datetime.now)  # 记录的创建时间
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 记录的更新时间


class BaseSchema(Schema):
    class Meta:
        render_module = ujson
        strict = True

    id = fields.Integer(key_check=True)
    name = fields.String()
    status = fields.Integer()
    update_time = fields.DateTime(dump_only=True)
    create_time = fields.DateTime(dump_only=True)
