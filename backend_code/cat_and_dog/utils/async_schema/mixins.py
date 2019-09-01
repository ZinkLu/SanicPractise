# -*- coding: utf-8 -*-
import asyncio
from functools import reduce
from inspect import isawaitable
from typing import *

from marshmallow import fields
from sqlalchemy import and_

from cat_and_dog.modules import Base, db
from cat_and_dog.utils.async_schema.process import (async_post_load, async_validates_schema, async_pre_load,
                                                    async_pre_dump)
from cat_and_dog.utils.empty import Empty
from cat_and_dog.utils.errors.exceptions import SchemaException


class MixInBase:
    __model__: Base

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.query_fields = [fi for fn, fi in self.fields.items()
                             if "query" in fi.metadata]

        self.dump_field_name = {field_name for field_name, field_obj in self.fields.items() if
                                not getattr(field_obj, 'load_only', False)}

    def fields_to_queries(self, field_value: Dict[fields.Field, Any]):
        """
        override this method to modify the queries
        the origin method will combine all `query` field
        with `and` expression

        - example:

            ```python
            class FooListSchema(PreLoadListMixin, ListMixin):
                __model__ = FooModel

                name = fields.String(query="like")
                code = fields.String(query="like)

            # the query will be
            # SELECT * FROM foo_model WHERE name like '%$1%' AND code like '%$2%'


            # override the method
            class FooListSchemaMod(FooListSchema):
                def fields_to_queries(self, field_value):
                    copy_value = field_value.copy()
                    ext_query = True
                    name_field = self.fields["name"]
                    if name_field in field_value:
                        ext_query = or_(self.__model__.code.like(f"%{field_value[name_field]}%"),
                                        self.__model__.name.like(f"%{field_value[name_field]}%"))
                        copy_value.pop(name_field)

                    # it's OK to combine your query with origin query with and_
                    queries = super().fields_to_queries(copy_value)
                    return and_(queries, ext_query)

            # the query will be
            # SELECT * FROM foo_model WHERE like '%$1%' OR code like '%$2%'
            ```

        :param field_value:
            {
                field_object: value  # type: Field field_object
            }
            field_object.name
            field_object.metadata
            ...
        :return: queries
        """
        model = self.__model__
        query_list = list()

        for field, field_value in field_value.items():

            if field.metadata.get("query") == "like":
                query_list.append(
                    getattr(model, field.name).like(f"%{field_value}%")
                )
            elif field.metadata.get("query") == "eq":
                if isinstance(field, fields.List):
                    query_list.append(
                        getattr(model, field.name).in_(field_value)
                    )
                else:
                    query_list.append(
                        getattr(model, field.name) == field_value
                    )
        return reduce(and_, query_list) if query_list else True

    def _to_queries(self, data):
        if not self.__model__:
            return data

        real_query_field = {field_info: data.get(field_info.name)
                            for field_info in self.query_fields
                            if data.get(field_info.name, Empty) is not Empty}

        queries = self.fields_to_queries(real_query_field)
        return queries

    async def dump_which_relation(self, instance):
        """
        为了不全量加载relation 属性, 判断目前的schema中有没有需要dump的字段
        :param instance:
        :return:
        """
        to_dump = instance.__rel__ & self.dump_field_name
        # print(to_dump)
        for d in to_dump:
            _d = getattr(instance, d)
            if isawaitable(_d):
                await _d

    @async_pre_dump
    async def await_for_relation(self, data: Awaitable or List):
        """await for the instance relationship, load了所有的关系, 因此性能八太好, 应该判断当前schema需要dump的字段"""

        # 获取当前schema需要dump的字段

        # await这个字段, i.e. 加载一个关系属性
        if isinstance(data, list):
            return await asyncio.wait([self.dump_which_relation(d) for d in data])
        return await self.dump_which_relation(data)


class PreLoadListMixin:
    """
    该MixIn可以将查询字符串中以逗号分隔的字符串转变为列表, 如:
    ?cate=1,2,3 查询分类id为1,2,3下面的spu
    sql 为 cate IN (1,2,3)
    """

    @async_pre_load
    async def split_into_list(self, data: Dict[AnyStr, Any]) -> Dict[AnyStr, Any]:
        """
        自动转化所有Str to ListField
        :param data
        :return:
        """
        data = data.copy()
        fs = self.fields
        list_fields = [k for k, v in fs.items() if isinstance(v, fields.List)]
        for l in list_fields:
            if data.get(l):
                data[l] = data[l].split(",")
        return data


