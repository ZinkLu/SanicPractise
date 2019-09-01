from marshmallow import fields

from cat_and_dog.utils.async_schema.mixins import ListMixin, DetailMixIn, CountMixIn, PreLoadListMixin
from .models import Brand
from ..goods.models import Spu
from ... import BaseSchema


class BrandBase(BaseSchema):
    __model__ = Brand
    name = fields.String(query="like")


class BrandListSchema(PreLoadListMixin, ListMixin, BrandBase):
    pass


class BrandCountSchema(PreLoadListMixin, CountMixIn, BrandBase):
    pass


class BrandDetailSchema(DetailMixIn, BrandBase):
    id = fields.Integer(key_check=True,
                        model=Brand)

    spus_ids = fields.List(fields.Integer(),
                           load_only=True,
                           key_check=True,
                           model=Spu,
                           fk="brand_id")

    name = fields.String(required=True)

    # dump_only
    spus = fields.Nested("SpuDetailSchema", only=("id", "name"), many=True, dump_only=True)
