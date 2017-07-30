#!/usr/bin/env python
# coding: utf-8

from datetime import date
import random
import re
from bs4 import BeautifulSoup
import sys
reload(sys)
sys.setdefaultencoding('utf8')

header = {
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
    'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.13 Safari/537.36',
    'Referer': 'http://www.gjjx.com.cn',
    'Connection': 'keep-alive'
}

class Appointment:
    def __init__(self, session):
        self.session = session

    # 预约前登录
    def login(self):
        h = header
        url = 'http://www.gjjx.com.cn/member/status'
        h['X-Requested-With'] = 'XMLHttpRequest'
        r = self.session.post(url, headers=h)
        json = r.json()
        # print self.session.cookies.get_dict()
        r = self.session.get(json['data']['yyurl_login']+'&selmenu=yyks&username='+json['data']['name'])

    # 预约表单
    def timetable(self):
        """
        @return tuple
        // 还有的状态:jinyue,moni
        schedule = [
            {
                "2017-05-13":[
                    {'state':'wuche', 'name':''},
                    {'state':'luxun', 'name':''},
                    {'state':'lijiyuyue', 'name':'clt01'}
                ]
            }
        ],
        payload
        """
        schedule = {}
        url = 'http://member.gjjx.com.cn/ych2.aspx?yt=2'
        r = self.session.get(url, headers=header)
        soup = BeautifulSoup(r.content, 'html.parser')
        form = soup.find(id='ctl00')
        payload = {
            '__EVENTTARGET': form.find(id='__EVENTTARGET').get('value'),
            '__EVENTARGUMENT': form.find(id='__EVENTARGUMENT').get('value'),
            '__LASTFOCUS': form.find(id='__LASTFOCUS').get('value'),
            '__VIEWSTATE': form.find(id='__VIEWSTATE').get('value'),
            '__EVENTVALIDATION': form.find(id='__EVENTVALIDATION').get('value'),
            'hiddenKM': form.find(id='hiddenKM'),
            # 'ctl02': '', # 预预约
        }
        # 按日期处理时间表
        table = soup.find(id='tb_yyrq')
        # 转换标题的日期 ['xxxx-xx-xx', ...]
        now = date.today()
        title = table.tr
        date_list = []
        for i in title.find_all('span')[1:]:
            groups = re.findall(r'(\d{1,2})', i.string.encode("utf-8"))
            if len(groups) == 2:
                year = now.year if groups[1] >= now.month else now.year + 1
                one_day = date(year, int(groups[0]), int(groups[1]))
            elif len(groups) == 3:
                one_day = date(int(groups[0]), int(groups[1]), int(groups[2]))
            else:
                raise Exception('Date Title Can\'t Be Recognized')
            date_list.append(one_day.isoformat())
            schedule[one_day.isoformat()] = []
        
        # 可预约情况
        for line in title.find_next_siblings('tr'):
            # 所有日期某个时间段预约情况
            for k,td in enumerate(line.find_all('td')[1:]):
                name = ''
                # 可预约
                if td.input != None:
                    state = 'lijiyuyue'
                    name = td.input.get('name').encode('utf-8')
                # 无车
                elif td.string == u'无车':
                    state = 'wuche'
                else:
                    state = 'unknow'
                schedule[date_list[k]].append({
                    'state': state,
                    'name': name
                })
        
        return payload, schedule

    # 开始预约
    def appointment(self, payload, ctl_name):
        url = 'http://member.gjjx.com.cn/ych2.aspx?yt=2'
        payload[ctl_name] = ''
        r = self.session.post(url, data=payload)
        soup = BeautifulSoup(r.content, 'html.parser')
        form = soup.find(id='ctl00')

        # 更新下一次请求的post参数
        payload['__VIEWSTATE'] = form.find(id='__VIEWSTATE').get('value')
        payload['__EVENTVALIDATION'] = form.find(id='__EVENTVALIDATION').get('value')
        # 扩展
        del payload[ctl_name]
        new_key = form.find(id='RepeaterKyycar_LinkBooking_0').get('name').encode('utf-8')
        payload[new_key] = ''
        payload['hid_yyrq_sel'] = form.find(id='hid_yyrq_sel').get('value').encode('utf-8')
        payload['hid_xnsd_sel'] = form.find(id='hid_xnsd_sel').get('value').encode('utf-8')
        h = header
        h['Referer'] = 'http://member.gjjx.com.cn/ych2.aspx?yt=2'
        h['Origin'] = 'http://member.gjjx.com.cn'
        h['Upgrade-Insecure-Requests'] = '1'
        r = self.session.post(url, data=payload, headers=h)
        groups = re.findall(r'预约成功！', r.content)

        return True if len(groups) > 0 else False