class ListMixin(MixInBase):
    """
    检查分页, mixin应该放在ma.ModelSchema之前
    """

    limit = fields.Integer(load_only=True)
    offset = fields.Integer(load_only=True)
    page = fields.Integer(load_only=True)
    per_page = fields.Integer(load_only=True)

    @async_validates_schema
    async def validate_for_pagination(self, data: dict):
        """验证limit和offset或者page/per_page"""
        limit = data.get("limit")
        offset = data.get("offset")
        page = data.get("page")
        per_page = data.get("per_page")

        if not any((limit is None, offset is None)):
            # limit/offset必须一起传入
            if any((limit < 1, offset < 0)):
                raise SchemaException("limit/offset必须大于0")
            return

        if not any((page is None, per_page is None)):
            # page/per_page必须一起传入
            if any((page < 1, per_page < 1)):
                raise SchemaException("page/per_page必须大于0")
            return

        raise SchemaException("分页信息错误, 必须提供limit/offset或者page/per_page")

    @async_post_load
    async def convert_page_to_limit(self, data: dict):
        """将page转换成limit"""
        if data.get("page"):
            limit = data["per_page"]
            offset = data["per_page"] * (data["page"] - 1)
            data["limit"] = limit
            data["offset"] = offset
        return data

    @async_post_load
    async def make_queries(self, data: dict):
        """
        ~将查询字符串转换为instance~
        :param data:
        :return:
        """
        query = self._to_queries(data)
        return await self.__model__.query.where(query).limit(data["limit"]).offset(data["offset"]).gino.all()


class DetailMixIn(MixInBase):
    """
    提供了外键的验证, 并且在返回实例的时候会将多对一的关联给改掉
    一般用于post或者put方法, 修改模型时

    **特别说明**:
        - `key_check`则是用来检查外键是否合法, 而`fk`参数是用来创建/修改关联(更新表数据)

            - key_check: `SELECT id FROM one WHERE id = $1 `

            - fk: UPDATE `many SET fk = $1 WHERE many.id IN ($2)`
    """

    __relations__: Dict[str, Tuple[Base, List[int]]] = dict()

    @staticmethod
    async def check_foreign_exits(model: Base, pk: int or list) -> None or List:
        """
        检查外键是否存在
        :param Base model: 关联外键的模型
        :param pk: 外键/主键
        :return: None or List
        """
        if pk is None:
            return
        if isinstance(pk, int):
            if pk <= 0 or (not await model.get(pk)):
                raise SchemaException("找不到对应的外键或主键")
        elif isinstance(pk, list) and pk:
            pk = tuple(pk)
            relations = await model.select("id").where(model.id.in_(pk)).gino.all()
            if len(relations) != len(pk):
                raise SchemaException("找不到对应的外键或主键")
            return [r[0] for r in relations]

    @async_post_load
    async def if_foreign_exist(self, data: dict):
        """自动判断外键是否存在"""
        check_fields = {f: v for f, v in self.fields.items() if data.get(f) and "key_check" in v.metadata}

        for field_name, field in check_fields.items():
            relations = await self.check_foreign_exits(field.metadata["model"], data.get(field_name))

            if relations:
                # 记录下查询到的fk值, 避免更新/创建时再次查询
                # 作为`一`的一方, 本身是不包含任何外键信息的, 因此data中将外键list剔除
                data.pop(field_name)
                self.__relations__[field.metadata["fk"]] = (field.metadata["model"], relations)
        return data

    @async_post_load
    async def make_instance(self, data: dict):
        """创建instance, 关联relations, 如果是不需要创建或者修改可以直接返回data
        `fk`用于在这里创建关联
        """
        async with db.auto_commit():
            if data.get("id"):
                # update
                _id = data.pop("id")
                instance = await self.__model__.get(_id)
                await instance.update(**data).apply()
            else:
                # create
                instance = await self.__model__.create(**data)

            _id = instance.id

            for fk, (model, ids) in self.__relations__.items():
                # update the many side, the the fk to the instance id
                # this is like
                # update model set model.fk = $1 where model.id in (ids) -- $1 is the one side we just create or update
                await model.update.values(**{fk: _id}).where(model.id.in_(ids)).gino.status()

        instance.init_the_relation()
        return instance


class CountMixIn(MixInBase):
    @async_post_load
    async def count(self, data):
        query = self._to_queries(data)
        count = await db.select([db.func.count()]).select_from(self.__model__).where(query).gino.status()
        return count[1][0].values()[0]
