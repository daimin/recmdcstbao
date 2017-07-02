#!/usr/bin/python
# -*- coding: utf-8 -*-
#encoding=utf-8

from myapp import app, db, user_id
from myapp import lib
from myapp.models import UserCustomerModel
from myapp.models import CompanyCustomerModel, CompanyModel
from flask import request
from flask import render_template
import sqlalchemy

@app.route('/api/customer/<id>', methods=['GET'])
def get(id = None):
    return lib.params.response_std(UserCustomerModel.query.get(id))

@app.route('/api/customer/list', methods=['GET'])
def get_list():
    company_id = 0
    if 'company_id' in request.args:
        company_id = request.args['company_id']
    if company_id > 0:
        user_customer_ids = db.session.query(CompanyCustomerModel.user_customer_id).filter_by(user_id=user_id, company_id=company_id).all()

    user_customer_id2s = []
    for user_customer_id in user_customer_ids:
        user_customer_id2s.append(user_customer_id[0])

    if len(user_customer_id2s) == 0:
        user_customers = UserCustomerModel.query.filter_by(user_id=user_id).all()
    else:
        user_customers = UserCustomerModel.query.filter_by(user_id=user_id).filter(UserCustomerModel.id.notin_(user_customer_id2s)).all()

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
    customer_ids = []
    i = 0
    while True:
        if 'customer_ids[' + str(i) + ']' in request.form:
            customer_ids.append(request.form['customer_ids[' + str(i) + ']'])
            i = i + 1
        else:
            break
    company_id = request.form['company_id']

    try:
        if len(customer_ids) == 0:
            customer_ids.append(save_customer())

        for user_customer_id in customer_ids:
            cnt = CompanyCustomerModel.query.filter_by(user_id = user_id, company_id = company_id, user_customer_id = user_customer_id).count();
            if cnt > 0:
                return lib.params.response_std(user_customer_id, '-1', '该客户已被推荐过')

            company_customer = CompanyCustomerModel(user_id, company_id, user_customer_id)
            db.session.add(company_customer)
            db.session.commit()
            customer = UserCustomerModel.query.get(user_customer_id)
            if customer:
                confirm_url = 'http://10.5.216.83:5000/api/cst/cf/%d' % company_customer.id
                print confirm_url
                ret = lib.sms.send_sms(customer.mobile_tel, ['随心贷', confirm_url])
                if ret:
                    print '短信发送成功'

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

@app.route('/api/cst/cf/<id>', methods=['GET'])
def customer_confirm(id=None):
    company_cst_model = CompanyCustomerModel.query.get(id)
    company = CompanyModel.query.get(company_cst_model.company_id)
    return render_template('customer_confirm.html', ccid=id, company=company)

@app.route('/api/cst/cfd/<id>', methods=['GET'])
def customer_confirm_done(id=None):
    query = db.session.query(CompanyCustomerModel)
    company_cst_model = query.get(id)
    company_cst_model.is_show = True
    db.session.flush()
    db.session.commit()
    return render_template('customer_done.html');
