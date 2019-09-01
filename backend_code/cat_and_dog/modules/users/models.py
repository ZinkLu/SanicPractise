# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import *
from werkzeug.security import check_password_hash, generate_password_hash

from cat_and_dog.utils.login.mixins import UserMixin
from cat_and_dog.utils.relations.orm_relations import many2one
from .. import RecordingMixin, Base, db


class WeiXinUser(RecordingMixin, Base):
    """保存用户微信信息"""
    __tablename__ = "weixin_user"

    # id = Column(Integer, primary_key=True)
    open_id = Column(String(100), index=True)
    avatar_url = Column(Text)
    nickname = Column(String(100))
    gender = Column(Boolean)
    province = Column(String(50))
    city = Column(String(50))
    country = Column(String(50))
    privilege = Column(Text)
    unionid = Column(Integer)

    # user = relationship("User", backref="weixin", uselist=False)


class User(UserMixin, RecordingMixin, Base):
    """User, 核心表"""
    __tablename__ = "user"

    # id = Column(Integer, primary_key=True)
    nick_name = Column(String(32), nullable=False)  # 用户昵称
    password_hash = Column(String(128))  # 加密的密码, 只有admin才会使用
    mobile = Column(String(11), unique=True, nullable=False, index=True)  # 手机号
    avatar_url = Column(String(256))  # 用户头像路径, 默认和微信一样, 后期支持修改?
    last_login = Column(DateTime, default=datetime.now)  # 最后一次登录时间
    is_admin = Column(Boolean, default=False)  # 是否管理员?
    signature = Column(String(512))  # 用户签名
    gender = Column(Enum("MAN", "WOMAN", name="varchar"), default="MAN")
    weixin_id = Column(Integer, ForeignKey("weixin_user.id"))

    wx_info = many2one("WeiXinUser")

    @property
    def is_active(self):
        return self.status == 1

    @property
    def password(self):
        return None

    @password.setter
    def password(self, value):
        self.password_hash = generate_password_hash(value)

    async def check_pwd(self, pwd):
        """验证密码的同时更新最后登录时间"""
        is_success = check_password_hash(self.password_hash, pwd)
        if is_success:
            async with db.auto_commit():
                await self.update(last_login=datetime.now()).apply()
        return is_success
