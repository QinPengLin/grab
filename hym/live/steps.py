# coding=utf-8
import json
import os
import random
import socket
import string
import re
import hashlib
import traceback
import sys
import function
import lxml.html as xt

import requests
from datetime import datetime
import time

import thread

from requests.exceptions import ProxyError

import hym
from hym import api_client, helper
from hym.core import Step, getLogger, logger, RetryAdapter, TaskCancelException



class Init(Step):
    """初始化类"""
    timeout = 20

    def __init__(self):
        super(Init, self).__init__()

    def execute(self, arguments):
        # 初始化日志
        app_log_path = sys.path[0] + '/logs/live/{0}_{1}.log'.format(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'),
                                                                       random.randint(100000, 9999999))
        self.context.logger = getLogger(app_log_path, True)
        self.context.app_log_path = app_log_path
        hym.core.default_logger = self.context.logger
        # requests初始化
        requests.packages.urllib3.disable_warnings()
        self.context.session = requests.session()
        self.context.session.verify = False
        log_path = sys.path[0] + '/logs/request_log/{0}_{1}.log'.format(time.strftime('%Y-%m-%d_%H-%M-%S_'),
                                                                        random.randint(1000000, 9999999))
        if not os.path.isdir(os.path.split(log_path)[0]):
            os.makedirs(os.path.split(log_path)[0])
            pass
        logger().info('request log path: {0}'.format(log_path))
        requestLogAdapter = RetryAdapter(self.check_retry, log_path, max_retries=5)
        self.context.session.mount('http://', requestLogAdapter)
        self.context.session.mount('https://', requestLogAdapter)
        self.context.session.headers.update({
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
        })
        self.context.request = self.request
        pass

    def check_retry(self, response):
        """
        在某些情况下返回True， 以完成重复发起请求
        :param response:
        :return:
        """
        if response.status_code == 502:
            return True
            pass
        return False
        pass

    def request(self, method, url, **kwargs):
        """
        使用 self.context.session.request()发起请求
        :param method:
        :param url:
        :param params:
        :return:
        """
        if not kwargs.has_key('timeout'):
            kwargs['timeout'] = Init.timeout
            pass
        response = None
        while response == None:
            try:
                response = self.context.session.request(method, url, **kwargs)
                pass
            except ProxyError:
                logger().error(traceback.format_exc())
                if hasattr(self.context, 'proxy_expire'):
                    delattr(self.context, 'proxy_expire')
            except Exception:
                logger().error('网络错误, {0} {1}\n {2}'.format(method, url, traceback.format_exc()))
                if hasattr(self.context, 'proxy_expire'):
                    delattr(self.context, 'proxy_expire')
            pass
        return response
        pass
class runs(Step):
    """docstring for runs"""
    def execute(self, arguments):
        response=self.context.request('GET','https://www.douyu.com/directory/game/wzry')
        tl=response.text
        a=xt.fromstring(tl)
        ul=a.xpath('//ul[@id="live-list-contentbox"]')
        li=ul[0].xpath('li')
        y=0
        listss={}
        for x in li:
            img=x.xpath('a/span/img[@class="JS_listthumb"]/@data-original')
            title=(x.xpath('a/div/div/h3[@class="ellipsis"]')[0]).text
            types=(x.xpath('a/div/div/span[@class="tag ellipsis"]')[0]).text
            author=(x.xpath('a/div/p/span[@class="dy-name ellipsis fl"]')[0]).text
            heat=(x.xpath('a/div/p/span[@class="dy-num fr"]')[0]).text
            listss[y]={
            'title':title,
            'img':img[0],
            'types':types,
            'author':author,
            'heat':heat,
            'heat_int':function.conversion(heat)
            }
            y+=1
            pass
        print listss[0]['title']
        print listss[0]['heat']
        print listss[0]['img']
        print listss[0]['types']
        print listss[0]['author']
        print listss[0]['heat_int']
        	