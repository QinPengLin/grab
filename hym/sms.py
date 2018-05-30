# coding=utf-8
import traceback

import re
from abc import ABCMeta, abstractmethod
import requests
from core import logger
import time


class Sms():
    __metaclass__ = ABCMeta

    @abstractmethod
    def getPhone(self, phone=None):
        """
        获得一个在指定项目可用的电话号码
        :param str phone: 指定号码
        :return string: 电话号码
        """
        pass

    @abstractmethod
    def receive(self, phone, delay=10, repeat=20):
        """
        收取一条指定号码的短信
        :param phone string: 指定的电话号码
        :param delay int: 每一次尝试取短信的延迟时间， 单位秒
        :param repeat int: 尝试取短信的最大次数，
        :return string|None: 返回获取到的短信str， 获取不到则返回None
        """
        pass

    @abstractmethod
    def send(self, phone, sendMsg):
        """
        使用指定号码发送一条短信
        :param phone: 指定的电话号码
        :param sendMsg: 要发送的短信内容
        :return string|None: 获得的手机短信, 失败返回None
        """
        pass

    @abstractmethod
    def sendAndRecv(self, sendMsg, max=3):
        """
        获取一个号码， 发送一条短信， 然后获取相同号码的一条短信
        :param sendMsg:
        :return dict: phone, msg
        """
        pass

class Cloudma(Sms):
    """
    爱乐赞短信平台
    """

    def __init__(self, apiAccount, password, recvProjectId, sendProjectId=None):
        self.token = None
        self.apiAccount = apiAccount
        self.password = password
        self.sendProjectId = sendProjectId
        self.recvProjectId = recvProjectId
        project = []
        if sendProjectId:
            project.append(sendProjectId)
        if recvProjectId:
            project.append(recvProjectId)
        project.sort()
        self.project = ','.join(project)

        self.apiBaseUri = 'http://api.xingjk.cn/api/do.php'


    def getToken(self):
        """
        获取爱乐赞token
        :return:
        """
        i = 0
        while not self.token:
            try:
                i += 1
                response = requests.post(self.apiBaseUri,{
                    'action': 'loginIn',
                    'name': self.apiAccount,
                    'password': self.password
                }, timeout=60)
                ret = response.text.split('|')
                if ret[0]=='1':
                    self.token = ret[1]
                else:
                    logger().error('爱乐赞获取token失败')
                    time.sleep(5)
            except:
                logger().error('爱乐赞获取token失败')
                time.sleep(5)

        return self.token


    def getPhone(self, phone=None, max=20):
        i = 0
        while(i<max):
            i += 1
            try:
                response = requests.post(self.apiBaseUri,{
                    'action': 'getPhone',
                    'sid': self.project,
                    'token': self.getToken(),
                    'phone': phone,
                    'vno':0,
                }, timeout=60)
                ret = response.text.split('|')
                if(ret[0]=='1'):
                    return ret[1]
                else:
                    time.sleep(10)

            except Exception as e:
                logger().error(traceback.format_exc())
                time.sleep(10)

        return None

    def sendAndRecv(self, sendMsg,max=3):
        i = 0
        while(i<max):
            i += 1
            phone = None
            try:
                phone = self.getPhone()
                if(phone):
                    sent = self.send(phone, sendMsg)
                    if(sent):
                        time.sleep(10)
                        msg = self.receive(phone)
                        if(msg):
                            return {'phone': phone, 'msg':msg}
            except Exception as e:
                if(phone):
                    self.release_phone(phone)
                logger().error(traceback.format_exc())
        return None

    def send(self, phone, sendMsg, max=5):
        """
        发送成功返回true, 失败false
        :param phone:
        :param sendMsg:
        :param max:
        :return:
        """
        i = 0
        while (i < max):
            try:
                i += 1
                response = requests.post(self.apiBaseUri, {
                    'action': 'putSentMessage',
                    'token': self.getToken(),
                    'phone': phone,
                    'sid': self.sendProjectId,
                    'message': sendMsg
                }, timeout=60)
                ret = response.text.split('|')
                if(ret[0]=='1'):
                    logger().info('成功提交短信发送:'+phone+' 发送 '+sendMsg)
                    return True
                time.sleep(10)
            except Exception as e:
                logger().error(traceback.format_exc())
                time.sleep(10)

        return False

    def receive(self, phone, delay=10, repeat=10):
        i = 0
        while(i<repeat):
            i+=1
            try:
                response = requests.post(self.apiBaseUri, {
                    'action': 'getMessage',
                    'token': self.getToken(),
                    'phone': phone,
                    'sid': self.recvProjectId
                }, timeout=60)
                ret = response.text.split('|')
                if(ret[0]=='1'):
                    return ret[1]
                time.sleep(10)
            except Exception as e:
                logger().error(traceback.format_exc())
                time.sleep(10)

        return None

    def blacklist(self, phone):
        response = requests.post(self.apiBaseUri, {
            'action': 'addBlacklist',
            'token': self.getToken(),
            'phone': phone,
            'sid': self.project
        }, timeout=60)
        ret = response.text.split('|')
        if (ret[0] == '1'):
            logger().info('添加黑名单成功:' + phone)
            return True
        else:
            logger().info('添加黑名单失败:' + phone)
            return False

    def release_phone(self, phone):
        response = requests.post(self.apiBaseUri,{
            'action': 'cancelRecv',
            'token': self.getToken(),
            'phone': phone,
            'sid': self.project
        }, timeout=60)
        ret = response.text.split('|')
        if(ret[0]=='1'):
            logger().info('释放手机号成功:'+phone)
            return True
        else:
            logger().info('释放手机号失败:' + phone)
            return False

