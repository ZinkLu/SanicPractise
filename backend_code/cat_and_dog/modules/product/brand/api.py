from sanic.response import json
from sanic.views import HTTPMethodView

from cat_and_dog import db
from cat_and_dog.utils.errors.status_code import UPDATE_OK
from cat_and_dog.utils.login.tools import admin_required
from .schema import BrandListSchema, BrandDetailSchema, BrandCountSchema
from .models import Brand as ModelBrand


class Brands(HTTPMethodView):
    async def get(self, request):
        """获取品牌列表"""
        schema = BrandListSchema(strict=True)
        instance_list, error = await schema.async_load(request.single_args)
        data, error = await schema.async_dump(instance_list, many=True)
        return json(data)

    @admin_required
    async def post(self, request):
        """创建品牌"""
        schema = BrandDetailSchema(strict=True)
        instance = (await schema.async_load(request.json)).data
        data, error = await schema.async_dump(instance)
        return json(data)


class Brand(HTTPMethodView):
    async def get(self, request, pk: int):
        """获取品牌详情"""
        schema = BrandDetailSchema()
        instance = await ModelBrand.get_or_404(pk)
        data, error = await schema.async_dump(instance)
        return json(data)

    @admin_required
    async def delete(self, request, pk: int):
        """删除品牌"""
        async with db.auto_commit():
            # await ModelCategories.get(pk)
            res = await ModelBrand.delete.where(ModelBrand.id == pk).gino.status()

        return json({"res": res[0]})

    @admin_required
    async def put(self, request, pk: int):
        """更新品牌"""
        schema = BrandDetailSchema(strict=True, partial=True)
        data = request.json
        data['id'] = pk
        instance = (await schema.async_load(data)).data
        data, error = await schema.async_dump(instance)
        return json(data, status=UPDATE_OK)


class BrandCount(HTTPMethodView):
    async def get(self, request):
        schema = BrandCountSchema(strict=True)
        count, error = await schema.async_load(request.single_args)
        return json({"count": count})
