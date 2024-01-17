# -*- coding:utf-8 -*-
"""
@Created on : 2022/4/22 22:02
@Author: binkuolo
@Des: app运行时文件
"""

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from config import settings
from fastapi.staticfiles import StaticFiles
from core import Exception, Events, Router, Middleware
from fastapi.templating import Jinja2Templates
from tortoise.exceptions import OperationalError, DoesNotExist, IntegrityError, ValidationError
from fastapi.openapi.docs import (get_redoc_html, get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html)
from fastapi.openapi.utils import get_openapi

# 创建FastAPI应用实例，设置debug模式，并设置doc和redoc页面为None
application = FastAPI(
    debug=settings.APP_DEBUG,
    docs_url=None,
    redoc_url=None,
    swagger_ui_oauth2_redirect_url=settings.SWAGGER_UI_OAUTH2_REDIRECT_URL,
)


# custom_openapi
def custom_openapi():
    if application.openapi_schema:
        return application.openapi_schema
    openapi_schema = get_openapi(
        description=settings.DESCRIPTION,
        version=settings.VERSION,
        title=settings.PROJECT_NAME,
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "/logo-teal.png"
    }
    application.openapi_schema = openapi_schema
    return application.openapi_schema


application.openapi = custom_openapi


# custom_swagger_ui_html
@application.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=application.openapi_url,
        title=application.title + " - Swagger UI",
        oauth2_redirect_url=application.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/swagger-ui-bundle.js",
        swagger_css_url="/swagger-ui.css",
    )


# swagger_ui_oauth2_redirect_url
@application.get(application.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


# redoc
@application.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=application.openapi_url,
        title=application.title + " - ReDoc",
        redoc_js_url="/redoc.standalone.js",
    )


# 事件监听
application.add_event_handler("startup", Events.startup(application))
application.add_event_handler("shutdown", Events.stopping(application))

# 异常错误处理
application.add_exception_handler(HTTPException, Exception.http_error_handler)
application.add_exception_handler(RequestValidationError, Exception.http422_error_handler)
application.add_exception_handler(Exception.UnicornException, Exception.unicorn_exception_handler)
application.add_exception_handler(DoesNotExist, Exception.mysql_does_not_exist)
application.add_exception_handler(IntegrityError, Exception.mysql_integrity_error)
application.add_exception_handler(ValidationError, Exception.mysql_validation_error)
application.add_exception_handler(OperationalError, Exception.mysql_operational_error)

# 中间件
#  添加中间件BaseMiddleware，用于处理全局请求和响应。
application.add_middleware(Middleware.BaseMiddleware)

#  添加中间件CORSMiddleware，用于处理跨域资源共享（CORS）相关的请求和响应。
application.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)
#   添加中间件SessionMiddleware，用于处理HTTP会话。
application.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie=settings.SESSION_COOKIE,
    max_age=settings.SESSION_MAX_AGE
)

# 路由
application.include_router(Router.router)

# 静态资源目录
application.mount('/', StaticFiles(directory=settings.STATIC_DIR), name="static")
application.state.views = Jinja2Templates(directory=settings.TEMPLATE_DIR)

'''
fastapi的 state，可以向请求头里放一些东西
Request对象的app.state属性是一个存储应用程序级别（application-level）状态的对象。
这个属性通常在FastAPI应用程序的启动过程中设置，并且可以包含任意自定义的应用程序级别的数据。
app.state属性是一个字典，你可以将任何需要在整个应用程序中共享的数据存储在其中。
app.state属性没有固定的属性列表，因为它可以包含任何你认为需要在应用程序的各个部分之间共享的数据。
你可以根据你的需求自由地向其中添加属性。
通常，app.state属性用于存储应用程序的配置、共享的数据库连接池、缓存连接池、全局设置、第三方服务的客户端实例等。
这可以帮助你在不同的路由处理函数之间共享数据，而无需在每个函数中显式传递这些数据。
'''

app = application
