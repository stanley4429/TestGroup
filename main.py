# author: stanley
# crated date: 2021/6/5
# -*- coding:utf-8 -*-
# update time:
# app store connect api


# 苹果开放接口 https://developer.apple.com/documentation/appstoreconnectapi


from authlib.jose import jwt
import time
import json
import requests
from datetime import datetime, timedelta


def description(resp):
    if resp.status_code == 200 or resp.status_code == 201:
        print('正确✅\n', json.dumps(resp.json()))
    else:
        print('错误❌\n', json.dumps(resp.json()))


def get_token(key, iss, key_file):
    """
    :param key:
    :param iss:
    :param key_file:
    :return:
    """
    # 读取私钥
    private_key = open(key_file, 'r').read()
    # 构造header
    header = {
        "alg": algorithm,
        "kid": key,
        "typ": "JWT"
    }
    # 构造payload
    payload = {
        "iss": iss,
        "exp": int(time.mktime((datetime.now() + timedelta(minutes=20)).timetuple())),
        "aud": "appstoreconnect-v1"
    }
    return jwt.encode(header, payload, private_key).decode('utf8')


# ------------------ 参数配置 ------------------

algorithm = 'ES256'
base_api_url = "https://api.appstoreconnect.apple.com"

private_key_id = 'F7GVGP3Y89'    # 密钥
issue_id = '98060318-d373-4e0b-b267-2521c73afc13'   # issue_id
auth_key_path = 'static/AuthKey_F7GVGP3Y89.p8'     # p8 文件
token2 = get_token(private_key_id, issue_id, auth_key_path)


# ------------------ 获取具体接口的方法 ------------------
def base_call(url, token, method="get", data=None):
    """
    :param url:
    :param token:
    :param method:
    :param data:
    :return:
    """

    re_header = {"Authorization": "Bearer %s" % token}
    r = {}
    url = base_api_url + url

    requests.adapters.DEFAULT_RETRIES = 1
    req = requests.session()
    req.keep_alive = False

    if method.lower() == "get":
        r = req.get(url, params=data, headers=re_header)

    elif method.lower() == "post":
        re_header["Content-Type"] = "application/json"
        r = req.post(url=url, headers=re_header, data=json.dumps(data))

    elif method.lower() == "patch":
        re_header["Content-Type"] = "application/json"
        r = req.patch(url=url, headers=re_header, data=json.dumps(data))

    # print('请求body：\n', json.dumps(data))
    return r


def set_betaGroups(api_token, data):
    set_betaGroups_url = '/v1/betaGroups'
    res = base_call(set_betaGroups_url, api_token, 'post', data)
    return res


def check_betaGroups(api_token, data):
    check_betaGroups_url = '/v1/betaGroups'
    res = base_call(check_betaGroups_url, api_token, 'get', data)
    return res


def get_apps(api_token, data):
    get_apps_url = '/v1/apps'
    res = base_call(get_apps_url, api_token, 'get', data)
    return res


# ------------------ 具体功能实现部分 ------------------

# 设置测试组
def setBetGroup(name, app_id):
    data = {
        "data": {
                "type": "betaGroups",
                "attributes": {
                    "hasAccessToAllBuilds": True,
                    "isInternalGroup": True,
                    "name": name
                },
                "relationships": {
                    "app": {
                        "data": {
                            "type": "apps",
                            'id': app_id
                        }
                    }
                }
            }
    }
    set_betaGroups(token2, data)


# 获取所有的app
def getApps():
    data = {
        "limit": 200,
        # "filter[removed]": False,
        # "include": "visibleApps,provider",
    }
    res = get_apps(token2, data)
    if res.status_code == 200:
        for app in res.json()["data"]:
            print('app名称：', app["attributes"]["name"])
            if checkBetaGroups(app["id"]) is False:   # 检测是否已经存在测试群组
                print('\t⚠️测试组不存在，开始创建测试组=> ', app["attributes"]["name"])
                setBetGroup(name=app["attributes"]["name"], app_id=app["id"])


# 检测app是否已经设置测试组
def checkBetaGroups(app_id):
    data = {
        "limit": 100,
        "filter[app]": app_id,
        # "sort": "name",
    }
    res = check_betaGroups(token2, data)
    for group in res.json()["data"]:
        print('\t测试组：', group["attributes"]["name"])

    if len(res.json()["data"]) > 0:
        return True
    else:
        return False


if __name__ == "__main__":
    getApps()
