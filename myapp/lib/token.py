#!/usr/bin/python
# -*- coding: utf-8 -*-
#encoding=utf-8
"""token的验证
"""
import time
import operator
from myapp import conf, comm

_first_check = True

def check_token(params, site):
    if "token" not in params or get_check_token_status(params, site) == False:
        return False 
    return True 
    
def get_check_token_status(params, site):
    global _first_check
    curtime = int(time.time())
    if  curtime - 1800 <= int(params['t']) <= curtime + 1800:
        #params['data'] = json.dumps(params['data'])
        #paramdata['t'] = params['t']
        reqtoken = params['token']
        params.pop('token')

        _first_check = True
        restoken  = set_token(params, site)
        if restoken == reqtoken:
            return True
        else:
            ## 为了兼容push的php和Python请求做一次兼容
            _first_check = False
            restoken = set_token(params, site)
            if restoken == reqtoken:
                return True
            return False
        
    return False
               
def loop_array_token(paramdata, site):
    global _first_check
    token = ""
    paramdata = sorted(paramdata.iteritems(), key=operator.itemgetter(0))
    for k,v in paramdata:
        if isinstance(v, dict):
            token = "%s%s" % (token, k)
            token = "%s%s" % (token, loop_array_token(v, site))
        else:
            token = "%s%s%s" % (token, k, v)
    if site == "PUSH" and _first_check: ## 兼容push请求不strip的情况
        return token
    else:
        return comm.stripslashes(token)

    
def set_token(paramdata, site = 'PUSH'):
    if site not in conf.TOKEN_KEYS:
        return None
    token = conf.TOKEN_KEYS[site]
   
    token = "%s%s" % (token, loop_array_token(paramdata, site))
    token = "%s%s" % (token, conf.TOKEN_KEYS[site])
    token = comm.md5(token, t='upper')

    return token

