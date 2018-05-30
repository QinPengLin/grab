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
        logger().info('request log path: {0}'.format(log_path))
        requestLogAdapter = RetryAdapter(self.check_retry, log_path, max_retries=5)
        self.context.session.mount('http://', requestLogAdapter)
        self.context.session.mount('https://', requestLogAdapter)
        self.context.session.headers.update({
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9'
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
		response=self.context.request('GET','https://www.baidu.com/')
		logger().info(response.text)
		print response.text
		