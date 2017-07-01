#!/usr/bin/python
# -*- coding: utf-8 -*-
#encoding=utf-8

from myapp import app, db, user_id
from myapp import lib
from myapp.models import UserCustomerModel
from myapp.models import CompanyCustomerModel
from flask import request
from flask import render_template
import sqlalchemy

@app.route('/api/customer/<id>', methods=['GET'])
def get(id = None):
    return lib.params.response_std(UserCustomerModel.query.get(id))

@app.route('/api/customer/list', methods=['GET'])
def get_list():
    company_id = 0
    if 'company_id' in request.form:
        company_id = request.form['company_id']
    if company_id > 0:
        user_customer_ids = db.session.query(CompanyCustomerModel.user_customer_id).filter_by(user_id=user_id, company_id=company_id).all()
    else:
        user_customer_ids = db.session.query(CompanyCustomerModel.user_customer_id).filter_by(user_id=user_id).all()
    user_customer_id2s = []

    for user_customer_id in user_customer_ids:
        user_customer_id2s.append(user_customer_id[0])
    user_customers = UserCustomerModel.query.filter(UserCustomerModel.id.in_(user_customer_id2s)).all()

    return lib.params.response_std(user_customers)

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
        customer_ids = []
        i = 0
        while True:
            if 'customer_ids[' + str(i) + ']' in request.form:
                customer_ids.append(request.form['customer_ids[' + str(i) + ']'])
                i = i + 1
            else:
                break
        if len(customer_ids) == 0:
            customer_ids.append(save_customer())

        company_id = request.form['company_id']
        for user_customer_id in customer_ids:
            company_customer = CompanyCustomerModel(user_id, company_id, user_customer_id)
            db.session.add(company_customer)
            db.session.commit()

        return lib.params.response_std(1)
    except Exception, e:
        return lib.params.response_std(0, '-1', e.message)

def save_customer():
    customer = UserCustomerModel(user_id, request.form['name'], request.form['mobile_tel'], request.form['gender'], request.form['remark'])
    db.session.add(customer)
    try:
        db.session.commit()
        return customer.id
    except sqlalchemy.exc.IntegrityError, e:
        raise e
    except Exception, e:
        raise e

@app.route('/customer/confirm', methods=['GET', 'POST'])
def customer_confirm():
    return render_template('customer_confirm.html', name='')
