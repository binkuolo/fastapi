# -*- coding:utf-8 -*-
"""
@Time : 2022/4/23 8:33 PM
@Author: binkuolo
@Des: views home
"""
from fastapi import Request, Form
from models.base import User


async def home(request: Request):
    # return templates.get_template("index.html").render({"request": request, "id": id})
    return request.app.state.views.TemplateResponse("index.html", {"request": request, "id": id})


async def reg_page(req: Request):
    """
    注册页面
    :param req:
    :return: html
    """
    return req.app.state.views.TemplateResponse("reg_page.html", {"request": req})


async def result_page(req: Request, username: str = Form(...), password: str = Form(...)):
    """
    注册结果页面
    :param password: str
    :param username: str
    :param req:
    :return: html
    """

    add_user = await User().create(username=username, password=password)
    print("插入的自增ID", add_user.pk)
    print("插入的用户名", add_user.username)

    user_list = await User().all().values()
    # 打印查询结果
    for user in user_list:
        print(f"用户:{user.get('username')}", user)

    # 获取当前创建的用户
    get_user = await User().get_or_none(username=username)
    if not get_user:
        print("")
        return {"info": "没有查询到用户"}

    return req.app.state.views.TemplateResponse(
        "reg_result.html", {"request": req, "username": get_user.username, "password": get_user.password})
