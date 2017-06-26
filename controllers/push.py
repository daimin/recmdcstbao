#!/usr/bin/python
# -*- coding: utf-8 -*-
#encoding=utf-8
"""
push系统专用接口
"""
import mmstats
from flask import request
from mmstats import comm
from mmstats import lib
from mmstats import conf
from mmstats.models.AppMamaquanLastvisitToken import AppMamaquanLastvisitToken
from mmstats.models.AppMamaquanLastvisitTokenRm import AppMamaquanLastvisitTokenRm
from mmstats.models.AppMamaquanMapiUidFid import AppMamaquanMapiUidFid
from mmstats.models.AppMamaquanPushQueue import AppMamaquanPushQueue
from mmstats.models.AppHuaiyunLastvisitToken import AppHuaiyunLastvisitToken
from mmstats.models.AppHuaiyunLastvisitTokenRm import AppHuaiyunLastvisitTokenRm
from mmstats.models import RedisConn
import math
from flask import json
import time
import pymongo
import os


logger = comm.getlogger("%s.log" %  __file__, ap=True)


def get_identity_condi(params):

    identity_params = params.get('identity', "None")
    if identity_params is None or identity_params == "all":
        return None

    appname = params.get("appname", None)

    def ch_tuple2dict(tup):
        if tup is None or len(tup) < 2: 
            return {} 
        dic = {}
        dic[tup[0]] = tup[1] 
        return dic
    
    def get_date_range(datval):
        daterange = {}
        try:
            daterange["$gte"] =  comm.timestamp2datetime(int(datval['s'])).strftime("%Y-%m-%d")
        except:
            pass
        
        try:
            daterange["$lt"] =  comm.timestamp2datetime(int(datval['e'])).strftime("%Y-%m-%d")
        except:
            pass
        return daterange
    
    orconds = []

    bbtags    = []
    bbtags_or = []

    if appname is None or appname == "mmq":
        if "beiyun" in identity_params:
            bbtags.append(1)
            bbtags_or.append(1)
        if "other" in identity_params:
            bbtags.append(4)
            bbtags_or.append(4)
            bbtags.append(0)    ## bbtag等于0，即没有bbtag的值的，我这里将其也当做other
            bbtags_or.append(0)
        if "huaiyun" in identity_params:
            bbtags.append(2)
        if "havebaby" in identity_params:
            bbtags.append(3)

        if len(bbtags) > 0:
            ## 只有怀孕和有小孩的需要拿所有的bbtag进行判断
            if 2 in bbtags or 3 in bbtags:
                bbtags.append(2)
                bbtags.append(3)
                bbtags.append(4)
                bbtags.append(0)

            bbtags = list(set(bbtags))  ## 去重复

            orconds.append({"bbtag": {"$in": bbtags}})
            ## 如果查询了所有的状态，且怀孕和有宝宝的查询都是all的话，就不做bbirth过滤了
            if len(bbtags) >= 5 and identity_params.get('huaiyun') == "all" and identity_params.get('havebaby') == "all":
                return orconds

            orconds.append({"$or":[]})
            if len(bbtags_or) > 0:
                orconds[1]["$or"].append({"bbtag" : {"$in": bbtags_or}})
        else:
            return orconds


        if "huaiyun" in identity_params:
            if identity_params['huaiyun'] != "all":
                huaiyun_dates  = lib.merge_baby_time.mergeHuanyunTime(identity_params['huaiyun'])
                if huaiyun_dates is not None:
                    for dat in huaiyun_dates:
                        datval = huaiyun_dates[dat]
                        if isinstance(datval, dict):
                            orconds[1]['$or'].append({"bbbirth":get_date_range(datval)})
                        else:
                            orconds[1]['$or'].append({"bbbirth":get_date_range(huaiyun_dates)})
            else:
                orconds[1]['$or'].append({"bbbirth":{"$gt":comm.todaybyweeks(0).strftime("%Y-%m-%d")}})

        if "havebaby" in identity_params:
            if identity_params['havebaby'] != 'all':
                havebaby_dates  = lib.merge_baby_time.mergeHavebabyTime(identity_params['havebaby'])
                if havebaby_dates is not None:
                    for dat in havebaby_dates:
                        datval = havebaby_dates[dat]
                        if isinstance(datval, dict):
                            orconds[1]['$or'].append({"bbbirth":get_date_range(datval)})
                        else:
                            orconds[1]['$or'].append({"bbbirth":get_date_range(havebaby_dates)})
                            break
            else:
                orconds[1]['$or'].append({"bbbirth":{"$lte":comm.todaybyweeks(0).strftime("%Y-%m-%d")}})

        if len(orconds[1]['$or']) == 0:
            orconds.pop()
    elif appname == "pt": ## 怀孕管家的处理
        ## 怀孕管家的bbtag的值只有5和6。bbtag为6的时候，代表是准妈，5的时候代表是准爸
        ## 现在怀孕管家只处理怀孕状态的，其它的不做处理
        if "beiyun" in identity_params:
            bbtags.append(1)
            bbtags_or.append(1)
        if "other" in identity_params:
            bbtags.append(4)
            bbtags_or.append(4)
            bbtags.append(0)
            bbtags_or.append(0)
        if "huaiyun" in identity_params:
            bbtags.append(2)
            bbtags.append(0)
            bbtags.append(5)
            bbtags.append(6)
        if "havebaby" in identity_params:
            bbtags.append(3)
            bbtags.append(0)
            bbtags.append(5)
            bbtags.append(6)

        if len(bbtags) > 0:
            bbtags = list(set(bbtags))  ## 去重复
            orconds.append({"bbtag":{"$in": bbtags}})
            orconds.append({"$or":[]})
            if len(bbtags_or) > 0:
                orconds[1]["$or"].append({"bbtag" : {"$in": bbtags_or}})
        else:
            return orconds

        if "huaiyun" in identity_params:
            if identity_params['huaiyun'] != "all":
                huaiyun_dates  = lib.merge_baby_time.mergePtHuanyunTime(identity_params['huaiyun'])
                if huaiyun_dates is not None:
                    for dat in huaiyun_dates:
                        datval = huaiyun_dates[dat]
                        if isinstance(datval, dict):
                            orconds[1]['$or'].append({"bbbirth":get_date_range(datval)})
                        else:
                            orconds[1]['$or'].append({"bbbirth":get_date_range(huaiyun_dates)})
                            break
            else:
                orconds[1]['$or'].append({"bbbirth":{"$gt":comm.todaybyweeks(0).strftime("%Y-%m-%d")}})

        if "havebaby" in identity_params:
            if identity_params['havebaby'] != 'all':
                havebaby_dates  = lib.merge_baby_time.mergeHavebabyTime(identity_params['havebaby'])
                if havebaby_dates is not None:
                    for dat in havebaby_dates:
                        datval = havebaby_dates[dat]
                        if isinstance(datval, dict):
                            orconds[1]['$or'].append({"bbbirth":get_date_range(datval)})
                        else:
                            orconds[1]['$or'].append({"bbbirth":get_date_range(havebaby_dates)})
                            break
            else:
                orconds[1]['$or'].append({"bbbirth":{"$lte":comm.todaybyweeks(0).strftime("%Y-%m-%d")}})

        if len(orconds[1]['$or']) == 0:
            orconds.pop()

    return orconds

