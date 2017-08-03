#!/usr/bin/env python
# coding: utf-8

import time
from session import Session
from login import Login
from appointment import Appointment
from parseconf import ParseConf
import webbrowser
import sys
reload(sys)
sys.setdefaultencoding('utf8')

DATELINE_CN = {'0':'上午', '1':'中午', '2':'晚上'}
CONFIG = ParseConf()


def apdate(appointment, datepoint):
    """
    预约日期
    :param appointment: 预约session
    :param datepoint 需要预约的时间点 [('2017-05-27', '0')]
    """
    (postdata, schedule) = appointment.timetable()
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

if __name__ == '__main__':
    session = Session().session

    login = Login(session)
    login.get_captcha()
    login.show_image(login.captcha_path)
    captcha = raw_input(u'输入验证码:')
    payload = {
        'username': CONFIG.user_name,
        'password': CONFIG.password,
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
            time.sleep(CONFIG.sleep)
            print count
            count = count + 1
            try:
                ok, ret = apdate(appointment, CONFIG.date_line)
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
