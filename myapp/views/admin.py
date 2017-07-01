#!/usr/bin/python
# -*- coding: utf-8 -*-
#encoding=utf-8
"""
日志系统后台
"""
from flask import request, redirect, url_for, render_template, json, Blueprint, current_app
from flask_admin.base import MenuLink, Admin, BaseView, expose, AdminIndexView 
from flask_admin import helpers
from flask_login import current_user, UserMixin, LoginManager, login_user, logout_user
from redis import Redis
from flask_admin.contrib import rediscli
from flask_admin.contrib.fileadmin import FileAdmin
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import form, fields, validators
from flask_admin.contrib.sqla import ModelView


from myapp import comm
from myapp import conf 
from myapp import lib
from myapp import app
from myapp import db
from myapp.models import UserModel

import os
import datetime
import time
import operator


"""
日志系统后台
"""
logger = comm.getlogger("%s.log" % __file__, ap=True)

########################################################
##           用户权限模块开始
########################################################


# Define login and registration forms (for flask-login)
class LoginForm(form.Form):
    login = fields.StringField(u"用户名", validators=[validators.required()])
    password = fields.PasswordField(u"密码", validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError(u'无效用户')
        # we're comparing the plaintext pw with the the hash from the db
        if not check_password_hash(user.password, self.password.data):
        # to compare plain text passwords use
        # if user.password != self.password.data:
            raise validators.ValidationError(u'错误密码')

    def get_user(self):
        return UserModel.query.filter_by(login=self.login.data).first()


class RegistrationForm(form.Form):
    login = fields.StringField(validators=[validators.required()])
    email = fields.StringField(validators=[validators.Email()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        if UserModel.objects(login=self.login.data):
            raise validators.ValidationError(u'用户名已存在')


# Initialize flask-login
def init_login():
    login_manager = LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return UserModel.query.filter_by(id=user_id).first()

init_login()

########################################################
#           用户权限模块结束
########################################################

# Create menu links classes with reloaded accessible
class AuthenticatedMenuLink(MenuLink):

    def __init__(self, name, url=None, endpoint=None, category=None, class_name=None, icon_type=None, icon_value=None):
        super(AuthenticatedMenuLink, self).__init__(name, url, endpoint, category, class_name, icon_type, icon_value)
        self.last_name = name

    def is_accessible(self):
        return current_user.is_authenticated

    def get_url(self):
        if current_user:
            self.name = u"[ {0} ] {1}".format(current_user.login, self.last_name)
        return super(AuthenticatedMenuLink, self).get_url()


class NotAuthenticatedMenuLink(MenuLink):

    def is_accessible(self):
        return not current_user.is_authenticated


class LogParseStatView(BaseView):
    @expose('/')
    def index(self):
        return self.render('authenticated-admin.html')

    def is_accessible(self):
        return current_user.is_authenticated

print generate_password_hash('123')

class UserInfoSearchView(BaseView):

    @expose('/')
    def index(self):
        return self.render('usersearch-info.html')

    @expose("/s/", methods=('GET', 'POST'))
    def search(self):
        uid = request.args.get("uid", "")
        mobileid = request.args.get("mobileid", "")
        appname = request.args.get("app", "mmq")
        uid = uid.strip()
        mobileid = mobileid.strip()
        cond = {"uid": uid, "mobileID": mobileid}
        cond = dict(filter(lambda x: x[1] is not None and x[1] != "", cond.iteritems()))
        if cond:
            if "uid" in cond:
                cond['uid'] = int(cond['uid'])

            if "mobileID" in cond:
                cond["$or"] = [{"mobileID": cond.get("mobileID")}, {"devicetoken": cond.get("mobileID")}]
                cond.pop("mobileID")

            if appname == "mmq":
                at = AppMamaquanLastvisitToken.getinstance()
            else:
                at = AppHuaiyunLastvisitToken.getinstance()

            results = at.find(cond)
            if results:
                res_results = []
                rev_platforms = comm.invert_dict(conf.PLATFORMS)
                results.limit(20)
                for res in results:
                    res['_id'] = str(res['_id'])
                    res['bbtag'] = comm.bbtag_display(res['bbtag'])
                    res['platform'] = rev_platforms.get(res.get('platform', 0), u"未知")
                    if "t" in res:
                        res[u'创建时间'] = comm.timestamp2datetime(res.pop("t")).strftime("%Y-%m-%d %H:%M:%S")
                    if "ut" in res:
                        res[u'更新时间'] = comm.timestamp2datetime(res.pop("ut")).strftime("%Y-%m-%d %H:%M:%S")
                    res_results.append(res)
                return json.dumps(res_results)

        return '[]'

    def is_accessible(self):
        return current_user.is_authenticated


class UserCondSearchView(BaseView):

    @expose('/')
    def index(self):
        return self.render('usersearch-cond.html')

    def is_accessible(self):
        return current_user.is_authenticated

    @expose("/s/", methods=('GET', 'POST'))
    def search(self):
        print request.args
        datas = lib.cache.read(lib.cache.get_cache_key(request.args))
        if not datas:
            conds = {}

            plts = request.args.getlist("platform[]", type=int)
            if plts:
                plts.sort()
                if plts != [1, 2, 5]:
                    conds['platform'] = {"$in": plts}
            else:
                plt = request.args.get("platform", type=int)
                if plt:
                    conds['platform'] = plt

            bbtags = request.args.getlist("bbtags[]", type=int)
            if bbtags:
                bbtags.sort()
                if bbtags != [1, 2, 3, 4]:
                    conds['bbtag'] = {"$in": bbtags}
            else:
                bbtag = request.args.get("bbtags", type=int)
                if bbtag:
                    conds['bbtag'] = bbtag

            uid = request.args.get("uid-select")
            if uid is not None and uid != "all":
                uid = int(uid)
                if not uid:
                    conds["uid"] = {"$in": [0, "", None]}
                else:
                    conds["uid"] = {"$nin": [0, "", None]}

            devtoken = request.args.get("devtoken-select")
            if devtoken is not None and devtoken != "all":
                devtoken = int(devtoken)
                if not devtoken:
                    conds["devicetoken"] = {"$in": [0, "", None]}
                else:
                    conds["devicetoken"] = {"$nin": [0, "", None]}

            def get_date(field):
                dstart = request.args.get(field + "-start")
                dend = request.args.get(field + "-end")
                if dstart is None and dend is None:
                    return None
                dconds = {}
                try:
                    if dstart is not None:
                        dconds["$gte"] = int(comm.datetime2timestamp(datetime.datetime.strptime(dstart, "%Y-%m-%d")))
                    if dend is not None:
                        dconds["$lte"] = int(comm.datetime2timestamp(datetime.datetime.strptime(dend, "%Y-%m-%d")))
                except:
                    pass

                return dconds

            res = get_date("t")
            if res:
                conds['t'] = res

            res = get_date("ut")
            if res:
                conds['ut'] = res

            res = get_date("bbbirth")
            if res:
                conds['bbbirth'] = res

                lib.cache.write(lib.cache.get_cache_key(request.args), [])
            else:
                return '{"count": 0}'

        else:
            return datas


class UserAdminView(BaseView):

    @expose('/')
    def index(self):
        users = UserModel.objects()
        self._template_args['users'] = users
        return self.render('useradmin.html')

    @expose('/add/', methods=('GET', 'POST'))
    def add(self):
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = UserModel()

            form.populate_obj(user)
            # we hash the users password to avoid saving it as plaintext in the db,
            # remove to use plain text:
            user.password = generate_password_hash(form.password.data)
            user.t = int(time.time())
            user.ut = int(time.time())

            user.save()

            return '1'
        else:
            errors = {}
            for f in form:
                if f.errors:
                    errors[f.name] = f.errors[0]

            return json.dumps(errors)

        return "0"

    @expose("/del/", methods=['GET', 'POST'])
    def _del(self):
        id_ = request.form.get("id")
        if id_ is None:
            id_ = request.args.get("id")
        try:
            UserModel.objects.filter(id=id_).delete()
        except Exception, e:
            return e.message
        return '1'

    @expose("/modifypassword/", methods=['GET', 'POST'])
    def modifypassword(self):
        id_ = request.form.get("id")
        if id_ is None:
            id_ = request.args.get("id")

        password = request.form.get("password")
        if password is None:
            password = request.args.get("password")

        try:
            user = UserModel.objects.filter(id=id_).first()
            user.password = generate_password_hash(password)
            user.save()
        except Exception, e:
            return json.dumps({"error": e.message})

        return '1'

    def is_accessible(self):
        return current_user.is_authenticated and current_user.login == "admin"


class UserModifyPasswordView(BaseView):

    @expose('/')
    def index(self):
        self._template_args["login"] = current_user.login
        self._template_args["mid"] = current_user.id
        return self.render('usermodifypassword.html')

    @expose('/modify/', methods=['POST', 'GET'])
    def modify(self):
        user = UserModel.objects.filter(id=request.form.get('mid')).first()
        errors = []
        if request.form.get('mpassword') != request.form.get('rempassword'):
            errors.append(u'重复新密码错误')

        if not check_password_hash(user.password, request.form.get('opassword')):
            errors.append(u'原密码错误')

        try:
            user.password = generate_password_hash(request.form.get('mpassword'))
            user.save()
        except Exception, e:
            errors.append(e.message)

        if errors:
            self._template_args["status"] = "error"
            for fk, fv in request.form.iteritems():
                self._template_args[fk] = fv
            self._template_args["errors"] = errors
        else:
            self._template_args["status"] = "success"
        return self.render('usermodifypassword.html')


class MyFileAdmin(FileAdmin):
    can_upload=False
    can_delete=False
    can_delete_dirs=False,
    can_mkdir=False
    can_rename=False
    can_download=False
    editable_extensions = ('log', 'txt', 'css', 'html', 'js')
    list_template = "file_list.html"

    def is_accessible(self):
        return current_user.is_authenticated

class MyRedisCli(rediscli.RedisCli):

    def is_accessible(self):
        return current_user.is_authenticated


class MyAdminIndex(AdminIndexView):



    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        self._template_args['logdata'] = []
        return self.render('index.html')

    @expose('/updatequeue/<type_>', methods=['GET'])
    def updatequeuestat(self, type_):
        updatequeuestat_db = UpdateQueueStat.getinstance()
        if type_ == "init":
            results = updatequeuestat_db.find({"t": {"$gt": int(time.time()) - 900}})
            response = {}
            for result in results:
                pid = result.get("pid")
                t = result.get("t")
                s = result.get("s")
                if pid in response:
                    response[pid].append({"x": t * 1000,"y": s})
                else:
                    response[pid] = [{"x": t * 1000,"y": s}]
            response = dict(sorted(response.iteritems(), key=operator.itemgetter(0)))
            return json.dumps(response)
        elif type_ == "timly":
            # 每5秒中更新一次，我最近10秒的数据，保证取到所有的pid
            results = updatequeuestat_db.find({"t": {"$gt": int(time.time()) - 10}})
            response = {}
            for result in results:
                pid = result.get("pid")
                t = result.get("t")
                s = result.get("s")
                if pid in response:
                    if response[pid]['x'] < (t * 1000):
                        response[pid]['x'] = t * 1000
                        response[pid]['y'] = s
                else:
                    response[pid] = {"x": t * 1000,"y": s}

            response = dict(sorted(response.iteritems(), key=lambda x:x[0]))
            return json.dumps(response)

        return json.dumps([])


    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login_user(user)

        if current_user.is_authenticated:
            return redirect(url_for('.index'))
        #link = '<p>Don\'t have an account? <a href="' + url_for('.register_view') + '">Click here to register.</a></p>'
        link = ''
        self._template_args['form'] = form
        self._template_args['link'] = link
        return self.render('auth.html')

    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        if not current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = UserModel()

            form.populate_obj(user)
            # we hash the users password to avoid saving it as plaintext in the db,
            # remove to use plain text:
            user.password = generate_password_hash(form.password.data)

            user.save() 

            login_user(user)
            return redirect(url_for('.index'))
        link = '<p>Already have an account? <a href="' + url_for('.login_view') + '">Click here to log in.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return self.render('auth.html')

    @expose('/logout/')
    def logout_view(self):
        logout_user()
        return redirect(url_for('.index'))


def formatdate(date_, fmt="%Y-%m-%d %H:%I:%S"):
    dt = comm.timestamp2datetime(date_)
    return dt.strftime(fmt)

app.jinja_env.filters['formatdate'] = formatdate

myAdminIndexView = MyAdminIndex(name=u"首页")
admin = Admin(name=u"日志系统后台", template_mode="bootstrap3", index_view=myAdminIndexView)

admin.add_view(UserInfoSearchView(name=u'信息查询', endpoint="userinfosearch", category=u"数据查询"))
admin.add_view(UserCondSearchView(name=u'条件查询', endpoint="usercondsearch", category=u"数据查询"))

admin.add_link(NotAuthenticatedMenuLink(name=u'登录', url="/admin/login"))

path = os.path.realpath(os.path.join(os.path.dirname(__file__), "../../.."))
admin.add_view(MyFileAdmin(path, '/filemgr/', name=u'文件管理'))

admin.add_view(UserAdminView(name=u"用户管理", endpoint="useradmin", category=u"用户管理"))
admin.add_view(UserModifyPasswordView(name=u"修改密码", endpoint="usermodifypassword", category=u"用户管理"))


# Add logout link by endpoint
admin.add_link(AuthenticatedMenuLink(name=u'注销', url="/admin/logout"))

admin.init_app(app)

