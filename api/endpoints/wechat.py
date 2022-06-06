# -*- coding:utf-8 -*-
"""
@Time : 2022/6/4 2:54 PM
@Author: binkuolo
@Des: 微信授权
"""
import json
import time
from wechatpy.oauth import WeChatOAuth
from wechatpy.exceptions import WeChatOAuthException
from fastapi import Request, APIRouter
from core.Auth import create_access_token
from core.Response import fail, success
from models.base import SystemParams
from aioredis import Redis
from config import settings
from schemas.base import WechatOAuthData, WechatUserInfo
from models.base import User

router = APIRouter()


@router.get('/auth/url')
async def get_authorize_url(req: Request):
    """
    获取微信授权url
    """
    # 获取session中的值 唯一字符串
    state = req.session.get("session")
    print(state)
    if not state:
        return fail(msg="非法请求")
    result = await SystemParams.get_or_none(params_name="wechat_auth")
    if not result:
        return fail(msg="请配置微信开发者参数")

    # 构造微信授权url
    oauth = WeChatOAuth(
        app_id=result.params.get("appid"),
        secret=result.params.get("secret"),
        scope='snsapi_userinfo',  # snsapi_base or snsapi_userinfo
        state=state,
        redirect_uri=result.params.get("redirect_uri")
    )

    # 写入redis缓存
    data = {"status": 0}
    redis: Redis = await req.app.state.cache
    await redis.set(name=f"auth_{state}", value=json.dumps(data), ex=settings.QRCODE_EXPIRE)

    return success(data={"authorize_url": oauth.authorize_url + '&t=' + str(int(time.time()))})


@router.get('/auth/call')
async def call(req: Request, code: str, state: str):
    """
    微信授权回调
    :param req:
    :param code: 授权code
    :param state: 授权后带回来的参数
    :return: html
    """
    # 获取redis中的数据
    data = await req.app.state.cache.get(f"auth_{state}")
    if not data:
        return req.app.state.views.TemplateResponse("wechat.html", {"request": req, "errmsg": "二维码已过期!"})

    result = await SystemParams.get_or_none(params_name="wechat_auth")
    if not result:
        return req.app.state.views.TemplateResponse("wechat.html", {"request": req, "errmsg": "请配置微信开发者参数!"})

    # 构造OAuth
    oauth = WeChatOAuth(
        app_id=result.params.get("appid"),
        secret=result.params.get("secret"),
        redirect_uri=result.params.get("redirect_uri")
    )

    try:
        # 拉取用户信息
        auth_data = WechatOAuthData(**oauth.fetch_access_token(code))

        # access_token
        time.sleep(0.5)
        # openid – 可选，微信
        # openid，默认获取当前授权用户信息
        #
        # access_token – 可选，
        # access_token，默认使用当前授权用户的access_token
        userinfo = WechatUserInfo(**oauth.get_user_info(openid=auth_data.openid, access_token=auth_data.access_token))
        print(userinfo.dict())
        # 将获微信用户授权信息写入redis缓存
        data = {"status": 1, "userinfo": userinfo.dict()}
        redis: Redis = await req.app.state.cache
        await redis.set(name=f"auth_{state}", value=json.dumps(data), ex=settings.QRCODE_EXPIRE)
        return req.app.state.views.TemplateResponse(
            "wechat.html", {"request": req, "client_ip": req.headers.get('x-forwarded-for'), **userinfo.dict()})

    except WeChatOAuthException as e:
        return req.app.state.views.TemplateResponse("wechat.html", {"request": req, "errmsg": e.errmsg})


@router.get('/auth/check')
async def scan_check(req: Request):
    # 获取session中的值 唯一字符串
    state = req.session.get("session")
    # 获取redis中的数据
    data = await req.app.state.cache.get(f"auth_{state}")
    if not data:
        return fail(code=201, msg="二维码已经过期!")
    # 提取redis中的数据
    result = json.loads(data)
    if result.get("status") == 1:
        userinfo = WechatUserInfo(**result.get("userinfo"))
        user = await User.get_or_none(wechat__openid=userinfo.openid)
        if not user:
            return fail(code=202, msg="当前微信未绑定,前往个人中心绑定!")
        jwt_data = {
            "user_id": user.pk,
            "user_type": user.user_type
        }
        jwt_token = create_access_token(data=jwt_data)
        data = {"token": jwt_token, "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60}
        await req.app.state.cache.delete(f"auth_{state}")
        return success(msg="登陆成功!", data=data)

    return fail(msg="等待扫码...")