def deal_before_version(params):
    """处理vesion参数中的一个特殊情况  before2.0.0
    """
    version_str = params.get("version", None)
    if version_str is not None:
        versions = version_str.split(",")
        if "before2.0.0" in versions: 
            return {"version": {"$lt":"2.0"}}
    return None 

def deal_with_version_param(params):
    """处理verson参数，这个参数有点特殊
    """
    version_str = params.get("version", None)
    if version_str is not None:
        versions = version_str.split(",")
        verparams = set(map(lambda x: x[1:] if x.find('V') == 0 else x, versions))
        return ",".join(verparams)
        
    return None

def merge_version_param(params, bf_vers):
    """合并关于version的参数
    """
    ver_params = lib.params.get_params(params, "version", "$in")
    
    if ver_params is not None and len(ver_params) > 0:
        if "before2.0.0" in ver_params[1]['$in']:
            ver_params[1]['$in'].remove("before2.0.0")

        ver_params2 = {}
        ver_params2[ver_params[0]] = ver_params[1]
        ver_params = [bf_vers, ver_params2]
    else:
        ver_params = [bf_vers]

    ver_params = filter(lambda x:x is not None, ver_params)
    return ver_params

def get_uids_by_fids(fids):
    """根据传入的圈子id得到uid和fid的对应关系
       这里会使用缓存
    """
    caches = lib.cache.read(lib.cache.gen_cache_key(fids))
    if caches is None:
        wherec = {}
        wherec[fids[0]] = fids[1]
        uidfids = AppMamaquanMapiUidFid.getinstance().find(wherec, {"_id" : 0})
        userfids = {} 
        for uidfid in uidfids:
            if uidfid['uid'] in userfids:
                    userfids[uidfid['uid']].append(uidfid['fid'])
            else:
                userfids[uidfid['uid']] = [uidfid['fid']]
        lib.cache.write(lib.cache.gen_cache_key(fids), userfids)
        return userfids
    else:
        return caches

