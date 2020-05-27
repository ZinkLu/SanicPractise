import uvloop

from cat_and_dog import create_app

uvloop.install()

app = create_app("dev")


async def init_db():
    from cat_and_dog.modules import db
    modules = (
        "cat_and_dog.modules.product.category",
        "cat_and_dog.modules.product.goods",
        "cat_and_dog.modules.product.brand",
        "cat_and_dog.modules.pet",
        "cat_and_dog.modules.users",
    )
    for m in modules:
        __import__(m + ".models")

    await db.set_bind(app.config["DATABASE_URL"])

    await db.gino.create_all()


async def create_admin(username, pwd):
    from cat_and_dog.modules import db
    from cat_and_dog.modules.users.models import User
    await db.set_bind(app.config["DATABASE_URL"])
    user = User()
    user.password = pwd
    user.mobile = username
    user.nick_name = username
    user.is_admin = True
    await user.create()


if __name__ == "__main__":
    # use sanic server to handler the request
    if app.config.get("DEBUG") is False:
        import multiprocessing

        # use nginx to handle the access log..
        # TODO: use uvicorn to start the app. there are some compatibility issues.
        app.run(port=5000, auto_reload=False, workers=multiprocessing.cpu_count() * 2 + 1, access_log=False)
    else:
        app.run(port=5000, auto_reload=True)
