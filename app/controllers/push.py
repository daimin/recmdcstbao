#!/usr/bin/python
# -*- coding: utf-8 -*-
#encoding=utf-8
"""
push系统专用接口
"""
from flask import request, json
import comm
import lib
import conf

import math
import time
import os
import sys

logger = comm.getlogger("%s.log" %  __file__, ap=True)
sys.path.append('../')

from index import app

@app.route('/test', methods=['GET',])
def test(): 
    return lib.params.response_std([]) 
            