def get_fid_by_uid(uid):
    uid_cache_key = lib.cache.gen_cache_key(uid, False)
    cachefids = lib.cache.read(uid_cache_key)
    fids = []
    if cachefids is None or len(cachefids) == 0:
        fidscur = AppMamaquanMapiUidFid.getinstance().find({"uid":uid}, {"fid" : 1, "_id":0})
        for fid in fidscur:
            fids.append(fid)
        #if len(fids) > 0:
        #    lib.cache.write(uid_cache_key, fids)
    else:
        fids = cachefids
    return fids

def gen_cache_key(params):
    """去掉params中含有时间戳的数据
    """
    keys =  []
    def loop_dict(vs):
        vkeys = []
        for kk, vv in vs.iteritems():
            vkeys.append(kk)
            if isinstance(vv, dict):
                vkeys.append(loop_dict(vv))
            else:
                if isinstance(vv, int) and vv > 1000000000: ## 时间戳不参与生成key
                    continue
                vkeys.append(json.dumps(vv))
        return vkeys

    for k, v in params.iteritems():
        keys.append(k)
        if isinstance(v, dict):
            keys.append(json.dumps(loop_dict(v)))
        else:
            keys.append(v)
    return keys

def get_push_cache_by_page(params, page, perpage, cache_key=None):
    """获取缓存结果的分页
    """
    page, perpage = int(page), int(perpage)
    cache_key = gen_cache_key(params) if cache_key is None else cache_key
    datas = lib.cache.read(lib.cache.get_cache_key(cache_key))
    if datas is not None:
        sumcount = len(datas)
        pagecount = math.floor((sumcount + perpage - 1) / perpage )
        if page > pagecount:
            page = pagecount
        start = (page - 1) * perpage
        return datas[start: start + perpage]
    return None  

