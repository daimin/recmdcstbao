#!/usr/bin/env python
# -*- coding:utf-8 -*-   
#encoding=utf-8
#author=daimin

import os
import sys 
import inspect
import conf
import datetime
import logging
from logging.handlers import RotatingFileHandler
import time
import hashlib
import struct
import socket
import urllib
import json
from sqlalchemy.ext.declarative import DeclarativeMeta

from itertools import izip 

def getlogger(logfile = None, onlyfile=False, ap=False):
    """获取日志对象
    """
    _logger = logging.getLogger("default_logger" if logfile is None else logfile)
    if len(_logger.handlers) == 0:
        if logfile == None:
            logfile = os.path.join(conf.log_dir, datetime.datetime.now().strftime("%Y%m%d") + ".log")
        else:
            ## 检查下logfile是否是.pyc文件
            ## 防止在绝对路径运行下__file__返回绝对路径，造成log文件路径不对
            logfile = os.path.basename(logfile)  
            if ".pyc" in logfile:
                logfile = logfile.replace(".pyc", ".py")

            if ap:
                stack = inspect.stack()  # 得到当前函数的调用栈
                exefile = os.path.basename(stack[-1][1]) # 找到最开始的调用者
                filesps = os.path.splitext(exefile)
                if len(filesps) > 1:
                    logfile = "%s-%s" % (filesps[0], logfile)

            logfile = os.path.join(conf.log_dir, logfile)

        hdlr = RotatingFileHandler(logfile, maxBytes=256*1024*1024, backupCount=7)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        hdlr.setLevel(logging.INFO)
        _logger.addHandler(hdlr)
        
        if onlyfile == False:
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            ch.setLevel(logging.INFO)
            _logger.addHandler(ch)

        _logger.setLevel(logging.DEBUG)
        _logger.debug("initialize logger")

    return _logger
    
'''
检验一个变量是否存在
'''
def  isset(v):
    try:
        type (eval(v))
    except:
        return   0
    else:
        return   1    


def utf82gbk(tstr):
    """转换UTF-8格式的编码为GBK编码
    """
    return tstr.decode("UTF-8").encode("GBK")
    
def datetime2timestamp(dt):
    return time.mktime(dt.timetuple())

def datetime2timestamp2(dt):
    """将datetime转换成日期秒数的方式
    """
    ndt = datetime.datetime(year=dt.year, month=dt.month, day=dt.day)
    return int(time.mktime(ndt.timetuple()))

def timestamp2datetime(ts):
    if ts is None:
        return datetime.datetime.now()
    return datetime.datetime.fromtimestamp(ts)

def todaybyweeks(weeks, isadd=False):
    """计算出weeks个周的日期
    """
    today = datetime.date.today()
    if isadd:
        return today + datetime.timedelta(weeks = weeks )
    else:
        return today - datetime.timedelta(weeks = weeks )


def get_before_month_time(n):
    """
    得到过去N个月的时间戳
    :param n: 月份数，可以为小数
    :return:
    """
    days = int(n * 30)
    now = datetime.datetime.now()
    lmt = now - datetime.timedelta(days=days)
    return datetime2timestamp2(lmt)


def usd2rmb(uds):
    return int((uds+0.1) * 6)
    
def dict2param(d):
    if not isinstance(d, dict):
        return ''
    params = []
    for (key, val) in d.items():
        params.append("%s=%s" %(key, val))
        
    return "&".join(params)


def md5(src, t='lower'):
    if t is 'lower':
        return hashlib.md5(src).hexdigest().lower()
    else:
        return hashlib.md5(src).hexdigest().upper()

def get_yes_day_time(day):
    yesday = day - datetime.timedelta(days = 1 )
    return (int(datetime2timestamp(datetime.datetime(day.year, day.month, day.day))),\
            int(datetime2timestamp(datetime.datetime(yesday.year, yesday.month, yesday.day))))
    

def ip2long(ipstr):
    if ipstr is None or ipstr == '' or ipstr == 'null': return 0
    return struct.unpack("!I", socket.inet_aton(ipstr))[0]



def parse_qs(qs):
    if qs is None or len(qs.strip()) == 0:
        return None
    qs = qs.strip().strip("&")
    qsda = qs.split("&")
    if len(qsda) == 0: return None
    return dict(map(lambda x:x.strip().split("=") if "=" in x else None, qsda))

def urldecode(data):
    try:
        return urllib.unquote(data).decode('utf-8')
    except:
        return None

def urlencode(data):
    try:
        return urllib.quote(data.encode("utf-8"))
    except:
        return None
    
import re
def stripslashes(s):
    r = re.sub(r"\\(n|r)", "\n", s)
    r = re.sub(r"\\", "", r)
    return r


bbtags = {1: u"备用", 2: u"怀孕中", 3: u"有宝宝", 4: u"其它"}
def bbtag_display(bbtag):
    global bbtags
    try:
        bbtag = int(bbtag)
    except:
        bbtag = 0
    return bbtags.get(bbtag, u"未知")

import xml.dom.minidom

def load_xml_config(path):
    """分析关于运行参数的xml配置文件
    """
    confdata = {"module":{}}
    def get_ele_val(node, name):
        sms = node.getElementsByTagName(name)
        if sms is not None and len(sms) > 0:
                return sms[0].childNodes[0].nodeValue  
        return None
    
    def get_module_cfg(mnode):
        cfg = {"hdfs":{}}
        cfg['rumtime'] = get_ele_val(mnode, 'runtime')
        for hdfs_node in mnode.getElementsByTagName("hdfs"):
            hdfscfg = {}
            hdfscfg["split-token"] = hdfs_node.getAttribute("split-token")
            hdfscfg["nkeys"]       = hdfs_node.getAttribute("nkeys")
            cfg['hdfs'][ hdfs_node.childNodes[0].nodeValue] = hdfscfg
        return cfg
            
                                                                                                                            
    with open(path) as cfgfile:                                                                                                          
        doc = xml.dom.minidom.parse(cfgfile)
        for node in doc.getElementsByTagName("config"):
            confdata['spark-master'] = get_ele_val(node, "spark-master")
            confdata['hdfs-master'] = get_ele_val(node, "hdfs-master")
            for mudule_node in node.getElementsByTagName("module"):
                confdata['module'][mudule_node.getAttribute("name")] = get_module_cfg(mudule_node)
                
    return confdata

def invert_dict(d):  
    return dict(izip(d.itervalues(),d.iterkeys()))


class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata' and x.find("query") != 0]:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data)     # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:    # 添加了对datetime的处理
                    if isinstance(data, datetime.datetime):
                        fields[field] = data.isoformat()
                    elif isinstance(data, datetime.date):
                        fields[field] = data.isoformat()
                    elif isinstance(data, datetime.timedelta):
                        fields[field] = (datetime.datetime.min + data).time().isoformat()
                    else:
                        fields[field] = None
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)

