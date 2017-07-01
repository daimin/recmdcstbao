#!/usr/bin/python
# -*- coding: utf-8 -*-
#encoding=utf-8

from myapp import app
from myapp import lib
from flask import request

@app.route('/api/customer/save', methods=['POST'])
def customer_save():
    # user = UserModel.query.filter_by(mobile_tel='18575516501').first()
    name = request.form['name']
    mobile_tel = request.form['mobile_tel']
    gender = request.form['gender']
    remark = request.form['remark']

    return lib.params.response_std([mobile_tel])