def handle_request(req_res, page=None, perpage=None, webrun=False, callfunc=None):
    """处理请求，两个接口的参数和查询完全一致
       返回为一个元组(结果, 处理过的请求参数, 是否是分页)
    """
    if req_res is None or len(req_res) == 1:
        req_res = [] if req_res is None else req_res
        return (None, None, False) 
    t, token, params = req_res

    wherec   = [] 

    wherec.append(lib.params.get_params(params, "city", "$in"))
   
        
    wherec.append(lib.params.get_params(params, "startview", "$gte", tf='ut', type='int'))
    wherec.append(lib.params.get_params(params, "endview", "$lt", tf='ut', type='int'))
    wherec.append(lib.params.get_params(params, "downloadstart", "$gte", tf='t', type='int'))
    wherec.append(lib.params.get_params(params, "downloadend", "$lt", tf='t', type='int'))
    wherec.append(lib.params.get_params(params, "nonusestart", "$gte", tf='ut', type='int'))
    wherec.append(lib.params.get_params(params, "nonuseend", "$lt", tf='ut', type='int'))
    wherec.append(lib.params.get_params(params, "forum", "$in", tf="fid", type="int"))

    wherec = lib.params.combine_params(wherec)
    
    identity_condis = get_identity_condi(params) 

    if identity_condis is not None and len(identity_condis) > 0:
        wherec["$and"] = identity_condis  

    cache_key = gen_cache_key(params)

    ### 参数的处理在这里结束，在这里处理缓存 =====================================
    ### 开始验证是否有缓存，如果有缓存使用缓存返回
    if page is not None and perpage is not None:  # 处理分页
        res = get_push_cache_by_page(params, page, perpage, cache_key)
        if res : 
            return (res, params, True) 
        else:
            return ([], params, True)
    else:
        datas = lib.cache.read(lib.cache.get_cache_key(cache_key))
        if datas is not None and callfunc is None:
            return (datas, params, False)

        if isinstance(datas, list) and callfunc is not None:
            for data in datas:
                callfunc(data)
            return True

    ## 结束缓存的处理 ============================================================
    ## 处理版本
    bf_vers = deal_before_version(params)
    params['version'] = deal_with_version_param(params)

    ver_params = merge_version_param(params, bf_vers)

    if ver_params is not None and len(ver_params) > 0:
        wherec["$or"] =  ver_params  

    ## 将传递过来的platform的参数转为数据库定义的格式
    invert_platforms = comm.invert_dict(conf.PLATFORMS)   
    
    appname = params.get("appname", None)
    if appname == 'pt':
        dbconn = AppHuaiyunLastvisitToken.getinstance()
    else:
        dbconn = AppMamaquanLastvisitToken.getinstance()
        
    if wherec is  None or len(wherec) == 0: 
        wherec = {}

    ##====================================================================begin
    ## 去掉devicetoken为空和UID为空的情况的数据
    ## {"devicetoken":{"$ne":null}, "platform":{"$in":[1,5]}}, {"platform":2}

    beforenmonthtime = comm.get_before_month_time(0.24)  # N个月前的时间戳

    platforms = params.get("platform", "all")
    if "$or" not in wherec: wherec["$or"] = []

    if platforms == "all":
        wherec["$or"].append({"platform" : conf.PLATFORMS["Android"], "uid":{"$nin":["", 0]}, "ut": {'$gte': beforenmonthtime}})
        if appname == "pt" :
            wherec["$or"].append({"platform" : conf.PLATFORMS["Android"], "mobileID":{"$nin":[None, "", 0]}, "ut": {'$gte': beforenmonthtime}})
        wherec["$or"].append({"devicetoken":{"$ne":None},
                              "platform" : {"$in" : [conf.PLATFORMS['IPhone'], conf.PLATFORMS['Ipad']]}})

    else:
        platforms = platforms.split(",")
        if "Ipad" in platforms or "IPhone" in platforms:
            wherec["$or"].append({"devicetoken":{"$ne":None},
                                  "platform" : {"$in" : [conf.PLATFORMS['IPhone'], conf.PLATFORMS['Ipad']]}})
        if "Android" in platforms:
            wherec["$or"].append({"platform" : conf.PLATFORMS["Android"], "uid":{"$nin":["", 0]}, "ut": {'$gte': beforenmonthtime}})
            if appname == "pt" :
                wherec["$or"].append({"platform" : conf.PLATFORMS["Android"], "mobileID":{"$nin":[None, "", 0]}, "ut": {'$gte': beforenmonthtime}})

    #wherec['$and'].append({"uid":{"$ne": None}})
    ##=====================================================================end
    print wherec

    pushinfos = dbconn.find(wherec, {"_id":0, "uid":1, "city":1, "bbbirth":1, "channel":1,\
                                     "version":1, "bbtag":1, "platform":1, "t":1,\
                                      "devicetoken":1, "mobileID":1, "sf": 1})
    ## 如果没有查询圈子的话，就直接返回总数
    if webrun:
        result_count = pushinfos.count()
        lib.cache.write(lib.cache.get_cache_key(cache_key), result_count)
        return (result_count, params, False)

    res_pushinfos = [] 
    #print pushinfos.batch_size(1024)
    if callfunc is not None:
        ## iphone用户先发，活跃用户先发
        pushinfos.sort("platform", pymongo.ASCENDING )
        #pushinfos.sort([("platform", pymongo.ASCENDING), ("ut", pymongo.DESCENDING)])
    for pushinfo in pushinfos: 
        pushinfo['platform'] = invert_platforms.get(pushinfo['platform'])
        ## 回调函数
        callfunc(pushinfo)
        res_pushinfos.append(pushinfo)
    ## 将查询的结果写入缓存
    if callfunc is None: ## 只有取总数的时候才写入缓存
        lib.cache.write(lib.cache.get_cache_key(cache_key), res_pushinfos)
    return (res_pushinfos, params, False)
        
    return (None, params, False)


