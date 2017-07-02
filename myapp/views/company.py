#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding=utf-8

from myapp import app, db, user_id
from myapp import lib
from myapp.models import CompanyModel
from myapp.models import CompanyCustomerModel
from myapp.models import UserCustomerModel
from flask import request
import sqlalchemy


@app.route('/api/company/list', methods=['GET'])
def get_company_list():
    companys = CompanyModel.query.order_by("created_time desc").all()
    return lib.params.response_std(companys)


@app.route('/api/company/', methods=['POST'])
@app.route('/api/company/<id>', methods=['POST','GET'])
def get_save_company(id=None):
    if request.method == 'POST':
        company_model = CompanyModel(request.form['name'], request.form['tel'], request.form['remark'], request.form['avatar'])
        db.session.add(company_model)
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError, e:
            return lib.params.response_std(0, '-1', e.message)
        except Exception, e:
            return lib.params.response_std(0, '-1', e.message)

        return lib.params.response_std(1)
    return lib.params.response_std(CompanyModel.query.get(id))

@app.route('/api/company/customer/list', methods=['GET'])
def get_customer_list():
    company_customers = CompanyCustomerModel.query.filter_by(user_id = user_id, company_id = request.args['company_id'], is_show = 1).all()
    user_customer_ids = []
    for company_customer in company_customers:
        user_customer_ids.append(company_customer.user_customer_id)
    user_customers = UserCustomerModel.query.filter_by(user_id=user_id).filter(
        UserCustomerModel.id.in_(user_customer_ids)).all()
    return lib.params.response_std(user_customers)