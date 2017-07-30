#!/usr/bin/env python
# coding: utf-8

import time
from session import Session
from login import Login
from appointment import Appointment
import sys
reload(sys)
sys.setdefaultencoding('gbk')

DATELINE_CN = ['上午', '中午', '晚上']

# 预约日期
def apdate(appointment, datepoint):
    (postdata, schedule) = appointment.timetable()
    # test
    # print postdata
    # print schedule
    print u'获取预约日期表...'

    for k,(d,i) in enumerate(datepoint):
        # 11点40更新第10天预约
        if schedule.has_key(d) == False:
            return False, None
        
        selected = schedule[d][i]
        if selected['state'] == 'lijiyuyue':
            # 可预约提示
            print d + DATELINE_CN[i] + u' 可以预约'
            appointment.appointment(postdata, selected['name'])
            return True, (d, i)
        else:
            return False, None

session = Session().session

login = Login(session)
login.getCaptcha()
captcha = raw_input(u'输入验证码: ')
payload = {
    'username': '用户名',
    'password': '密码',
    'captcha': captcha
}
(loginStat, loginMsg) = login.login(payload)

if loginStat == True:
    print u'登录成功'
    appointment = Appointment(session)
    appointment.login()
    nowtime = time.time()
    
    count = 1
    aplogin = False
    # 已经登录
    #   590-600登录  已经登录 (r)
    while True:
        time.sleep(2)
        print count
        count = count + 1
        try:
            ok, ret = apdate(appointment, [('2017-06-25', 0)])
        except Exception as e:
            print e
            continue
        if ok == True:
            print ret[0] + DATELINE_CN[ret[1]] + u'预约成功'
            break

        left = (time.time() - nowtime) % 600
        if left <= 590:
            aplogin = False
        elif aplogin == False and left > 590:
            appointment.login()
            aplogin = True
else:
    print u'登录失败'