@mmstats.app.route('/get_push_userinfo', methods=['GET',])
def get_push_userinfo(): 
    st = time.clock()
    res  = lib.params.validate_params(request, "PUSH", True)

    if res is None or len(res) == 0:
        return lib.params.response_std([], 0, -101)

    page, perpage =  request.args.get('page', None),  request.args.get('perpage', None)
    result, _ , ispage = handle_request(res, page, perpage, True)

    ot = time.clock() - st
    logger.info("get_push_userinfo offtime : %f" % ot)
    
    if ispage == False:
        if result is None:
            return lib.params.response_std({"count":0}, 1)
        else:
            try:
                result = int(result)
            except:
                pass
            if isinstance(result, int):
                return lib.params.response_std({"count":result})
            else:
                return lib.params.response_std({"count":len(result)}) 
    else:
        return lib.params.response_std(result) 
            

@mmstats.app.route('/find_push_device', methods=['GET',])
def find_push_device():
    res  = lib.params.validate_params(request, "PUSH", True)
    ## 查看wid参数是否存在
    wid = request.args.get('wid', None)
    if wid is None: 
        return lib.params.response_std([], 1)

    ## 不关心是否是分页的情况
    #result, params, _ = handle_request(res) 
    
    ## 启用一个服务去调用它的接口
    if res is not None and len(res) > 0:
        AppMamaquanPushQueue.getinstance().push({"type":"push", "wid":wid, "appname":res[2]['appname']}, json.dumps(res))
        return lib.params.response_std([])
    else:
        return lib.params.response_std([], 0, -101)


@mmstats.app.route('/rm_dev_token', methods=['GET',])
def rm_dev_token():
    res = lib.params.validate_params(request, "PUSH", True)
    if res is not None and len(res) > 0:
        _,_,reqdata = res
        _del = reqdata['del']
        norm_tokens = []
        if _del > 1:
            ## token在指定的_del小时内删除，暂未实现
            pass
        elif _del == 1:
            dbconn, rmdbconn = None, None
            appname = reqdata.get("appname", None)
            if appname == 'pt':
                dbconn   = AppHuaiyunLastvisitToken.getinstance()
                rmdbconn = AppHuaiyunLastvisitTokenRm.getinstance()
            else:
                dbconn   = AppMamaquanLastvisitToken.getinstance()
                rmdbconn = AppMamaquanLastvisitTokenRm.getinstance()
            
            ## 立即删除
            for token in reqdata["tokens"]:        
                platform = 0
                try:
                    platform = int(token["platform"])
                except:
                    pass
            
                olddata = dbconn.find_one({
                    "devicetoken" :  token["token"]
                    })
                 
                res =  dbconn.remove({
                    "devicetoken" :  token["token"]
                    })
                ## 检查是否删除成功，如果没有删除成功，就会将没有删除的token返回回去
                if res is None or res.get("n", 0) == 0:
                    norm_tokens.append(token)
                else:
                    olddata.pop("_id")
                    olddata['rt'] = int(time.time())
                    rmdbconn.insert(olddata)

            if len(norm_tokens) > 0:
                return lib.params.response_std({"tokens":norm_tokens}, 1)
            else:
                return lib.params.response_std({"tokens":norm_tokens}, 1)
        else:
            return lib.params.response_std({"tokens":[]}, 1)
            
    else:
        return lib.params.response_std({"tokens":[]}, 0, -101)

@mmstats.app.route('/get_devicetoken', methods=['GET',])
def get_devicetoken():
    res = lib.params.validate_params(request, "PUSH", True)
    if res is not None and len(res) > 0:
        _,_,reqdata = res
        if "uid" in reqdata:
            appname = reqdata.get("appname", None)
            uid     = reqdata.get("uid", None)
            if appname == 'pt':
                dbconn   = AppHuaiyunLastvisitToken.getinstance()
            else:
                dbconn   = AppMamaquanLastvisitToken.getinstance()

            result = dbconn.find({"uid": uid}, {"devicetoken":1, "sf":1, "_id":0})
            if result:
                tokens = []
                for token in result:
                    if 'devicetoken' in token:
                        sf = 0
                        try:
                            sf = int(token.get('sf', 0))
                        except:
                            sf = 0
                        tokens.append({"token": token['devicetoken'], "sf": sf})
                if tokens:
                    return lib.params.response_std({"tokens":tokens}, 1)
                else:
                    return lib.params.response_std({"tokens":[]}, 1)
            else:
                return lib.params.response_std({"tokens":[]}, 1)
        else:
            return lib.params.response_std({"tokens":[]}, 1)
    else:
        return lib.params.response_std({"tokens":[]}, 0, -101)

