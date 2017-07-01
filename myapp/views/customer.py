#!/usr/bin/python
# -*- coding: utf-8 -*-
#encoding=utf-8

from myapp import app, db
from myapp import lib
from myapp.models import CustomerModel
from flask import request
import sqlalchemy

@app.route('/api/customer/<id>', methods=['GET'])
def get(id = None):
    return lib.params.response_std(CustomerModel.query.get(id))

@app.route('/api/customer/list', methods=['GET'])
def get_list():
    customers = CustomerModel.query.order_by("created_time desc").all()
    return lib.params.response_std([customers])

@app.route('/api/customer/save', methods=['POST'])
def save():
    try:
        id = save_customer()
        return lib.params.response_std(id)
    except Exception, e:
        return lib.params.response_std(0, '-1', e.message)

@app.route('/api/customer/recommend', methods=['POST'])
def recommend():
    try:
        customer_id = request.form['']
        customer_id = save_customer()
    except Exception, e:
        raise e

def save_customer():
    customer = CustomerModel(request.form['name'], request.form['mobile_tel'], request.form['gender'], request.form['remark'])
    db.session.add(customer)
    try:
        db.session.commit()
        return customer.id
    except sqlalchemy.exc.IntegrityError, e:
        raise e
    except Exception, e:
        raise e