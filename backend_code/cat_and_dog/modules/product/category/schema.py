from marshmallow.fields import *

from cat_and_dog.utils.errors.exceptions import SchemaException
from cat_and_dog.modules.product.goods.models import Spu
from cat_and_dog.utils.async_schema.process import async_post_load, async_validates_schema
from .models import Categories
from ... import BaseSchema
from cat_and_dog.utils.async_schema.mixins import ListMixin, DetailMixIn, CountMixIn
from ....utils.empty import Empty


class CateBase(BaseSchema):
    __model__ = Categories

    # load_only
    id = Integer(dump_only=True, eq=True)
    name = String(query="like")
    parent_id = Integer(load_only=True, query="eq")


class CateListSchema(ListMixin, CateBase):
    # dump_only
    children_nums = Integer(dump_only=True)

    @async_post_load
    async def make_queries(self, data: dict):
        if data.get("parent_id", Empty) is not Empty:
            data["parent_id"] = data["parent_id"] or None
        # 添加children_nums
        res = await super().make_queries(data)
        for r in res:
            setattr(
                r, "children_nums", await r.count_child()
            )
        return res


class CateCountSchema(CountMixIn, CateBase):

    @async_post_load
    async def count(self, data):
        if data.get("parent_id", Empty) is not Empty:
            data["parent_id"] = data["parent_id"] or None
        return await super().count(data)


class CateDetailSchema(DetailMixIn, CateBase):
    # load_only
    id = Integer(key_check=True, model=Categories)
    # 不再进行外键检查, 因为在check_circular_reference方法中已经验证
    parent_id = Integer(load_only=True)
    spus_ids = List(Integer(),
                    load_only=True,
                    key_check=True,
                    model=Spu,
                    fk="category_id")

    # dump
    name = String(required=True)

    # relations
    parent = Nested("self", only=("id", "name"), dump_only=True)
    children = Nested("self", only=("id", "name"), many=True, dump_only=True)

    @async_validates_schema
    async def check_circular_reference(self, data):
        """无法将已有子类设置为父类"""
        new_parent_id = data.get("parent_id")
        instance_id = data.get("id")
        if new_parent_id and instance_id:
            if new_parent_id == instance_id:
                raise SchemaException("无法将子类设置为自己")
            parent_instance = await self.__model__.get(new_parent_id)
            if not parent_instance:
                raise SchemaException("未找到对应的父类")
            this_instance = await self.__model__.get(instance_id)

            await self.check_parent(this_instance, parent_instance)

    @staticmethod
    async def check_parent(this_instance, parent_instance):
        """
        检查是否存在循环引用的情况
        :param this_instance: 需要更新的模型对象
        :param parent_instance: `this_instance` 即将设置的parent_instance
        :return:
        """
        while await parent_instance.parent:
            parent_instance = await parent_instance.parent
            if parent_instance.id == this_instance.id:
                raise SchemaException("无法将已有子类设置为父类")