@mmstats.app.route('/get_userdevs', methods=['GET',])
def get_userdevs():
    res = lib.params.validate_params(request, "PUSH", True)
    if res is not None and len(res) > 0:
        _,_,reqdata = res
        if "uid" in reqdata:
            appname = reqdata.get("appname", None)
            uid     = reqdata.get("uid", None)
            if appname == 'pt':
                dbconn   = AppHuaiyunLastvisitToken.getinstance()
            else:
                dbconn   = AppMamaquanLastvisitToken.getinstance()

            result = dbconn.find({"uid": uid}, {"_id":0})
            if result:
                infos = list()
                for res in result:
                    infos.append(res)
                return lib.params.response_std({"devices": infos}, 1)
            else:
                return lib.params.response_std({"devices":[]}, 1)
        else:
            return lib.params.response_std({"devices":[]}, 1)
    else:
        return lib.params.response_std({"devices":[]}, 0, -101)

import re

@mmstats.app.route('/get_push_num', methods=['GET',])
def get_push_num():
    res = lib.params.validate_params(request, "PUSH", True)
    if res is not None and len(res) > 0:
        _,_,reqdata = res
        counts = {"total": 0, "android": 0, "old_android": 0, "ios": 0}
        if "wid" in reqdata:
            wid = reqdata.get("wid", None)
            with open(os.path.join(conf.log_dir, "run_push_queue_redis.py.log")) as runlog:
                try:
                    pat = "Finish push %d total count" % int(wid)
                except:
                    return lib.params.response_std({"nums": {}}, 0, "wid wrong")

                p = re.compile(r'\[(\d+)\]')
                for line in runlog:
                    if pat in line:
                        nums = p.findall(line)
                        if nums:
                            counts['total'] = nums[0] if len(nums) > 0 else counts['total']
                            counts['ios']   = nums[1] if len(nums) > 1 else counts['ios']
                            counts['old_android'] = nums[2] if len(nums) > 2 else counts['old_android']
                            counts['android'] = nums[3] if len(nums) > 3 else counts['android']

            return lib.params.response_std({"nums": counts}, 1)
        else:
            return lib.params.response_std({"nums": counts}, 1)
    else:
        return lib.params.response_std({"nums": {}}, 0, -101)

"""
获取近N个月的活跃用户的uid
"""
# 近N个月的活跃用户的的文件
MONTH_NUM = 3
ACTIVE_USER_MONTH_FILE = os.path.join(conf.cache_dir, "__active_user_%d_month.csv" % MONTH_NUM)
ACTIVE_USER_MONTH_INDEX_FILE = os.path.join(conf.cache_dir, "__active_user_%d_month.idx" % MONTH_NUM)
ACTIVE_USER_MONTH_KEY = "bigdata_active_user_month_%d" %  MONTH_NUM
ACTIVE_USER_MONTH_PAGE_SIZE = 5000
@mmstats.app.route("/get_active_by_months", methods=['GET',])
def get_active_by_months():
    res = lib.params.validate_params(request, "KENG", True)
    if res is not None and len(res) > 0:
        _,_,reqdata = res
        redisconn = RedisConn.getinstance()
        page = int(reqdata.get("page", 1))
        # 从每天生成的索引文件中获取分页索引
        with open(ACTIVE_USER_MONTH_INDEX_FILE) as idxaf:
            idxdict = json.loads(idxaf.read())
        # 从redis中获取总共有多少数据
        uids = {"total": redisconn.get(ACTIVE_USER_MONTH_KEY), "pages":0, "uids": []}
        uids['pages'] = (int(uids['total']) + ACTIVE_USER_MONTH_PAGE_SIZE - 1) / ACTIVE_USER_MONTH_PAGE_SIZE
        # 打开缓存数据文件
        with open(ACTIVE_USER_MONTH_FILE) as af:
            # 根据分页索引返回分页数据
            af.seek(idxdict.get(str(page), 0))
            count = 0
            for line in af:
                line = line.strip()
                try:
                    if count <= ACTIVE_USER_MONTH_PAGE_SIZE:
                        uids['uids'].append(int(line))
                        count += 1
                    else:
                        break
                except Exception, e:
                    print e
        return lib.params.response_std(uids, 1)
    else:
        return lib.params.response_std({"uids": {}}, 0, -101, errmsg="token错误")

