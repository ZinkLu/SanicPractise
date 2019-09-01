import datetime
import os

import aiofiles
from sanic.exceptions import abort
from sanic.response import json

from cat_and_dog.utils.login.tools import admin_required
from . import public_bp
from sanic.request import Request


@public_bp.post("upload_files")
@admin_required
async def upload_files(request: Request):
    """上传图片并自动保存"""
    oss = request.app.config.get("OSS_URL")  # 如果有云存储使用云存储

    if oss:
        # 此处应该还需要读取oss相关的配置
        return

    # 保存当前文件
    file = request.files.get("file")
    if not file:
        return abort(400, "can't find any file in form-data")

    # 准备文件名
    static_file_path = request.app.config.get("STATIC_PATH")
    now = datetime.datetime.now()

    filename = f"{now.strftime('%Y%m%d%H%M%S%f')}-{file.name}"
    filepath = os.path.join(static_file_path, filename)

    async with aiofiles.open(filepath, "wb") as f:
        await f.write(file.body)

    return json({"location": filepath})
