#!/usr/bin/python
# -*- coding: utf-8 -*-
#encoding=utf-8
"""
push系统专用接口
"""
from flask import request, json
from myapp import comm
from myapp import lib
from myapp import conf
from myapp import app

import math
import time
import os
import sys

logger = comm.getlogger("%s.log" %  __file__, ap=True)


@app.route('/static/.*', methods=['GET',])
def get_static():
    return 'xxx'


@app.route('/api', methods=['GET',])
def test():
    # user = UserModel.query.filter_by(mobile_tel='18575516501').first()
    return lib.params.response_std([])
            