"""
根据时间戳获取最近N分钟的活跃用户
限定N分钟才能请求一次
"""
ACTIVE_USER_STEP_TIME = 5
ACTIVE_USER_LAST_NM_TIME_KEY = "active_user_last_%dm_time" % ACTIVE_USER_STEP_TIME
ACTIVE_USER_LAST_NM_PAGE_SIZE = ACTIVE_USER_MONTH_PAGE_SIZE
ACTIVE_USER_LAST_NM_CACHE_KEY= "active_user_last_nm_cache"
@mmstats.app.route("/get_active_by_time", methods=['GET',])
def get_active_by_time():
    res = lib.params.validate_params(request, "KENG", True)
    if res is not None and len(res) > 0:
        _,_,reqdata = res
        redisconn = RedisConn.getinstance()
        curtime = int(time.time())
        page = int(reqdata.get("page", 1))
        page = 1 if page <= 0 else page
        try:
            time_ = int(reqdata.get("time", None))
        except:
            time_ = curtime

        appname = reqdata.get("appname", None)
        if appname == 'pt':
            dbconn = AppHuaiyunLastvisitToken.getinstance()
        else:
            dbconn = AppMamaquanLastvisitToken.getinstance()
        ## 生成各种key
        # 上一次的页面总数
        activeuser_pages_key = "%s_pages" % ACTIVE_USER_LAST_NM_TIME_KEY
        # cache的key
        activeuser_cache_key = "%s_%d" % (ACTIVE_USER_LAST_NM_CACHE_KEY, time_) 
        lastpages = redisconn.get(activeuser_pages_key)
        lastpages = 0 if lastpages is None else int(lastpages)
        # 判断page不能大于page总数
        page = lastpages if page > lastpages and lastpages > 0 else page
        # 生成上一次的时间key
        activeuser_time_key = "%s_%d" % (ACTIVE_USER_LAST_NM_TIME_KEY, page)

        lastntime = redisconn.get(activeuser_time_key)
        lastntime = 0 if lastntime is None else int(lastntime)
        # 每次请求时间不得小于N分钟,分页除外
        if curtime - lastntime < ACTIVE_USER_STEP_TIME * 60:
            return lib.params.response_std({"uids": {}}, 0, -102, errmsg="在%d分钟之内只可以调用一次" % ACTIVE_USER_STEP_TIME)
        ## 先找cache是否存在
        response_ = lib.cache.read(activeuser_cache_key)
        if not response_:
            ##在mongo中取出N分钟之内的活跃用户的uid
            results = dbconn.find({"ut": {"$gt": time_ - ACTIVE_USER_STEP_TIME * 2 * 60, "$lt": time_},
                                   "uid":{"$nin":[0, None]}}, {"uid": 1, "_id": 0})
            response_ = {
                "total": 0,
                "pages": 0,
                "uids": []
            }
            c = 0
            for result in results:
                response_['uids'].append(result.get("uid", 0))
                c += 1
            response_['total'] = c
            response_['pages'] = (response_['total'] + ACTIVE_USER_LAST_NM_PAGE_SIZE - 1) / ACTIVE_USER_LAST_NM_PAGE_SIZE
            # 缓存数据到文件系统
            lib.cache.write(activeuser_cache_key, response_)
            # 设置一些控制性的值
            redisconn.set(activeuser_time_key, curtime)
            redisconn.set(activeuser_pages_key, response_['pages'])
        # 限定page不能大于page总数
        page = response_['pages'] if page > response_['pages'] else page
        # 分页
        response_['uids'] = response_['uids'][(page - 1) * ACTIVE_USER_LAST_NM_PAGE_SIZE:
                                                       page * ACTIVE_USER_LAST_NM_PAGE_SIZE]
        return lib.params.response_std(response_, 1)
    else:
        return lib.params.response_std({"uids": {}}, 0, -101, errmsg="token错误")

