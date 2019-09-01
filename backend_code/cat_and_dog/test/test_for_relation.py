# -*- coding: utf-8 -*-

import uvloop
from asyncpg import connect
from gino import Gino
from sqlalchemy import *

from cat_and_dog.utils.relations.orm_relations import one2many, setup_base, many2one, many2many

DATABASE_URL = "postgresql://localhost/test_for_relation"

db = Gino()


@setup_base
class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


class Parent(Base):
    __tablename__ = "test_parent"

    name = Column(String(255), nullable=False, index=True)

    children = one2many('Children')
    favorites = many2many("ParentFavorite", "ParentFavoriteRel")


class Children(Base):
    __tablename__ = "test_children"
    name = Column(String(255), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey('test_parent.id'))

    parent = many2one('Parent')


class ParentFavorite(Base):
    __tablename__ = "test_favorite"

    name = Column(String(255), nullable=False, index=True)


class ParentFavoriteRel(Base):
    __tablename__ = "parent_favorite_rel"
    parent_id = Column(Integer, ForeignKey("test_parent.id"), index=True)
    favorite_id = Column(Integer, ForeignKey("test_favorite.id"), index=True)


uvloop.install()


async def connect_with_gino():
    await db.set_bind(DATABASE_URL)


async def make_record():
    await db.gino.create_all()
    instance = await Parent.create(name="parent1", )
    favorite = await ParentFavorite.create(name="fav1")

    _id = instance.id

    await ParentFavoriteRel.create(
        parent_id=_id,
        favorite_id=favorite.id
    )

    for _ in range(10):
        await Children.create(name=f"parent_{_}", parent_id=_id)

    return _id


async def test_start():
    conn = await connect(host="localhost", database="postgres")
    res = await conn.fetchrow("select count(*) from pg_database where datname = 'test_for_relation'")
    count = res.get("count")
    if not count:
        await conn.execute("CREATE database test_for_relation")
    await conn.close()

    if not count:
        await connect_with_gino()
        await make_record()


async def test_wait_all_relations():
    await connect_with_gino()
    parent = await Parent.query.where(Parent.name == "parent1").gino.first()
    print(parent.children)
    print(parent.favorites)
    await parent
    print(parent.children)

    no1 = parent.children[0]

    assert isinstance(no1, Children)

    print(await no1.parent)
    print("The name of no1's parent is ", no1.parent.name)

    print(parent.favorites)
    assert isinstance(parent.children.children, list)


# @pytest.mark.asyncio
async def test_wait_one_relation():
    await connect_with_gino()
    parent = await Parent.query.where(Parent.name == "parent1").gino.first()

    print(parent.children)
    print(parent.favorites)

    await parent.favorites
    print(parent.favorites)
    await parent.children
    print(parent.children)

    no1 = parent.children[0]

    assert isinstance(no1, Children)

    print(await no1.parent)
    print("The name of no1's parent is ", no1.parent.name)

    assert isinstance(parent.children.children, list)
