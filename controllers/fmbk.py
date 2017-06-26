#!/usr/bin/python
# -*- coding: utf-8 -*-
#encoding=utf-8
"""
非买不可的统计专用
"""
import mmstats
from flask import request
from mmstats import comm
from mmstats import lib
from mmstats.models.AppMamaquanFsbkRecmdRidPv import AppMamaquanFsbkRecmdRidPv
from mmstats.models.AppHuaiyunFsbkRecmdRidPv import AppHuaiyunFsbkRecmdRidPv
from mmstats.models.AppMamaquanFsbkRecmdListVisitedNum import AppMamaquanFsbkRecmdListVisitedNum 

import os
import datetime
import pymongo


logger = comm.getlogger("%s.log" % __file__, ap=True)

@mmstats.app.route('/get_fmbk_recmd_pv', methods=['GET',])
def get_fmbk_recmd_pv():
    """
        非卖不可推荐详情页接口
    """
    res  = lib.params.validate_params(request, "FMBK")
    if res is not None and len(res) > 0:
        t, _, params = res
        date = params.get("date", None)
        rids = params.get("rids", None)
        wherec = {}
        if rids is None or len(rids) == 0:
            return lib.params.response_std({}, 0)
        if date is None: # 如果date是空，那么就查询所有的
            wherec = {"rid":{"$in": rids}}
        else:
            wherec = {"rid":{"$in": rids}, "date":date}

        appname = params.get("appname", "mmq")
        if appname == "pregnancy":
            results = AppHuaiyunFsbkRecmdRidPv.getinstance().find(wherec ,{"num":1, "rid":1, "_id":0})
        else:
            results = AppMamaquanFsbkRecmdRidPv.getinstance().find(wherec ,{"num":1, "rid":1, "_id":0})

        rid_pv_count = {}
        for result in results:
            #pv_sum_count += result["num"]
            rid = result['rid']
            if rid in rid_pv_count:
                rid_pv_count[rid] += result['num'] 
            else:
                rid_pv_count[rid] = result['num'] 

        return lib.params.response_std(rid_pv_count, 1)

    return lib.params.response_std({}, 0)
      
   
@mmstats.app.route('/get_fmbk_tagid_stat', methods=['GET',])
def get_fmbk_tagid_stat():
    res  = lib.params.validate_params(request, "FMBK", True)
    if res is not None and len(res) > 0:
        t, _, params = res
        sdate  = params.get('sdate', None)
        edate  = params.get('edate', None)
        tagIds = params.get('tagIds', None)
        wherec = {}
        if tagIds is None or len(tagIds) == 0:
            return lib.params.response_std({}, 0)

        tagIds = [int(tagId) for tagId in tagIds] ## 转成整数

        if sdate is None and edate is None:
            wherec = {"tagId": {"$in": tagIds}}
        elif sdate is not None and edate is None:
            wherec = {"tagId": {"$in": tagIds}, "date":{"$gte":sdate}}
        elif sdate is None and edate is not None:
            wherec = {"tagId":{"$in": tagIds}, "date": {"$lte": edate}}
        else:
            wherec = {"tagId":{"$in": tagIds}, "date": {"$gte":sdate, "$lte": edate}}

        results = AppMamaquanFsbkRecmdListVisitedNum.getinstance().find(wherec ,{"tagId":1, "pv":1, "uv":1, 'date':1, "_id":0})
        tagId_count = {}
 
        for result in results:
            redate = result['date']
            tagId  = result['tagId']
            if redate in tagId_count:
                if tagId in tagId_count[redate]:
                    tagId_count[redate][tagId]['pv'] += result['pv'] 
                    tagId_count[redate][tagId]['uv'] += result['uv'] 
                else:
                    tagId_count[redate][tagId] = {'pv': result['pv'], 'uv':result['uv']}
            else:
                tagId_count[redate] = { tagId: {'pv': result['pv'], 'uv':result['uv'] } }

        total_tagId = {}
        if 0 in tagIds:   ## 是否有mmq的统计需求
            wherec.pop("tagId") 
            results = AppMamaquanFsbkRecmdListVisitedNum.getinstance().find(wherec ,{"pv":1, "uv":1, 'date':1, "_id":0})

            for result in results:
                redate = result['date']
                if redate in total_tagId:
                    total_tagId[redate]['uv'] += result['uv']
                    total_tagId[redate]['pv'] += result['pv']
                else:
                    total_tagId[redate] = { 'pv' : result['pv'], 'uv' : result['uv'] }

            for redate in tagId_count:
                tagId_count[redate][0]  = total_tagId[redate]
            
        return lib.params.response_std(tagId_count, 1)

    return lib.params.response_std({}, 0, errno=-1, errmsg="token verification failed!")


@mmstats.app.route('/get_fmbk_recmd_pv_sort', methods=['GET',])
def get_fmbk_recmd_pv_sort():
    """
        非卖不可推荐详情页接口(按pv排序，并分页)
        根据传入一个日期，返回日期后N天的数据，N也是一个参数，如果未传默认为7天
    """
    res  = lib.params.validate_params(request, "FMBK")
    if res is not None and len(res) > 0:
        t, _, params = res
        date = params.get("date", None)
        nday = params.get("nday", 7)
        page = params.get("page", None)
        pagesize = params.get("pagesize", None)
        if page is None:
            page = 1
        else:
            try:
                page = int(page)
            except:
                page = 1
        
        if page < 1:
            page = 1

        if pagesize is None:
            pagesize = 100
        else:
            try:
                pagesize = int(pagesize)
            except:
                pagesize = 100

        if pagesize > 2000:
            pagesize = 2000

        if pagesize < 10:
            pagesize = 10

        try:
            nday = int(nday)
        except:
            nday = 7

        if nday > 30:
            nday = 30

        if nday < 1:
            nday = 1

        if date is None:
            date = datetime.datetime.now()
        else:
            try:
                date = datetime.datetime.strptime(date, "%Y-%m-%d")
            except:
                date = datetime.datetime.now()

        startdate = date - datetime.timedelta(days=nday)

        date = date.strftime("%Y-%m-%d")
        startdate = startdate.strftime("%Y-%m-%d")

        wherec = {
            "date": {"$gte": startdate, "$lte": date}
        }

        appname = params.get("appname", "mmq")

        keys = {"appname": appname, "date": date, "nday": nday}
        keys = lib.cache.get_cache_key(keys)

        response_ = lib.cache.read(keys, 300)
        print "======get_fmbk_recmd_pv_sort size %d" % len(response_) if response_ is not None else 0 
        if not response_: 
            if appname == "pregnancy":
                results = AppHuaiyunFsbkRecmdRidPv.getinstance().find(wherec ,{"date": 1, "num":1, "rid":1, "_id":0})
            else:
                results = AppMamaquanFsbkRecmdRidPv.getinstance().find(wherec ,{"date": 1, "num":1, "rid":1, "_id":0})

            if results:
                results = results.sort([("date", pymongo.DESCENDING), ("num", pymongo.DESCENDING)])
                
                response_ = []
                for result in results:
                    response_.append({"date": result.get("date"), "pv": result.get("num", 0), "rid": result.get("rid", 0)})
                lib.cache.write(keys, response_)  
         
        if not response_:
            return lib.params.response_std({}, 0, errno=-301, errmsg="no data")
       
        pos = (page - 1) * pagesize
        response_data = response_[pos: pos+pagesize]

        return lib.params.response_std({"pvs": response_data, "total": len(response_)}, 1)

    return lib.params.response_std({}, 0, errno=-300, errmsg="token wrong")
