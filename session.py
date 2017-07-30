#!/usr/bin/env python
# coding: utf-8

import requests

"""
会话请求
"""
class Session(object):
    def __init__(self):
        self.session = requests.Session()