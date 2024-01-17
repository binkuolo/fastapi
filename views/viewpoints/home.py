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
    # app.py 中 ，application.state.views = Jinja2Templates(directory=settings.TEMPLATE_DIR)
    #通常用法：
    # templates =  Jinja2Templates(directory=settings.TEMPLATE_DIR)
    # return templates.TemplateResponse("index.html", {"request": request})
    # return方法2：
    # return templates.get_template("index.html").render({'request':request, 'id': id})

    return request.app.state.views.TemplateResponse("index.html", {"request": request})

