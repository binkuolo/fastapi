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
from fastapi import Request, APIRouter, Security
from api.endpoints.common import write_access_log
from core.Auth import create_access_token, check_permissions
from core.Response import fail, success
from models.base import SystemParams
from aioredis import Redis
from config import settings
from schemas.base import WechatOAuthData, WechatUserInfo
from models.base import User, UserWechat

router = APIRouter()


@router.get('/auth/url', tags=["获取微信授权url"], description="用于扫码登陆、扫码注册场景")
async def get_authorize_url(req: Request, scan_type: str = 'login'):
    """
    获取微信授权url
    :param req:
    :param scan_type: 扫码类型 默认登陆
    :return:
    """
    # 获取session中的值 唯一字符串
    state = req.session.get("session")
    if not state:
        return fail(msg="页面标识丢失!")
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
    expire = result.params.get("expire") * 60
    # 写入redis缓存
    data = {"status": 0, "scan_type": scan_type}
    redis: Redis = await req.app.state.cache
    await redis.set(name=f"auth_{state}", value=json.dumps(data), ex=expire)
    data = {
        "authorize_url": oauth.authorize_url + '&t=' + str(int(time.time())),
        "expire": expire
    }
    return success(data=data, msg="微信授权二维码url")


@router.get('/auth/bind/url', dependencies=[Security(check_permissions)], description="获取用户微信绑定url")
async def wechat_bind(req: Request):
    """
    用户微信绑定url
    :param req:
    :return:
    """
    # 获取session中的值 唯一字符串
    state = req.session.get("session")
    if not state:
        return fail(msg="页面标识丢失!")
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
    expire = result.params.get("expire") * 60
    # 写入redis缓存
    data = {"status": 0, "scan_type": "binding", "user_id": req.state.user_id}
    redis: Redis = await req.app.state.cache
    await redis.set(name=f"auth_{state}", value=json.dumps(data), ex=expire)
    data = {
        "authorize_url": oauth.authorize_url + '&t=' + str(int(time.time())),
        "expire": expire
    }
    return success(data=data, msg="用户微信用户绑定二维码url")


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
        # print(userinfo.dict())
        if json.loads(data).get('scan_type') == "binding":
            # 微信绑定
            is_bind = await UserWechat.get_or_none(openid=auth_data.openid)
            if is_bind:
                return req.app.state.views.TemplateResponse(
                    "wechat.html",
                    {
                        "request": req,
                        "errmsg": "当前微信已绑被其他用户绑定!"
                    })
        # 将获微信用户授权信息写入redis缓存
        redis_result: dict = json.loads(data)
        redis_result.update({"status": 1})
        redis_result.setdefault("userinfo", userinfo.dict())
        print(redis_result)
        redis: Redis = await req.app.state.cache
        await redis.set(name=f"auth_{state}", value=json.dumps(redis_result), ex=result.params.get("expire") * 60)
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
        if result.get("scan_type") == "login":
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
            await write_access_log(req, user.pk, "通过微信扫码登陆了系统!")
            return success(msg="登陆成功!", data=data)

        if result.get("scan_type") == "binding":
            # 获取到当前用户ID
            user_id = result.get("user_id")
            if not user_id:
                return fail(code=4003, msg="未携带用户标识!")
            if user_id == 1:
                return fail(4003, "请添加普通用户测试此功能!")
            user = await User.get_or_none(id=user_id)
            if not user:
                return fail(4004, "当前用户不存在,可能被管理员删除了!")
            # 提取微信用户信息
            userinfo = WechatUserInfo(**result.get("userinfo"))
            # 微信表不存在就创建、存在就更新
            await UserWechat.update_or_create(user=user, defaults=userinfo.dict())
            # 更新用户头像和昵称
            await User.filter(id=user.pk).update(header_img=userinfo.headimgurl, nickname=userinfo.nickname)
            # 删除redis中的数据
            await req.app.state.cache.delete(f"auth_{state}")
            return success(msg="绑定成功!")

    return fail(msg="等待扫码...")
