from marshmallow import fields
from sqlalchemy import or_, and_

from cat_and_dog.utils.async_schema.mixins import ListMixin, DetailMixIn, CountMixIn, PreLoadListMixin
from .models import Spu, Sku, ProductSpecificationOptions
from ..brand.models import Brand
from ..category.models import Categories
from ... import BaseSchema


class SpuBase(BaseSchema):
    __model__ = Spu
    name = fields.String(query="like")
    category_id = fields.List(fields.Integer(), load_only=True, query="eq")
    brand_id = fields.List(fields.Integer(), load_only=True, query="eq")


class SpuListSchema(PreLoadListMixin, ListMixin, SpuBase):
    pass


class SpuCountSchema(PreLoadListMixin, CountMixIn, SpuBase):
    pass


class SpuDetailSchema(DetailMixIn, SpuBase):
    id = fields.Integer(key_check=True,
                        model=Spu)

    # load_only
    category_id = fields.Integer(load_only=True,
                                 key_check=True,
                                 model=Categories)
    brand_id = fields.Integer(load_only=True,
                              key_check=True,
                              model=Brand)
    options_ids = fields.List(fields.Integer(),
                              load_only=True,
                              key_check=True,
                              model=ProductSpecificationOptions,
                              fk="spu_id")
    skus_ids = fields.List(fields.Integer(),
                           load_only=True,
                           key_check=True,
                           model=Sku,
                           fk="spu_id")

    name = fields.String(required=True)
    information = fields.String()

    # dump_only
    skus = fields.Nested("SkuDetailSchema", only=("id", "name"), many=True, dump_only=True)
    # options
    category = fields.Nested("CateDetailSchema", only=("id", "name"), dump_only=True)
    brand = fields.Nested("BrandDetailSchema", only=("id", "name"), dump_only=True)


class SkuBase(BaseSchema):
    __model__ = Sku
    name = fields.String(query="like")
    spu_id = fields.List(fields.Integer(), load_only=True, query="eq")


class SkuListMixin(ListMixin):
    def fields_to_queries(self, field_value):
        """使得获取列表时name可以和code混合查询"""
        copy_value = field_value.copy()
        ext_query = True
        name_field = self.fields["name"]
        if name_field in field_value:
            value = field_value[name_field]
            ext_query = or_(self.__model__.code.like(f"%{value}%"), self.__model__.name.like(f"%{value}%"))
            copy_value.pop(name_field)

        queries = super().fields_to_queries(copy_value)

        return and_(queries, ext_query)


class SkuListSchema(PreLoadListMixin, SkuListMixin, SkuBase):
    pass


class SkuCountSchema(PreLoadListMixin, SkuListMixin, SkuBase):
    pass


class SkuDetailSchema(DetailMixIn, SkuBase):
    name = fields.Str(required=True)
    code = fields.Str(required=True)
    price = fields.Float(required=True)
    purchase_price = fields.Float(required=True)

    id = fields.Integer(key_check=True,
                        model=Sku)

    spu_id = fields.Integer(load_only=True,
                            key_check=True,
                            model=Spu)

    spu = fields.Nested("SpuDetailSchema", dump_only=True)
