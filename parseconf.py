#!/usr/bin/env python
# coding: utf-8

import ConfigParser
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class ParseConf:
    def __init__(self):
        try:
            cf = ConfigParser.ConfigParser()
            cf.read('conf.ini')

            # 用户名
            self.user_name = cf.get('assistant', 'user_name')
            # 密码
            self.password = cf.get('assistant', 'password')

            # 刷新间隔(秒)
            self.sleep = int(cf.get('assistant', 'sleep'))

            # 预约时间
            date_line = cf.get('assistant', 'date_line')
            self.date_line = map(lambda x: x.split(','), date_line.split('|'))

        except Exception, e:
            print '[ERROR] Parse conf.ini failed.'
            raise e