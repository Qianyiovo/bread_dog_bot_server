"""Terraria_Bot_Server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import json
import sqlite3
import config
from django.http import HttpResponse
from django.urls import path


def execute_sql(sql: str):
    """
     在数据库执行指定的sql语句
    :param sql: 执行的sql语句
    :return: 执行结果 成功返回[True, sql执行结果] 失败返回 [False, 失败原因]
    """
    try:
        conn = sqlite3.connect("db.sqlite3")
        cursor = conn.cursor()
        cursor.execute(sql)
        sql_return_result = cursor.fetchall()
        cursor.close()
        conn.commit()
        conn.close()
        return True, sql_return_result
    except:
        return False, "无法连接至数据库"


def auth(token: str):
    """
    权限验证
    :return:
    """
    result, sql_return_result = execute_sql("select Token from user")
    if result:
        token_list = []
        for i in sql_return_result:
            token_list.append(i[0])

        if token in token_list:
            return True, None
        else:
            return False, "权限验证失败"
    else:
        return False, sql_return_result


class Token:
    @staticmethod
    def get():
        """
        获取QQ 和 token
        :return:
        """
        result, sql_return_result = execute_sql("select * from user")
        if result:
            token_list = []
            for i in sql_return_result:
                token_list.append(i)
            return True, token_list
        else:
            return False, None

    @staticmethod
    def add(qq: str):
        """
        添加token
        :return:
        """
        import random
        import string
        token = 'BDT_' + ''.join(random.sample(string.ascii_letters + string.digits, 32))
        result, sql_return_result = execute_sql("insert into user (Token, QQ) values ('%s', '%s')" % (token, qq))
        if result:
            return True, token
        else:
            return False, sql_return_result


class Blacklist:
    @staticmethod
    def get():
        """
        获取黑名单列表
        :return: 黑名单列表 成功返回[True, 黑名单列表] 失败返回 [False, 失败原因]
        """
        sql = "select * from blacklist"
        result, blacklist = execute_sql(sql)
        if result:
            return True, blacklist
        else:
            return False, blacklist

    @staticmethod
    def add(qq: str, groupID: str, reason: str):
        """
        添加黑名单
        :param reason: 原因
        :param groupID: QQ群号
        :param qq: QQ号
        :return: 添加结果 成功返回[True, None] 失败返回 [False, 失败原因]
        """
        sql = "insert into blacklist(QQ, groupID, reason) values('{}', '{}', '{}')".format(qq, groupID, reason)
        result, reason = execute_sql(sql)
        if result:
            return True, None
        else:
            return False, reason

    @staticmethod
    def delete(qq: str):
        """
        删除黑名单
        :param qq: QQ号
        :return: 删除结果 成功返回[True, None] 失败返回 [False, 失败原因]
        """
        sql = "delete from blacklist where QQ = '{}'".format(qq)
        result, reason = execute_sql(sql)
        if result:
            return True, None
        else:
            return False, reason


def get_blacklist(request):
    """
    获取黑名单列表
    :return:
    """
    if request.method == "GET":
        token = request.GET.get("token")
        result, reason = auth(token)
        if result:
            result, blacklist = Blacklist.get()
            if result:
                return HttpResponse(json.dumps({"status": 200, "msg": "获取黑名单列表成功", "data": blacklist}), status=200)
            else:
                return HttpResponse(json.dumps({"status": 403, "msg": blacklist}), status=403)
        else:
            return HttpResponse(json.dumps({"status": 403, "msg": reason}), status=403)
    else:
        return HttpResponse(json.dumps({"status": 405, "msg": "请求方式错误"}), status=405)


def add_blacklist(request):
    """
    添加黑名单
    :return:
    """
    if request.method == "GET":
        token = request.GET.get("token")
        result, reason = auth(token)
        if result:
            qq = request.GET.get("QQ")
            groupID = request.GET.get("groupID")
            reason = request.GET.get("reason")
            # 参数判断
            if qq is None or groupID is None or reason is None:
                return HttpResponse(json.dumps({"status": 403, "msg": "参数错误"}), status=403)
            # 判断是否存在
            result, blacklist = Blacklist.get()
            if result:
                for i in blacklist:
                    if i[0] == qq:
                        return HttpResponse(json.dumps({"status": 403, "msg": "已存在"}), status=403)
            # 添加黑名单
            result, reason = Blacklist.add(qq, groupID, reason)
            if result:
                return HttpResponse(json.dumps({"status": 200, "msg": "添加黑名单成功"}), status=200)
            else:
                return HttpResponse(json.dumps({"status": 403, "msg": reason}), status=403)
        else:
            return HttpResponse(json.dumps({"status": 403, "msg": reason}), status=403)
    else:
        return HttpResponse(json.dumps({"status": 405, "msg": "请求方式错误"}), status=405)


def delete_blacklist(request):
    """
    删除黑名单
    :return:
    """
    if request.method == "GET":
        token = request.GET.get("token")
        result, reason = auth(token)
        if result:
            qq = request.GET.get("QQ")
            # 参数判断
            if qq is None:
                return HttpResponse(json.dumps({"status": 403, "msg": "参数错误"}), status=403)
            # 判断是否存在
            result, blacklist = Blacklist.get()
            if result:
                for i in blacklist:
                    if i[0] == qq:
                        result, reason = Blacklist.delete(qq)
                        if result:
                            return HttpResponse(json.dumps({"status": 200, "msg": "删除黑名单成功"}), status=200)
                        else:
                            return HttpResponse(json.dumps({"status": 403, "msg": reason}), status=403)

            return HttpResponse(json.dumps({"status": 403, "msg": "不存在"}), status=403)
        else:
            return HttpResponse(json.dumps({"status": 403, "msg": reason}), status=403)
    else:
        return HttpResponse(json.dumps({"status": 405, "msg": "请求方式错误"}), status=405)


def add_token(request):
    """
    添加token
    :return:
    """
    if request.method == "GET":
        token = request.GET.get("token")
        # 判断超级管理员token
        if token == config.super_admin_token:
            # 获取参数
            qq = request.GET.get("QQ")
            # 判断参数
            if qq is None:
                return HttpResponse(json.dumps({"status": 403, "msg": "参数错误"}), status=403)
            # 判断是否存在
            result, token = Token.get()
            if result:
                for i in token:
                    if i[0] == qq:
                        return HttpResponse(json.dumps({"status": 403, "msg": "已存在"}), status=403)
            # 添加token
            result, reason = Token.add(qq)
            if result:
                return HttpResponse(json.dumps({"status": 200, "msg": "添加token成功", "data": reason}), status=200)
            else:
                return HttpResponse(json.dumps({"status": 403, "msg": reason}), status=403)
        else:
            return HttpResponse(json.dumps({"status": 403, "msg": "权限验证失败"}), status=403)
    else:
        return HttpResponse(json.dumps({"status": 405, "msg": "请求方式错误"}), status=405)


urlpatterns = [
    path('blacklist/', get_blacklist),
    path('blacklist/add/', add_blacklist),
    path('blacklist/delete/', delete_blacklist),
    path('token/add/', add_token),
]
