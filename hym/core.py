# coding=utf-8
import logging
import traceback

import datetime
import time
import os
import sys

from abc import ABCMeta, abstractmethod
from requests.adapters import HTTPAdapter

from hym import api_client


class Context():
    """
    :var currentStep:
    """
    __metaclass__ = type

    def __init__(self):
        pass

class Pipeline:
    __metaclass__ = type

    def __init__(self, context, steps):
        self.currentIndex = 0
        self.steps = steps
        self.context = context
        self.stepForceMoved = False
        self.stepListeners = {}

    def __getattr__(self, item):
        if (item == 'currentStep'):
            return None if self.currentIndex >= len(self.steps) else self.steps[self.currentIndex]
        return super(Pipeline,self).__getattr__(item)

    def __setattr__(self, key, value):
        if (key=='currentStep'):
            if (value in self.steps):
                index = self.steps.index(value)
                self.currentIndex = index
        super(Pipeline,self).__setattr__(key, value)

    def start(self):
        """
        开始依次执行pipeline
        :return:
        """
        try:
            retVal = None
            while (self.currentIndex > -1):
                if (self.currentIndex >= len(self.steps)):
                    break
                retVal = self.next(retVal)
            hasError = False
        except TaskCancelException as e:
            logger().error('程序要求停止任务:' + e.msg)
            # api_client.client.post_log(e.msg, self.context.app_log_path)
            hasError = True
        except Exception as e:
            logger().error('未处理的异常导致流程结束: ' + e.__str__())
            logger().error(traceback.format_exc())
            traceback.print_exc()
            # api_client.client.post_log('unknown', self.context.app_log_path)
            hasError = True
        logger().info('Pipeline 流程结束')
        return not hasError

    def next(self, arguments=None):
        step = self.currentStep
        step = step()
        step.set_environment(context=self.context, pipeline=self)
        logger().info('Step: '+step.__class__.__name__)
        retVal = step.execute(arguments=arguments)
        if(not self.stepForceMoved):
            self.currentIndex += 1
        self.stepForceMoved = False
        return retVal

    def moveToStep(self, step, match_index=0):
        """
        :param class step: class， 应该是类的引用
        :param match_index: 匹配的索引， 如pipeline中有两个相同的class， index为0时，跳到第一个， 1跳到第二个， 以此类推
        :return:
        """
        index = None
        i = -1
        matchedIndex = -1
        stepObject = None

        for item in self.steps:
            i += 1
            if(item==step):
                matchedIndex += 1
                if(matchedIndex==match_index):
                    index = i
                    stepObject = item
                    break

        if(index != None):
            listener = self.getStepMoveListener(stepObject)
            if(listener):
                listener(step)
            logger().info('强制跳转: '+ self.currentStep.__name__ +' to ' + step.__name__)
            self.currentIndex = index
            self.stepForceMoved = True
            pass
        else:
            raise Exception(step.__name__ + ' 不在pipeline中')


    def setStepMoveListener(self, step, function):
        self.stepListeners[step] = function

    def getStepMoveListener(self, step):
        return self.stepListeners[step] if self.stepListeners.has_key(step) else None

    def removeStepMoveListener(self, step):
        if(self.stepListeners.has_key(step)):
            del self.stepListeners[step]

class Step():
    __metaclass__ = ABCMeta

    def __init__(self):
        self.context = None
        self.pipeline = None

    def set_environment(self, context, pipeline):
        self.context = context
        self.pipeline = pipeline

    @abstractmethod
    def execute(self, arguments):pass

class TaskCancelException(Exception):

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)

class RequestLogAdapter(HTTPAdapter):

    def __init__(self, logfile_path, **kwargs):
        super(RequestLogAdapter, self).__init__(**kwargs)
        self.logger = logging.Logger('request_log')
        handler = logging.FileHandler(logfile_path)
        handler.setFormatter(logging.Formatter('[%(asctime)s] %(thread)d-%(levelname)s:%(message)s'))
        self.logger.addHandler(handler)

    def build_response(self, req, resp):
        """

        :param PreparedRequest req:
        :param resp:
        :return:
        """
        # 格式化 request 记录
        now = time.time()
        log_str = '-------------------------------------------------------\n'
        log_str += req.method + ' ' + req.url + '\n'
        log_str += 'request [{0}.{1}]:\n'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), str(now).split('.')[1])
        for header_key in req.headers.keys():
            log_str += '{0}: {1}\n'.format(header_key, req.headers.get(header_key))
        log_str += '\n{0}\n'.format(req.body)

        response = None
        #格式化 response 记录
        try:
            response = super(RequestLogAdapter, self).build_response(req, resp)
            now = time.time()
            log_str += '=====================================\n'
            if response==None:
                log_str += '\nresponse [{0}.{1}]: None'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), str(now).split('.')[1])
            else:
                log_str += '\nresponse [{0}.{1}]:\n'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), str(now).split('.')[1])
                log_str += '{0} {1}\n'.format(response.status_code, response.reason if response.reason else '')
                for header_key in response.headers.keys():
                    log_str += '{0}: {1}\n'.format(header_key, response.headers.get(header_key))
                log_str += '\n{0}'.format(response.text)
            self.logger.info(log_str)
        except Exception:
            self.logger.error(log_str+'\n'+traceback.format_exc())

        return response

class RetryAdapter(RequestLogAdapter):

    def __init__(self, check_callable, logfile_path, **kwargs):
        """

        :param checkCallable: 函数， 第一个参数为response， 如果要重新请求， 返回True
        :param kwargs:
        """
        super(RetryAdapter, self).__init__(logfile_path, **kwargs)
        self.check_callable = check_callable


    def build_response(self, req, resp):
        response = super(RetryAdapter, self).build_response(req, resp)
        retry = self.check_callable(response)
        if retry:
            return self.send(req)
        else:
            return response

def broadcast(msg):
    print ('<broadcast>' + str(msg))
    sys.stdout.flush()


def getLogger(target_file=None, output_to_stdout=False):
    if not target_file:
        target_file = sys.path[0]+'/logs/{0}.log'.format(datetime.datetime.now().strftime('%Y-%m-%d'))
    if logging.Logger.manager.loggerDict.has_key(target_file):
        return logging.getLogger(target_file)
    if not os.path.isdir(os.path.split(target_file)[0]):
        os.makedirs(os.path.split(target_file)[0])

    logger = logging.getLogger(target_file)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
    file_handler = logging.FileHandler(target_file, 'a', 'utf8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if output_to_stdout:
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)

    return logger

def logger():
    """
    返回当前默认的logger,  默认logger可以通过对hym.core.default_logger赋值进行修改
    :return:
    """
    return default_logger

default_logger = getLogger()
