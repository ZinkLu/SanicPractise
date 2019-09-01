from sanic.response import json
from sanic.views import HTTPMethodView

from cat_and_dog import db
from cat_and_dog.utils.errors.status_code import UPDATE_OK
from cat_and_dog.utils.login.tools import admin_required
from .models import Spu as ModelSpu, Sku as ModelSku
from .schema import SpuCountSchema, SpuDetailSchema, SpuListSchema, SkuListSchema, SkuCountSchema, SkuDetailSchema


class Spus(HTTPMethodView):
    async def get(self, request):
        """获取SPU列表"""
        schema = SpuListSchema(strict=True)
        instance_list, error = await schema.async_load(request.single_args)
        data, error = await schema.async_dump(instance_list, many=True)
        return json(data)

    @admin_required
    async def post(self, request):
        """创建SPU"""
        schema = SpuDetailSchema(strict=True)
        instance = (await schema.async_load(request.json)).data
        data, error = await schema.async_dump(instance)
        return json(data)


class Spu(HTTPMethodView):
    async def get(self, request, pk: int):
        """获取SPU详情"""
        schema = SpuDetailSchema()
        instance = await ModelSpu.get_or_404(pk)
        data, error = await schema.async_dump(instance)
        return json(data)

    @admin_required
    async def delete(self, request, pk: int):
        """删除SPU"""
        async with db.auto_commit():
            # await ModelCategories.get(pk)
            res = await ModelSpu.delete.where(ModelSpu.id == pk).gino.status()

        return json({"res": res[0]})

    @admin_required
    async def put(self, request, pk: int):
        """更新SPU"""
        schema = SpuDetailSchema(strict=True, partial=True)
        data = request.json
        data['id'] = pk
        instance = (await schema.async_load(data)).data
        data, error = await schema.async_dump(instance)
        return json(data, status=UPDATE_OK)


class SpusCount(HTTPMethodView):
    async def get(self, request):
        schema = SpuCountSchema(strict=True)
        count, error = await schema.async_load(request.single_args)
        return json({"count": count})


class Skus(HTTPMethodView):
    async def get(self, request):
        """获取Sku列表"""
        # breakpoint()
        schema = SkuListSchema(strict=True)
        instance_list, error = await schema.async_load(request.single_args)
        data, error = await schema.async_dump(instance_list, many=True)
        return json(data)

    @admin_required
    async def post(self, request):
        """创建Sku"""
        schema = SkuDetailSchema()
        instance, error = await schema.async_load(request.single_args)
        data, error = await schema.async_load(instance)
        return json(data)


class Sku(HTTPMethodView):
    async def get(self, request, pk: int):
        """SKU详情"""
        schema = SkuDetailSchema()
        instance = await ModelSku.get_or_404(pk)
        data, error = await schema.async_dump(instance)
        return json(data)

    @admin_required
    async def put(self, request):
        pass

    @admin_required
    async def delete(self, request, pk: int):
        async with db.auto_commit():
            res = await ModelSku.delete.where(ModelSpu.id == pk).gino.status()
        return json({"res": res[0]})


class SkusCount(HTTPMethodView):
    async def get(self, request):
        schema = SkuCountSchema(strict=True)
        count, error = await schema.async_load(request.single_args)
        return json({"count": count})
