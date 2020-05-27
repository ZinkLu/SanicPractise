# -*- coding: utf-8 -*-

from functools import partial
from reprlib import repr

from gino.declarative import Model
from gino.loader import ModelLoader
from sqlalchemy import and_, select

from cat_and_dog.utils.empty import Empty
from .exception import RelationException


def _do_load(self, row):
    values = dict((c.name, row[c]) for c in self.columns if c in row)
    if all((v is None) for v in values.values()):
        return None
    rv = self.model()
    for c in self.columns:
        if c in row:
            # noinspection PyProtectedMember
            instance_key = self.model._column_name_map.invert_get(c.name)
            rv.__values__[instance_key] = row[c]

    # set the relation automatically
    rv.init_the_relation()

    return rv


ModelLoader._do_load = _do_load


def setup_base(base):
    new_base = type(
        base.__name__,
        (RelationMixin, base),
        {}
    )

    RelationShip.base = new_base
    return new_base


class RelationMixin:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.__rel__ = set()
        for k, v in cls.__dict__.items():
            if isinstance(v, RelationShip):
                cls.__rel__.add(k)

    def __str__(self):
        return f"<{self.__class__.__name__}-{self.id}>"

    def __await__(self):
        """query for all relations"""

        async def query_all_relations(self):
            for name in self.__rel__.copy():
                await getattr(self, name)

        return query_all_relations(self).__await__()

    def init_the_relation(self):
        """
        在model loader之后应该调用该方法, 设置relation,
           重新调用该方法会重新设置属性

        # 伪代码
        instance = await Model.get(1)

        await instance  # load the relation

        # update the instance
        await instance.update(name='XXXX', parent_id=20)

        # 此时relation并没有更改
        instance.parent # 原来的parent

        instance.init_the_relation()

        await instance.parent  # 重新load关系属性

        instance.parent  # 此时更新
        """
        for rel in self.__rel__:
            relation = getattr(self.__class__, rel)
            if isinstance(relation, RelationShip):
                setattr(self, rel, relation(self, rel))


class RelationShip:
    """
    重新定义relationship;
    该属性应该设置在`One`的一方, 因为`Many`的一方已经存在了外键, 可以通过外外键来找到其Parent;
    该类应该有缓存的作用;因此`One`的一方也应该设置该值;
    该类被访问时应该有动态加载的效果(针对One的一方), 而不是全部加载, 也应该要支持切片;

    RelationShip is behavior like a factory function,
    the instance of RelationShip query for the relations
    and return a new instance of its self.

    - usage

        ```python
        @setup_base  # a base model is required
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

        # MUST USE `Class` to define a table
        class ParentFavoriteRel(Base):
            __tablename__ = "parent_favorite_rel"
            parent_id = Column(Integer, ForeignKey("test_parent.id"), index=True)
            favorite_id = Column(Integer, ForeignKey("test_favorite.id"), index=True)
            ```
    """
    base = None

    __slots__ = ('relation',
                 'related_model',
                 'fk',
                 'secondary',
                 'secondary_fk',
                 'is_find_model',
                 'is_find_foreign')

    def __init__(self,
                 relation,
                 related_model,
                 secondary=None,
                 fk=None,
                 secondary_fk=None):
        """
        :param relation:
                - many2one return an instance of parent
                - one2many return a list-like of children
                - many2many return a list-like of relations(like one2many)
                - one2one return an instance of parent(like many2one)
        :param related_model: related model name of the model
        :param secondary: for many2many, the `secondary` stand for the model that
                          holds the relations
        :param fk: foreign key
        :param secondary_fk: secondary foreign key
        """
        if not self.base:
            raise RelationException("call setup_base() before subclass of Base created")
        self.is_find_model = False
        self.is_find_foreign = False
        self.relation = relation
        self.related_model = related_model
        self.fk = fk
        self.secondary = secondary
        self.secondary_fk = secondary_fk
        if relation == "many2many" and secondary is None:
            raise RelationException("many2many relation should explict 'secondary'")

    @staticmethod
    def get_fk_from_related_model(one: 'Model',
                                  many: 'Model') -> str:
        """
        :param one:
        :param many:
        :return: foreign key name
        """
        tablename = one.__tablename__

        fks = {fk for fk in many.__table__.foreign_keys if tablename == fk._column_tokens[1]}
        if len(fks) != 1:
            raise RelationException(
                f"Can't figure out the foreign, the related model {many} has {len(fks)} foreign key(s)")
        return fks.pop().parent.name

    def figure_out_fk(self, instance):
        """
        figure out the foreign key, and set self.fk and self.secondary_fk
        """
        if self.secondary:
            if not self.fk:
                self.fk = self.get_fk_from_related_model(one=instance, many=self.secondary)
            if not self.secondary_fk:
                self.secondary_fk = self.get_fk_from_related_model(one=self.related_model, many=self.secondary)
        else:
            if self.fk:
                return
            if self.relation == "many2one":
                self.fk = self.get_fk_from_related_model(one=self.related_model, many=instance)
            elif self.relation == "one2many":
                self.fk = self.get_fk_from_related_model(one=instance, many=self.related_model)

    @staticmethod
    def find_model_by_class_name(name: str,
                                 base) -> Model:
        """
        find the model in the subclass of base by the model name
        :param name: the name of the model
        :param base: base model
        :return: the model
        """
        model_to_find = list(filter(lambda x: name == x.__name__, base.__subclasses__()))
        model_to_find = model_to_find and model_to_find[0] or None
        if not model_to_find:
            raise Exception(f"can't find secondary model {name}")
        return model_to_find

    def __call__(self, instance, local_variable_name) -> 'RelationalParent' or 'RelationalChildren':
        """
        - many2one return an instance of parent
        - one2many return a list-like of children
        - many2many return a list-like of relations(like one2many)
        - one2one return an instance of parent(like many2one)
        """
        if not self.is_find_model:
            # related_model must been found here because the base has't been fully inited until now
            self.is_find_model = True
            self.related_model = self.find_model_by_class_name(self.related_model, self.base)
            if self.secondary:
                self.secondary = self.find_model_by_class_name(self.secondary, self.base)

        if not self.is_find_foreign:
            self.is_find_foreign = True
            self.figure_out_fk(instance)

        if self.relation in ("many2one", "one2one"):
            return RelationalParent(self.related_model, instance, self.fk, variable=local_variable_name)
        elif self.relation == "one2many":
            return RelationalChildren(self.related_model, instance, self.fk)
        elif self.relation == "many2many":
            return RelationalChildren(self.related_model, instance, self.fk,
                                      secondary=self.secondary, secondary_fk=self.secondary_fk)


