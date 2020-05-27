# A Sanic Playground🚀

## Goal

想要学习一下Python的异步编程, 想使用异步的web框架编写一个简单的应用, 同时也了解一下[`ASGI`](https://asgi.readthedocs.io/en/latest/index.html), 于是就有了这个仓库.

## About the App

1. 这是一个**宠物社区商城**的后端项目, 提供了一套标准的Restful接口;

2. 这是一个学习项目, 因此不会处理非常复杂的业务逻辑, 但是目标是完成基本的商城功能与社交功能;

3. 目前进度: 之前一直在编写一些小工具, 因此目前进度十分缓慢;

4. Api文档[地址](http://www.empty.com);

5. 👨‍💻‍👨‍💻‍不断提交中👨‍💻‍👨‍💻‍;

6. 配套的前端代码也正在开发中;

7. **勿用作商业**;如果你想要快速搭建一个电商应用, 不妨尝试[Saleor](https://saleor.io/)(基于graphQL)或者[odoo](https://www.odoo.com/)

## Backend Component

> 在这里推荐[awesome-asyncio](https://github.com/timofurrer/awesome-asyncio) 这个仓库, 虽然现在Python异步的库不是很多. 本仓库的组件基本来自于awesome-asyncio

### Web Framework:

使用了Sanic框架进行开发

- [**Sanic**](https://github.com/huge-success/sanic)

    Sanic是一个类Flask的异步web框架, 并且拥有活跃的[社区](https://community.sanicframework.org/)

    由于使用了[ujson](https://github.com/ultrajson/ultrajson)和[uvloop](https://github.com/MagicStack/uvloop), Sanic的速度很快

还有一些优秀的异步web框架, 如:

- [Tornado](https://www.tornadoweb.org/en/stable/)

    原来使用epoll实现, 现在也原生支持了async语法, 很成熟了, production-ready

- [Quart](https://gitlab.com/pgjones/quart)

    提供了几乎与Flask一样的Api, 甚至能够使用Flask一些现有的插件

- [viper](https://github.com/viper-framework/viper)

    项目正在进行重构, 暂不考虑

### ORM

使用了[Gino](https://python-gino.org/)作为ORM

#### Database Client

Gino目前只支持postgresql作为其数据库, 且数据库客户端为[asyncpg](https://github.com/MagicStack/asyncpg), 一个性能极高的异步posgresql客户端

> Gino目前正在添加MySQL数据库的支持, 可以加入[社区](https://gitter.im/python-gino/Lobby)讨论

##### Relational

Gino使用了[SQLAlchemy core](https://github.com/sqlalchemy)作为其SQL的组具, 但是遗憾的是不支持SQLAlchemy ORM, 因为SQLAlchemy ORM的所有操作都是同步的.

虽然Gino也支持使用[Loaders and Relationship](https://python-gino.org/docs/en/master/how-to/loaders.html)去加载数据库一对多等关系, 但是稍微有些繁琐, 这里我自己封装了简单的[relationship工具](#relationship)以供项目使用.

##### Migrate

由于使用了SQLAlchemy, 因此支持[alembic](https://github.com/sqlalchemy/alembic)做数据库迁移工具

### Serializer and Validating

使用[marshmallow](https://github.com/marshmallow-code/marshmallow)2.x作为数据的序列化器和反序列化器, 由于我想在marshmallow中进行数据库级别的校验, 正好mm不支持异步校验, 因此在基础上实现了[异步的校验工具](#asyncvalidate), 支持在redis和数据库中进行校验.

### Message Queue Client

这里没有进行太多的选择, 直接使用了[celery](https://github.com/celery/celery) + [rabbitmq](https://www.rabbitmq.com/)进行消息的发送与处理.

PS: celery的`delay()`方法也是异步的

### Testing

[pytest+sanic](https://github.com/yunstanford/pytest-sanic)插件

### Server

由于最新的Sanic已经支持了ASGI(老版本不支持), 因此使用[Uvicorn](https://github.com/encode/uvicorn)作为服务器也是不错的选择.

Sanic自带的服务器性能没测试过, 不知道怎么样

### Others

aiofiles, aioredis, 等等的异步Python包

## Plugins

这里的插件指的是Sanic的插件, 虽然目前Sanic的插件不是很多.

1. [Sanic Session](https://github.com/xen/sanic_session)

## Utils

由于Sanic的插件目前不是很丰富, 于是自己封装了一些简单的工具

### <span id="asyncvalidate">Async Schema</span>

重写了marshmallow中的 `Unmarshaller`类, 添加了`async`方法/函数的装饰器

实现的装饰器有:

- `async_validates`

- `async_validates_schema`

- `async_pre_dump`

- `async_post_dump`

- `async_pre_load`

- `async_post_load`

使用如下:

```python
class FooSchema(Schema):
    
    id = fields.Integer()

    @async_validates_schema
    async def check_pk(self, data):
        _id = data.get("id")
        if not _id:
            raise Exception("id is required")
        
        model_id = await DB_BIND.execute("select id from foo_table where id = $1", (_id, ))

        if not model_id:
            raise Exception(f"{_id} is not exists in foo table")
        
        return data
```

> 目前只支持2.x的marshmallow

### Schema Mixin

使用mixin混入类来实现List, Detail等功能.

### <span id="relationship">ORM Relationship</span>

使用如下:

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

### Request Class

实现了request.user

参考了falsk-login的设计

## Run

使用docker来最少入侵你的系统

```sh
docker run -it -p 5000:5000 zinkworld/cat_and_dog:lastest sh -c "(service postgresql start ;redis-server /etc/redis/redis.conf ; su - cat -c 'python /home/cat/backend_code/main.py')"
```