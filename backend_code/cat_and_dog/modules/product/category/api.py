# -*- coding: utf-8 -*-
from sanic.response import json
from sanic.views import HTTPMethodView

from cat_and_dog import db
from cat_and_dog.utils.errors.status_code import UPDATE_OK
from cat_and_dog.utils.login.tools import admin_required
from .schema import CateListSchema, CateDetailSchema, CateCountSchema
from .models import Categories as ModelCategories


class Categories(HTTPMethodView):
    async def get(self, request):
        """获取分类列表"""
        schema = CateListSchema(strict=True)
        instance_list, error = await schema.async_load(request.single_args)
        data, error = await schema.async_dump(instance_list, many=True)
        return json(data)

    @admin_required
    async def post(self, request):
        """创建分类"""
        schema = CateDetailSchema(strict=True)
        instance = (await schema.async_load(request.json)).data
        data, error = await schema.async_dump(instance)
        return json(data)


class Category(HTTPMethodView):
    # @admin_required
    async def get(self, request, pk: int):
        """获取分类详情"""
        schema = CateDetailSchema()
        instance = await ModelCategories.get_or_404(pk)
        data, error = await schema.async_dump(instance)
        return json(data)

    @admin_required
    async def delete(self, request, pk: int):
        """删除分类"""
        async with db.auto_commit():
            # await ModelCategories.get(pk)
            res = await ModelCategories.delete.where(ModelCategories.id == pk).gino.status()

        return json({"res": res[0]})

    @admin_required
    async def put(self, request, pk: int):
        """更新分类"""
        schema = CateDetailSchema(strict=True, partial=True)
        data = request.json
        data['id'] = pk
        instance = (await schema.async_load(data)).data
        data, error = await schema.async_dump(instance)
        return json(data, status=UPDATE_OK)


class CountForCategories(HTTPMethodView):
    async def get(self, request):
        schema = CateCountSchema(strict=True)
        count, error = await schema.async_load(request.single_args)
        return json({"count": count})
