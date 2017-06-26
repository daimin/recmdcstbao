#!/usr/bin/env python
# -*- coding:utf-8 -*-
#encoding=utf-8

"""
用来转换怀孕和有宝宝的查询的时间
"""
from mmstats import comm

def mergeHuanyunTime(huaiyun):
    result = {}
    total = len(huaiyun)
    if len(huaiyun) == 2:
        if huaiyun.get('huaiyun_1to12week') and huaiyun.get('huaiyun_13to25week'):
            result['0'] = {'s':huaiyun['huaiyun_1to12week']['s'], 'e':huaiyun['huaiyun_13to25week']['e']}
        elif huaiyun.get('huaiyun_13to25week') and huaiyun.get('huaiyun_26to40week'):
            result['0'] = {'s':huaiyun['huaiyun_13to25week']['s'], 'e':huaiyun['huaiyun_26to40week']['e']}
        else:
            result = {'0':huaiyun.get('huaiyun_1to12week'), '1':huaiyun.get('huaiyun_26to40week')}
    else:
        result = huaiyun.get('huaiyun_1to12week') or huaiyun.get('huaiyun_13to25week') or huaiyun.get('huaiyun_26to40week')
    return result

def mergePtHuanyunTime(huaiyun):
    """转换怀孕管家的怀孕时间
    """
    result_idxs, result = [], {}
    maphuaiyun = {}
    for i in xrange(1, 41):
        maphuaiyun["huaiyun_%dweek" % i] = i

    maphuaiyunr = comm.invert_dict(maphuaiyun)
    ##合并相连的值
    #"huaiyun_1week" :{"s":1403063644, "e":1410321244},"huaiyun_2week" :{"s":1403063644, "e":1410321244},
    keys = huaiyun.keys()

    for k in keys:
        if k in maphuaiyun:
            result_idxs.append(maphuaiyun.get(k))

    if len(result_idxs) > 0:
        result_idxs        = list(set(result_idxs))
        sorted_result_idxs = sorted(result_idxs)
        reslen, pre, next  = len(sorted_result_idxs), -1, 0
        discons = {}
        def add_discons(discons, next, idx):
            if next not in discons:
                discons[next] = [ idx ]
            else:
                discons[next].append(idx)
                next += 1
            return next

        for i in xrange(reslen):
            if sorted_result_idxs[i] - pre > 1:
                ## 不连续
                next = add_discons(discons, next, sorted_result_idxs[i])

            if i < reslen - 1:
                if sorted_result_idxs[i+1] - sorted_result_idxs[i] > 1:
                    next = add_discons(discons, next, sorted_result_idxs[i])
            else:
                next = add_discons(discons, next, sorted_result_idxs[i])

            pre = sorted_result_idxs[i]

        for dkey in discons:
            discon = list(set(discons[dkey]))
            ## 为了兼容请求端的数据排序
            discon = sorted(discon, reverse=True)

            if len(discon) == 2:
                result[dkey] = {'s': (huaiyun[maphuaiyunr.get(discon[0])])['s'], 'e':
                                     (huaiyun[maphuaiyunr.get(discon[1])])['e']}
            elif len(discon) == 1:
                result[dkey] = {'s': (huaiyun[maphuaiyunr.get(discon[0])])['s'], 'e':
                                     (huaiyun[maphuaiyunr.get(discon[0])])['e']}
    return result


def mergeHavebabyTime(havebaby):
    result = {}
    reversemaphavebaby = {}
    result1 = []
    result2 = []
    result3 = {}
    start = end = ''
    onetotwomonth = False
    maphavebaby = {'havebaby_1mon':1, 'havebaby_2mon':2, 'havebaby_3mon':3, 'havebaby_4mon':4, 'havebaby_5mon':5,
                   'havebaby_6mon':6,'havebaby_7mon':7, 'havebaby_8mon':8, 'havebaby_9mon':9, 'havebaby_10mon':10,
                   'havebaby_11mon':11, 'havebaby_12mon':12,'havebaby_1to2year':13, 'havebaby_2to3year':14,
                   'havebaby_3to7year':15, 'havebaby_7to14year':16, 'havebaby_above14':17}
    for line2 in maphavebaby:
        reversemaphavebaby[maphavebaby[line2]] = line2
    keys = havebaby.keys()
    if keys:
        for line in keys:
            if line in maphavebaby:
                result1.append(maphavebaby.get(line))
        if result1:
            sort_result1 = sorted(result1)

            for line1 in sort_result1:
                pre = sort_result1.count(int(line1) - 1)
                behind = sort_result1.count(int(line1) + 1)
                start = start if pre > 0 else line1
                end = end if behind > 0 else line1
                if start and end:
                    result2.append({'s':start,'e':end})
                    start = end = ''
            j = 0
            if result2:
                for line3 in result2:
                    s = reversemaphavebaby[line3['s']]
                    e = reversemaphavebaby[line3['e']]
                    result3[j] = {'s':havebaby[e]['s'], 'e':havebaby[s]['e']}
                    j = j + 1
    return result3