class Ema(Sms):
    """
    爱乐赞短信平台
    """

    def __init__(self, username, password, developer, project):
        self.token = None

        self.username = username
        self.password = password
        self.developer = developer
        self.project = project

        self.apiBaseUri = 'http://api.ema666.com/Api'


    def getToken(self):
        """
        获取爱乐赞token
        :return:
        """
        if(not self.token):
            token = None
            while token==None:
                try:
                    response = requests.get(self.apiBaseUri+'/userLogin', params={
                        'uName': self.username,
                        'pWord': self.password,
                        'Developer': self.developer
                    }, timeout=60)
                    if response.status_code!=200:
                        logger().error('ema登录失败: 响应码 {0}, 内容: \n{1}'.format(response.status_code, response.text))
                        time.sleep(10)
                        continue
                    ret = response.text.split('&')
                    if len(ret) < 2:
                        logger().error('ema登录失败: 服务器响应'+response.text)
                        time.sleep(10)
                        continue
                    self.token = ret[0]
                    break
                except:
                    logger().error('ema登录失败: 未捕获的异常\n'+traceback.format_exc())
                    time.sleep(10)


        return self.token


    def getPhone(self, phone=None, max=20):
        i = 0
        while(i<max):
            i += 1
            try:
                response = requests.get(self.apiBaseUri+'/userGetPhone', params={
                    'ItemId': self.project,
                    'token': self.getToken(),
                    'PhoneType': 0,
                    'Phone': phone
                }, timeout=60)
                if response.status_code!=200:
                    logger().error('获取号码失败， 服务器响应 {0}\n{1}'.format(response.status_code, response.text))
                    continue
                ret = response.text.split(';')
                if(len(ret)>1 and re.match('\d+',ret[0])):
                    return ret[0]
                else:
                    logger().error('获取号码失败， 服务器响应\n'+response.text)
                    time.sleep(10)
            except:
                logger().error(traceback.format_exc())
                time.sleep(10)

        return None

    def sendAndRecv(self, sendMsg,max=3):
        i = 0
        while(i<max):
            i += 1
            phone = None
            try:
                phone = self.getPhone()
                if(phone):
                    sent = self.send(phone, sendMsg)
                    if(sent):
                        time.sleep(10)
                        msg = self.receive(phone)
                        if(msg):
                            return {'phone': phone, 'msg':msg}
            except Exception as e:
                if(phone):
                    self.release_phone(phone)
                logger().error(traceback.format_exc())
        return None

    def send(self, phone, sendMsg, max=20):
        """
        发送成功返回true, 失败false
        :param phone:
        :param sendMsg:
        :param max:
        :return:
        """
        i = 0
        while (i < max):
            try:
                i += 1
                response = requests.get(self.apiBaseUri+'/userSendMessage', params={
                    'token': self.getToken(),
                    'Phone': phone,
                    'ItemId': self.project,
                    'Msg': sendMsg
                }, timeout=60)
                if response.status_code==200 and response.text.lower().find('ok')!=-1:
                    logger().info('成功提交短信发送:'+phone+' 发送 '+sendMsg)
                    return True
                time.sleep(10)
            except:
                logger().error(traceback.format_exc())
                time.sleep(10)

        return False

    def receive(self, phone, delay=10, repeat=20):
        i = 0
        while(i<repeat):
            i+=1
            try:
                response = requests.post(self.apiBaseUri+'/userSingleGetMessage', {
                    'token': self.getToken(),
                    'phone': phone,
                    'itemId': self.project
                }, timeout=60)
                if response.status_code==200 and response.text.find('MSG&')!=-1:
                    return response.text.replace('MSG&','')
                if response.status_code==200 and response.text=='False:此号码已经被释放':
                    return None
                time.sleep(10)
            except:
                logger().error(traceback.format_exc())
                time.sleep(10)


        return None

    def blacklist(self, phone):
        response = requests.post(self.apiBaseUri+'/userAddBlack', {
            'token': self.getToken(),
            'phoneList': '{0}-{1};'.format(self.project, phone)
        }, timeout=60)
        if response.status_code==200:
            logger().info('添加黑名单成功:' + phone)
            return True
        else:
            logger().info('添加黑名单失败:' + phone)
            return False

    def release_phone(self, phone):
        response = requests.post(self.apiBaseUri+'/userReleasePhone',{
            'token': self.getToken(),
            'phoneList': '{0}-{1};'.format(phone,self.project),
        }, timeout=60)
        if response.status_code==200:
            logger().info('释放手机号成功:'+phone)
            return True
        else:
            logger().info('释放手机号失败:' + phone)
            return False

