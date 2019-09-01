# -*- coding: utf-8 -*-

from sqlalchemy import *

from cat_and_dog.modules import RecordingMixin, Base
from cat_and_dog.utils.relations.orm_relations import one2many, many2one


class Spu(RecordingMixin, Base):
    """Spu表, 表示一类商品
    iPhone6
    """
    __tablename__ = "spu"

    name = Column(String(255), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"), nullable=True, index=True)
    information = Column(Text)

    # skus = relationship("Sku", backref="spu", lazy="dynamic")
    # options = relationship("ProductSpecificationOptions", backref="spu", lazy="dynamic")
    skus = one2many("Sku")
    options = one2many("ProductSpecificationOptions")

    category = many2one("Categories")
    brand = many2one("Brand")


class Sku(RecordingMixin, Base):
    """Sku表, 表示一个商品
    iPhone 6 16g 红色 xx
    """
    __tablename__ = "sku"

    name = Column(String(255), nullable=False, index=True)
    code = Column(String(30), index=True, nullable=False, unique=True)
    price = Column(Float(2))
    purchase_price = Column(Float(2, decimal_return_scale=True))
    spu_id = Column(Integer, ForeignKey("spu.id", ondelete="CASCADE"), nullable=True, index=True)

    spu = many2one("Spu")


class ProductSpecificationOptions(RecordingMixin, Base):
    """
    商品规格, 一个SPU应该有多个规格
    """
    __tablename__ = "product_specification_options"

    spu_id = Column(Integer, ForeignKey("spu.id", ondelete="CASCADE"), nullable=True, index=True)
    option_name = Column(String(50))

    # values = relationship("ProductSpecificationValues", backref="option", lazy="dynamic")


class ProductSpecificationValues(RecordingMixin, Base):
    """
    商品规格值, 该值应该关联到某一个规格
    """
    __tablename__ = "product_specification_values"

    option_id = Column(Integer, ForeignKey("product_specification_options.id", ondelete="CASCADE"),
                       nullable=True, index=True)
    value_name = Column(String(50))


class ProductSpecification(Base):
    __tablename__ = "product_specifications"
    sku_id = Column(Integer, ForeignKey("sku.id"), index=True)
    option_id = Column(Integer, ForeignKey("product_specification_options.id"), index=True)
    value_id = Column(Integer, ForeignKey("product_specification_values.id"), index=True)
