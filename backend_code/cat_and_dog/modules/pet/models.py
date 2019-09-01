# -*- coding: utf-8 -*-
# pet模块, 用于后期给用户打标签

from sqlalchemy import *
from sqlalchemy.orm import relationship

from .. import Base, RecordingMixin


class UserPetcate(Base):
    __tablename__ = "user_pet_cate_rel"
    user_id = Column(Integer, ForeignKey("user.id"))
    pet_cate_id = Column(Integer, ForeignKey("pet_categories.id"))


class PetCategories(RecordingMixin, Base):
    """宠物的分类, 用户注册时先让其选择自己样的宠物"""

    __tablename__ = "pet_categories"
    name = Column(String(255), nullable=False)

    # picked_pets = relationship("User", secondary='user_pet_cate_rel', lazy="dynamic", backref="pet_cate")
