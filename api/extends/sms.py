# -*- coding:utf-8 -*-
"""
@Time : 2022/6/7 5:16 PM
@Author: binkuolo
@Des: 腾讯云云短信SMS
"""
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
# 导入 SMS 模块的client Models
from tencentcloud.sms.v20190711 import sms_client, models

# 导入可选配置类
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile

# 系统包
from fastapi import Request, APIRouter, Query
from aioredis import Redis
from core.Response import fail, success
from core.Utils import code_number
from models.base import SystemParams, User

router = APIRouter()


@router.get('/send')
async def send_msg(req: Request, phone_number: str = Query(..., regex="^1[34567890]\\d{9}$")):
    """
    验证码发送
    :param req:
    :param phone_number:
    :return:
    """
    session_code = req.session.get("session")
    # redis 连接
    redis: Redis = await req.app.state.code_cache
    # 查询当前手机号是否绑定用户
    user = await User.get_or_none(user_phone=phone_number)
    if not user:
        return fail(msg=f"手机号 {phone_number} 未绑定用户!")
    # 获取云短信配置
    # params = {
    #     "secret_id": "",
    #     "secret_key": "",
    #     "region": "ap-guangzhou",
    #     "app_id": "",
    #     "sign": "",
    #     "template_id": "",
    #     "expire": 10
    # }
    result = await SystemParams.get_or_none(params_name="tencent_sms")
    if not result:
        return fail(msg="请配置腾讯云短信参数")

    # 验证码过期时间
    expire = result.params.get("expire")
    # 查询是否发送过验证码
    is_send = await redis.get(name=f"code_{phone_number}")
    if is_send:
        return fail(msg=f"手机号 {phone_number} 已发送过验证码，若未收到短信，请{expire}分钟后重试!")

    # 生成验证码
    code = code_number(6)
    # 发送验证码
    result.params.pop('expire')
    try:
        res = send(phone_number, session_code, code, **result.params)
        if not res:
            return fail(msg='短信接口错误')
        res = res.SendStatusSet
        if res[0].Code != 'Ok':
            print("短信发送失败！", res[0].Message)
            return fail(msg="短信发送失败，请稍后再试或者更换手机号！")
        print(res)
        await redis.set(name=f"code_{phone_number}", value=code, ex=expire * 60)
        return success(msg=f"短信已经发送，{expire} 分钟内有效。", data=expire * 60)
    except TencentCloudSDKException as err:
        return fail(msg="短信接发生错误!", data=err.message)


async def check_code(req: Request, verify_code: str, phone: str):
    """
    短信验证码校验
    :param req:
    :param verify_code:
    :param phone:
    :return:
    """
    # 获取redis中的验证码
    redis: Redis = await req.app.state.code_cache
    code = await redis.get(f"code_{phone}")
    # 比对验证码
    if code and verify_code == code:
        await redis.delete(f"code_{phone}")
        return True
    # 获取缓存中验证码
    return False


def send(
        phone: str,
        session: str,
        verify_code: str,
        secret_id: str,
        secret_key: str,
        region: str,
        app_id: str,
        sign: str,
        template_id: str
):
    """

    :param phone: 手机号
    :param session: 客户端唯一字符串
    :param verify_code: 验证码
    :param secret_id: 凭证ID
    :param secret_key: 凭证钥匙
    :param region: 地域
    :param app_id: 应用ID
    :param sign: 签名
    :param template_id: 模版ID
    :return:
    """
    try:
        # 必要步骤：
        # 实例化一个认证对象，入参需要传入腾讯云账户密钥对 secretId 和 secretKey
        # 本示例采用从环境变量读取的方式，需要预先在环境变量中设置这两个值
        # 您也可以直接在代码中写入密钥对，但需谨防泄露，不要将代码复制、上传或者分享给他人
        # CAM 密钥查询：https://console.cloud.tencent.com/cam/capi
        cred = credential.Credential(secret_id, secret_key)
        # cred = credential.Credential(
        #     os.environ.get(""),
        #     os.environ.get("")
        # )

        # 实例化一个 http 选项，可选，无特殊需求时可以跳过
        http_profile = HttpProfile()
        http_profile.reqMethod = "POST"  # POST 请求（默认为 POST 请求）
        http_profile.reqTimeout = 30  # 请求超时时间，单位为秒（默认60秒）
        http_profile.endpoint = "sms.tencentcloudapi.com"  # 指定接入地域域名（默认就近接入）

        # 非必要步骤:
        # 实例化一个客户端配置对象，可以指定超时时间等配置
        client_profile = ClientProfile()
        client_profile.signMethod = "TC3-HMAC-SHA256"  # 指定签名算法
        client_profile.language = "en-US"
        client_profile.httpProfile = http_profile

        # 实例化 SMS 的 client 对象
        # 第二个参数是地域信息，可以直接填写字符串 ap-guangzhou，或者引用预设的常量
        client = sms_client.SmsClient(cred, region, client_profile)

        # 实例化一个请求对象，根据调用的接口和实际情况，可以进一步设置请求参数
        # 您可以直接查询 SDK 源码确定 SendSmsRequest 有哪些属性可以设置
        # 属性可能是基本类型，也可能引用了另一个数据结构
        # 推荐使用 IDE 进行开发，可以方便的跳转查阅各个接口和数据结构的文档说明
        req = models.SendSmsRequest()

        # 基本类型的设置:
        # SDK 采用的是指针风格指定参数，即使对于基本类型也需要用指针来对参数赋值
        # SDK 提供对基本类型的指针引用封装函数
        # 帮助链接：
        # 短信控制台：https://console.cloud.tencent.com/smsv2
        # sms helper：https://cloud.tencent.com/document/product/382/3773

        # 短信应用 ID: 在 [短信控制台] 添加应用后生成的实际 SDKAppID，例如1400006666
        req.SmsSdkAppid = app_id
        # 短信签名内容: 使用 UTF-8 编码，必须填写已审核通过的签名，可登录 [短信控制台] 查看签名信息

        req.Sign = sign
        # 短信码号扩展号: 默认未开通，如需开通请联系 [sms helper]
        req.ExtendCode = ""
        # 用户的 session 内容: 可以携带用户侧 ID 等上下文信息，server 会原样返回
        req.SessionContext = session
        # 国际/港澳台短信 senderid: 国内短信填空，默认未开通，如需开通请联系 [sms helper]
        req.SenderId = ""
        # 下发手机号码，采用 e.164 标准，+[国家或地区码][手机号]
        # 例如+8613711112222， 其中前面有一个+号 ，86为国家码，13711112222为手机号，最多不要超过200个手机号
        req.PhoneNumberSet = [f"+86{phone}"]
        # 模板 ID: 必须填写已审核通过的模板 ID，可登录 [短信控制台] 查看模板 ID
        req.TemplateID = template_id
        # 模板参数: 若无模板参数，则设置为空
        req.TemplateParamSet = [verify_code, "10"]

        # 通过 client 对象调用 SendSms 方法发起请求。注意请求方法名与请求对象是对应的
        resp = client.SendSms(req)
        return resp

    except TencentCloudSDKException as err:
        print(err)
        raise err
