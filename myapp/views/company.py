#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding=utf-8

from myapp import app, db
from myapp import lib
from myapp.models import CompanyModel
from flask import request
import sqlalchemy


@app.route('/api/company/list', methods=['GET'])
def get_customer_list():
    companys = CompanyModel.query.order_by("created_time desc").all()
    return lib.params.response_std([companys])


@app.route('/api/company', methods=['POST', 'GET'])
@app.route('/api/company/<id>', methods=['GET'])
def save_customer(id=None):
    if request.method == 'POST':
        company_model = CompanyModel(request.form['name'], request.form['tel'], request.form['remark'])
        db.session.add(company_model)
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError, e:
            return lib.params.response_std(0, '-1', e.message)
        except Exception, e:
            return lib.params.response_std(0, '-1', e.message)

        return lib.params.response_std(1)
    return lib.params.response_std(CompanyModel.query.get(id))