class Yima(Sms):
    """
    爱乐赞短信平台
    """

    def __init__(self, token, recvProjectId, sendProjectId=None):
        self.token = token
        self.sendProjectId = sendProjectId
        self.recvProjectId = recvProjectId

        self.apiBaseUri = 'http://api.51ym.me/UserInterface.aspx'


    def getToken(self):
        """
        :return:
        """
        return self.token


    def getPhone(self, phone=None, max=20):
        projects = list()
        if self.recvProjectId:
            projects.append(self.recvProjectId)
        if self.sendProjectId:
            projects.append(self.sendProjectId)
        if len(projects)<1:
            raise Exception('短信平台没有配置项目id')

        for project_id in projects:
            phone = self.__getPhone(project_id, phone, max)
            if not phone:
                return None
        return phone

    def __getPhone(self, project_id, phone=None, max=20):
        i = 0
        while (i < max):
            i += 1
            try:
                response = requests.get(self.apiBaseUri, {
                    "action": "getmobile",
                    "itemid": project_id,
                    "token": self.getToken(),
                    'mobile': phone
                }, timeout=60)
                ret = response.text.split('|')
                if (ret[0] == 'success'):
                    return ret[1]
                else:
                    logger().info('易码取号失败')
                    time.sleep(10)

            except Exception:
                logger().error(traceback.format_exc())
                time.sleep(10)

        return None

    def sendAndRecv(self, sendMsg,max=3):
        i = 0
        while(i<max):
            i += 1
            phone = None
            try:
                phone = self.getPhone()
                if(phone):
                    sent = self.send(phone, sendMsg)
                    if(sent):
                        time.sleep(10)
                        msg = self.receive(phone)
                        if(msg):
                            return {'phone': phone, 'msg':msg}
            except Exception as e:
                if(phone):
                    self.release_phone(phone)
                logger().error(traceback.format_exc())
        return None

    def send(self, phone, sendMsg, max=10):
        """
        发送成功返回true, 失败false
        :param phone:
        :param sendMsg:
        :param max:
        :return:
        """
        i = 0
        while (i < max):
            try:
                i += 1
                response = requests.get(self.apiBaseUri, {
                    'action': 'sendsms',
                    'token': self.getToken(),
                    'mobile': phone,
                    'itemid': self.sendProjectId,
                    'sms': sendMsg
                }, timeout=60)
                if(response.text.find('success')!=-1):
                    logger().info('成功提交短信发送:'+phone+' 发送 '+sendMsg)
                    return True
                time.sleep(10)
            except:
                logger().error(traceback.format_exc())
                time.sleep(10)
            finally:
                # fixme: 也许需要释放手机号
                pass
        return False

    def receive(self, phone, delay=10, repeat=20):
        i = 0
        while(i<repeat):
            i+=1
            try:
                response = requests.get(self.apiBaseUri, {
                    'action': 'getsms',
                    'token': self.getToken(),
                    'mobile': phone,
                    'itemid': self.recvProjectId,
                    'release': '1'
                }, timeout=60)
                response.encoding = 'utf8'
                ret = response.text.split('|')
                if(ret[0]=='success'):
                    return ret[1]
                if(ret[0]=='2008'):
                    logger().error('手机号已被释放')
                    return None
                time.sleep(10)
            except:
                logger().error(traceback.format_exc())
                time.sleep(10)

        return None

    def blacklist(self, phone):
        try:
            if self.recvProjectId:
                response = requests.get(self.apiBaseUri, {
                    'action': 'addignore',
                    'token': self.getToken(),
                    'mobile': phone,
                    'itemid': self.recvProjectId
                }, timeout=60)
            if self.sendProjectId:
                response = requests.get(self.apiBaseUri, {
                    'action': 'addignore',
                    'token': self.getToken(),
                    'mobile': phone,
                    'itemid': self.sendProjectId
                }, timeout=60)
            ret = response.text.split('|')
            if (ret[0] == 'success'):
                logger().info('添加黑名单成功:' + phone)
                return True
            else:
                logger().info('添加黑名单失败:' + phone)
                return False
        except:
            return False

    def release_phone(self, phone):
        try:
            if self.recvProjectId:
                response = requests.get(self.apiBaseUri, {
                    'action': 'release',
                    'token': self.getToken(),
                    'mobile': phone,
                    'itemid': self.recvProjectId
                }, timeout=60)
            if self.sendProjectId:
                response = requests.get(self.apiBaseUri, {
                    'action': 'release',
                    'token': self.getToken(),
                    'mobile': phone,
                    'itemid': self.sendProjectId
                }, timeout=60)
            ret = response.text.split('|')
            if(ret[0]=='success'):
                logger().info('释放手机号成功:'+phone)
                return True
            else:
                logger().info('释放手机号失败:' + phone)
                return False
        except:
            return False