class RelationalChildren:
    """
    lazy load children
    """

    __slots__ = ('model', 'instance', 'fk', 'children', '_where')

    def __init__(self,
                 model: 'Model',
                 instance,
                 fk: str,
                 secondary=None,
                 secondary_fk=None,
                 query=None
                 ):
        """
        :param model: the related model
        :param instance:
        :param fk: foreign name
        :param query: sqlalchemy query
        """
        self.model = model
        self.instance = instance
        # self.id = instance.id
        self.fk = fk  # foreign key
        self.children = Empty
        if query is not None:
            self._where = query
        else:
            if secondary and secondary_fk:
                # `select secondary_fk from secondary where fk  = instance.id`
                self._where = getattr(model, "id").in_(
                    select([getattr(secondary, secondary_fk)]).
                        where(getattr(secondary, fk) == instance.id))
            else:
                # `select id from rel_model where fk = instance.id`
                self._where = (getattr(model, fk) == instance.id)  # Only take fk as condition

    def __str__(self):
        if self.children is not Empty:
            return self.children.__str__()
        return f"<Query {repr(self._where.__str__())}>"

    def filter(self, query):
        """
        query return a new instance of RelationList which only change the
        query statement
        :param query:
        :return:
        """
        return self.condition_filter(query)

    def condition_filter(self, query, condition=and_):
        """
        like `query` method , but with condition
        :param query:
        :param condition: and_, or_, not_, when the new query combine the
               original query; the cached children also reset to list()
        :return: RelationalChildren
        """
        return RelationalChildren(self.model, self.instance, self.fk, condition(self._where, query))

    async def first(self) -> 'Model' or None:
        if self.children is Empty:
            return await self.model.query.where(self._where).gino.first()

        return self.children and self.children[0] or None

    async def all(self):
        """
        query for the children using self._where
        """
        if self.children is Empty:
            self.children = await self.model.query.where(self._where).gino.all()

        return self.children

    def __await__(self):
        """await all CacheInstance
        also see `all()`
        """
        return self.all().__await__()

    def __setitem__(self, key, value):
        """
        the children can't be set by subscription
        """
        pass

    def __getitem__(self, item):
        if self.children is Empty:
            raise RelationException("Await the RelationalChildren before access to it")
        return self.children[item]

    def __iter__(self):
        if self.children is Empty:
            raise RelationException("Await the RelationalChildren before access to it")
        return iter(self.children)


class RelationalParent:
    __slots__ = ("model", "instance", "_where", "variable")

    def __init__(self,
                 model: 'Model',
                 instance,
                 fk: str,
                 variable: str):
        self.model = model
        self.instance = instance
        self.variable = variable
        self._where = (getattr(model, "id") == getattr(instance, fk))

    async def set_parent(self):
        res = await self.model.query.where(self._where).gino.first()
        setattr(self.instance, self.variable, res)
        return res

    def __await__(self):
        return self.set_parent().__await__()

    def __getattr__(self, item):
        raise RelationException("Await the RelationalParent to access before access it")

    def __str__(self):
        return f"<Related to {self.model.__name__} id={self.instance.id}>"


class CacheInstance:
    """
    CacheInstance 可能用不到了...
    """
    __slots__ = ("model", "id", "instance")

    def __init__(self, model: 'Model', _id: int):
        self.model = model
        self.id = _id
        self.instance = None  # awaitable, its won't interact with DB until be awaited

    def __repr__(self):
        return f"<{self.model.__name__}-{self.id}>"

    def __getattr__(self, item):
        if self.instance:
            return getattr(self.instance, item)
        return self.__await__()

    async def get_instance(self) -> 'Model':
        return await self.instance

    def __await__(self):
        """make the CacheInstance can be awaited
        instance = await CacheInstance(Model, 1)
        """

        async def bind_instance(self):
            if self.instance:
                return self.instance
            self.instance = await self.model.get(self.id)

        return bind_instance(self).__await__()


many2one = partial(RelationShip, "many2one")
one2many = partial(RelationShip, "one2many")
many2many = partial(RelationShip, "many2many")

doc = RelationShip.__doc__
many2one.__doc__ = doc
many2many.__doc__ = doc
one2many.__doc__ = doc

if __name__ == '__main__':
    import asyncio


    async def test():
        from cat_and_dog.modules import db
        from cat_and_dog.modules.product.category.models import Categories
        from cat_and_dog.config.dev import DATABASE_URL
        await db.set_bind(DATABASE_URL, echo=True)

        instance = await Categories.get(1)

        children = await instance.children.filter(Categories.name.like("猫"))
        print(children)
        pass


    asyncio.run(test())
