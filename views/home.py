# -*- coding:utf-8 -*-
"""
@Time : 2022/4/23 8:33 PM
@Author: binkuolo
@Des: views home
"""
from fastapi import Request


async def home(request: Request, id: str):

    return request.app.state.views.TemplateResponse("index.html", {"request": request, "id": id})