class EyuanSms(Sms):

    def __init__(self, project):
        self.project = project
        self.apiBaseUri = 'http://yangmao.ieyuan.com/sms'

    def getPhone(self, phone=None, max=20):
        i = 0
        while (i < max):
            i += 1
            try:
                response = requests.get(self.apiBaseUri+'/get-phone', {
                    'project_id': self.project,
                    'phone': phone
                }, timeout=60)
                ret = response.json()
                if (ret['code'] == 1):
                    return ret['msg']
                else:
                    time.sleep(10)

            except:
                logger().error(traceback.format_exc())
                time.sleep(10)

        return None

    def receive(self, phone, delay=10, repeat=20):
        i = 0
        while (i < repeat):
            i += 1
            try:
                response = requests.get(self.apiBaseUri+'/receive/{0}/{1}'.format(self.project, phone), timeout=60)
                ret = response.json()
                if (ret['code'] == 1):
                    return ret['msg']
                time.sleep(10)
            except:
                logger().error(traceback.format_exc())
                time.sleep(10)

        return None

    def send(self, phone, sendMsg, max=20):
        """
                发送成功返回true, 失败false
                :param phone:
                :param sendMsg:
                :param max:
                :return:
        """
        i = 0
        while (i < max):
            try:
                i += 1
                response = requests.post(self.apiBaseUri+'/send', {
                    'phone': phone,
                    'project_id': self.project,
                    'msg': sendMsg
                }, timeout=60)
                ret = response.json()
                if (ret['code'] == 1):
                    logger().info('成功提交短信发送:' + phone + ' 发送 ' + sendMsg)
                    return True
                time.sleep(10)
            except:
                logger().error(traceback.format_exc())
                time.sleep(10)

        return False

    def sendAndRecv(self, sendMsg,max=3):
        """
        发送并收取短信， 返回号码和收到的短信
        :param sendMsg:
        :param max:
        :return dict: phone: 号码,   msg: 短信内容
        """
        i = 0
        while(i<max):
            i += 1
            phone = None
            try:
                phone = self.getPhone()
                if(phone):
                    sent = self.send(phone, sendMsg)
                    if(sent):
                        time.sleep(10)
                        msg = self.receive(phone)
                        if(msg):
                            return {'phone': phone, 'msg':msg}
            except:
                if(phone):
                    self.release_phone(phone)
                logger().error(traceback.format_exc())
        return None

    def release_phone(self, phone):
        # 平台并没有此api
        return True

class HkSms():

    def __init__(self):
        pass

    def sendAndRecv(self, sendMsg, targetPhone):
        """
        获取一个号码， 向目标号码发送一条短信， 然后获取相同号码的一条短信
        :param sendMsg:
        :return dict: phone, msg
        """
        response = requests.post('http://yangmao.ieyuan.com/api/hk/send-recv',data={
            'msg':sendMsg,
            'target_phone':targetPhone
        },timeout=60*5)
        if response==None:
            return None

        if response.status_code!=200:
            return None

        json = response.json()
        if json['code']==1:
            msg = json['msg']
            ret = msg.split('|',1)
            return {'phone': ret[0], 'msg': ret[1]}

        return None
        pass

if __name__=='__main__':

    sms = HkSms()
    ret = sms.sendAndRecv('JFKDJF*$(','85256434822')
    print ret

