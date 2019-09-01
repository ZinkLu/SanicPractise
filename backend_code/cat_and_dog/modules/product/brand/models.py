# -*- coding: utf-8 -*-

from sqlalchemy import *
# from sqlalchemy.orm import relationship

from cat_and_dog.modules import Base, RecordingMixin
from cat_and_dog.utils.relations.orm_relations import one2many


class Brand(RecordingMixin, Base):
    """商品品牌表, 一个品牌有多个Spu
    苹果, 华为, 小米
    """
    __tablename__ = "brands"

    name = Column(String(255), index=True, nullable=False, unique=True)
    # spus = relationship("Spu", backref="brand", lazy="dynamic")

    spus = one2many("Spu")
