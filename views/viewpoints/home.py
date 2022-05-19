# -*- coding:utf-8 -*-
"""
@Time : 2022/4/23 8:33 PM
@Author: binkuolo
@Des: views home
"""
from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", tags=["门户首页"], response_class=HTMLResponse)
async def home(request: Request):
    """
    门户首页
    :param request:
    :return:
    """
    return request.app.state.views.TemplateResponse("index.html", {"request": request})
