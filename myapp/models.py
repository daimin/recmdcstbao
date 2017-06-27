#!/usr/bin/python
# -*- coding: utf-8 -*-
#encoding=utf-8

from myapp import db

# Create user model.
class UserModel(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(200))
    t = db.Column(db.Integer)
    ut = db.Column(db.Integer)

    def __repr__(self):
        return '<User %r>' % self.login

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    # Required for administrative interface
    def __unicode__(self):
        return self.login
