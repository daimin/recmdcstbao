#!/usr/bin/python
# -*- coding: utf-8 -*-
#encoding=utf-8

"""
参数辅助模块
"""

from flask import json
import myapp.lib.token
from flask import json
import time

def validate_params(request, site, docheck=False):
    """验证参数是否可以用
    """
    data     = request.args.get('data', None)
    t        = request.args.get('t', None)
    token    = request.args.get('token', None)
    
    if data is not None and t is not None and token is not None:
        try:
            if docheck:
                checkdata = {'t':t, 'token':token, "data": data}
                if request.args.get('wid', None):
                    checkdata = {'t':t, 'token':token, "data": data, "wid": request.args.get('wid', None)}
                if not mmstats.lib.token.check_token(checkdata, site):
                    return None
            else:
                curtime = int(time.time())
                if int(t) <= curtime - 1800 or int(t) >= curtime + 1800: ## 验证时间
                    return None
            datajson = json.loads(data)
            if not isinstance(datajson, dict):
                return None
            return (t, token, datajson) 
        except: 
            return None
    else:
        return None

def get_params(srcparams, f, t="$in" , **kwargs):
    """获取参数并组装好
    """
    ## 请求参数名
    if f is None: return ()
    ## 目标参数名，在数据库中存储的名称
    tf   = f if "tf" not in kwargs else kwargs["tf"]
    ## 字段的类型
    _type = 'string' if "type" not in kwargs else kwargs["type"]
    ## 目录值，在数据库中对应的值
    val   =  None if "val" not in kwargs else kwargs["val"]
    ### 请求参数的值
    rval   =  None if "rval" not in kwargs else kwargs["rval"]
    ### 系统给定的映射
    _map  =  None if "map" not in kwargs else kwargs["map"]
    
    param     = srcparams.get(f, None)

    if isinstance(param, int): param = str(param) ## 整数统一作为字符串处理

    if param == "all" or param is None: 
        return ()
    
    if rval is not None and (param != rval and (not isinstance(param, str) and not isinstance(param, rval))):
        return ()
    
    if val is not None and param != val:
        param = val
    
    if param is not None and len(param) > 0: 
        if t == "$in":
            param    = param.split(",") 
            
        if _type == 'int':
            if isinstance(param, list):
                if _map is not None:
                    param    = map(lambda x:int(_map[x]), param)
                else:
                    param    = map(lambda x:int(x), param)
            else:
                if _map is not None:
                    param    = int(_map[param])
                else:
                    param    = int(param)
                
        if t != '=':        
            return (tf, {t: param})
        else:
            return (tf, val)
        
    return ()

def combine_params(params):
    """整个得到的参数
    params 是一个元素是元组的列表
    """
    if params is None or len(params) == 0: return None
    params = filter(lambda x: x is not None and len(x) > 1, params )
    resparams = {}
    for (t,v) in params:
        if t in resparams and isinstance(v, dict):
            resparams[t].update(v)
        else: 
            resparams[t] = v
    return resparams 

def response_std(res, status=1, errno=0, errmsg=""):
    """构建返回结果为公司标准方式
    """
    #data = []
    #if res is not None and len(res) > 0:
    #    data.append(res)
    return json.dumps({"status": status,"data": res,"errormsg": {"errno": errno,"errmsg": errmsg}})
    

