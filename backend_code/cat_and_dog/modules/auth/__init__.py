from sanic import Blueprint

from cat_and_dog.utils.login.manager import LoginManager
from ..users.models import User

from .api import Auth
from ...modules.api_version import api_prefix

auth_bp = Blueprint("auth", url_prefix=api_prefix + 'auth/')

auth_bp.add_route(Auth.as_view(), "login/admin")
auth_bp.add_route(Auth.as_view(), "logout/admin")

login_manager = LoginManager()


@login_manager.user_loader
async def get_user(pk):
    return await User.get(pk)
