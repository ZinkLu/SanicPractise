# -*- coding: utf-8 -*-

from sqlalchemy import *

from cat_and_dog.modules import Base, db, RecordingMixin
from cat_and_dog.utils.relations.orm_relations import many2one, one2many


class Categories(RecordingMixin, Base):
    """商品分类表, 一个Spu应该属于某个分类
    一级分类:
    二级分类:
    三级分类:  -> 商品对应的分类
    """
    __tablename__ = "categories"

    parent_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), index=True)
    name = Column(String(50), nullable=False)

    # relations
    parent = many2one("Categories")
    children = one2many("Categories")

    async def count_child(self):
        return await db.scalar("SELECT COUNT(*) FROM categories where parent_id = $1", self.id)
