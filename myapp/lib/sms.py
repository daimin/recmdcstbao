#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding=utf-8
"""发送短信
"""
import datetime
import requests
import json
import base64
import hashlib

accountSid = 'ef468b2eae27e0340cf1995baf702862'
token = '09e786fb2dd5529eae653448a0981f39'
templateId = '12157'
appid = '36638b4307fc423a89ea8af876563db7'


def send_sms(phone, param):
    url = "https://api.ucpaas.com/2014-06-30/"
    body_json = {
        'templateSMS' : {
            'appId' : appid,
            'templateId' : templateId,
            'to' : phone,
            'param' : ",".join(param)
        }
    }
    requrl = url + "Accounts/%s/Messages/templateSMS?sig=%s" % (accountSid, get_sig_parameter())
    res = requests.post(requrl, data=json.dumps(body_json), headers={
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': get_authorization(),
    })

    if res and res.status_code == 200:
        res_obj = json.loads(res.content)
        if res_obj and 'resp' in res_obj and res_obj['resp']['respCode'] == '000000':
            return True
    return False


def get_timestamp():
    return int(datetime.datetime.now().strftime("%Y%m%d%H%M%S")) + 7200


def get_sig_parameter():
    m2 = hashlib.md5()
    m2.update(("%s%s%s" % (accountSid, token, get_timestamp())))
    return m2.hexdigest().upper()


def get_authorization():
    return base64.b64encode("%s:%s" % (accountSid, get_timestamp()))


send_sms('13560093349', ['<a href="http://www.baidu.com">百度</a>', '1'])
# print getSigParameter()