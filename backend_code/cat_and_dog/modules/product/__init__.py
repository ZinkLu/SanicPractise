from sanic import Blueprint

from .brand.api import Brand, BrandCount, Brands
from .category.api import Categories, Category, CountForCategories
from .goods.api import Spus, SpusCount, Spu, Skus, SkusCount, Sku
from ..api_version import api_prefix

product_bp = Blueprint("product", url_prefix=api_prefix)

product_bp.add_route(Categories.as_view(), "categories")
product_bp.add_route(CountForCategories.as_view(), "categories/count")
product_bp.add_route(Category.as_view(), "category/<pk:int>")

product_bp.add_route(Spus.as_view(), "products")
product_bp.add_route(SpusCount.as_view(), "products/count")
product_bp.add_route(Spu.as_view(), "product/<pk:int>")

product_bp.add_route(Brands.as_view(), "brands")
product_bp.add_route(BrandCount.as_view(), "brands/count")
product_bp.add_route(Brand.as_view(), "brand/<pk:int>")

product_bp.add_route(Skus.as_view(), "skus")
product_bp.add_route(Sku.as_view(), "sku/<pk:int>")
product_bp.add_route(SkusCount.as_view(), "skus/count")
