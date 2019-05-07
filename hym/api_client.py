# coding=utf-8
import requests
import json

class ApiClient:

    def __init__(self):
        #self.server = 'http://yangmao.ieyuan.com'
        self.server = 'http://ggj.api.qinpl.cn'
        #self.server = 'http://api.yxgg.com'
        #self.server = 'http://hd.qinpl.cn/api.php'
        # self.proxies = {'http':'http://127.0.0.1:8888','https':'http://127.0.0.1:8888'}
        self.proxies = None

    def getReservePhone(self):
        """
        获得需要预约的机型列表
        :return: 一个dict， key为part_number， value为dict，包含机型参数
        """
        response = requests.get(self.server+'/api/reserve-phones',None,proxies=self.proxies, timeout=30)
        if(response.status_code==200):
            phones = json._default_decoder.decode(response.text)
            return phones
        else:
            raise Exception('无法获取预约机型'+'status code: '+str(response.status_code)+', '+response.text)

    def getReserveStore(self):
        """
        获得需要预约的店铺列表
        :return: 一个dict， key为店铺编号， value为dict，包含店铺参数
        """
        response = requests.get(self.server+'/api/reserve-stores',None,proxies=self.proxies,timeout=30)
        if(response.status_code==200):
            stores = json._default_decoder.decode(response.text)
            return stores
        else:
            raise Exception('无法获取预约店铺'+'status code: '+str(response.status_code)+', '+response.text)

    def getAppleid(self):
        response = requests.get(self.server+'/api/appleid',None,proxies=self.proxies,timeout=30)
        if response.status_code==200:
            account = json.loads(response.text)
            return account
        else:
            return None

    def getIdcard(self, city):
        """
        获得一个指定城市的身份证
        :param string city: eg. 上海 成都 等等
        :return map: 返回一个dict对象
        """
        response = requests.get(self.server+'/api/idcard', {'city':city}, proxies=self.proxies,timeout=30)
        if(response.status_code==200):
            data = json.loads(response.text)
            return data
        return None

    def postReseration(self, part_number, quantity, appleid, government_id, firstname, lastname, store, response_log):
        """
        上传成功预约记录到服务器
        :param str part_number:
        :param int quantity:
        :param str appleid:
        :param str government_id:
        :param str firstname:
        :param str lastname:
        :param str store:
        :param str response_log:
        :return:
        """
        response = requests.post(self.server+'/api/iphone_reservation',{
            'part_number': part_number,
            'quantity': quantity,
            'appleid': appleid,
            'government_id': government_id,
            'firstname': firstname,
            'lastname': lastname,
            'store': store,
            'response_log': response_log
        }, proxies=self.proxies)
        if response.status_code!=200:
            pass

    def destroy_me(self):
        """
        向服务器请求， 销毁我这台服务器吧
        :return:
        """
        response = requests.post(self.server+'/api/ecs/destroy',timeout=10)

    def get_proxy(self):
        """
        获取芝麻代理
        :return:
        """
        # response = requests.get(self.server+'/api/zhima/proxy',timeout=20)
        response = requests.get(self.server+'/api/zhima/proxy', timeout=60)
        return response


    def send_mail(self,subject,content='',to='36437395@qq.com'):
        """
        通过api server发送邮件
        :param str to:
        :param str subject:
        :param str content:
        :rtype boll:
        """
        response = requests.post(self.server+'/api/mail',data={
            'to': to,
            'subject': subject,
            'content': content
        },timeout=20)
        if response==None or response.status_code!=200:
            return False
        return True

    def post_log(self, type, file_path):
        try:
            response = requests.post(self.server+'/api/iphone/fail-log',data={'type': type},files={'log': open(file_path,'rb')})
        except:
            return False

        if response==None or response.status_code!=200:
            return False
        return True

    def get_jd_session(self, account):
        try:
            response = requests.get(self.server+'/jd/session', {'account': account})
            if response.status_code != 200:
                return None
            else:
                session = response.json()
                return session
        except:
            return None

    def post_jd_session(self, account, session):
        try:
            response = requests.post(self.server+'/jd/session', json={
                'account': account,
                'session': session
            })
            if response.status_code==200:
                return True
            return False
        except:
            return False
            pass
    def post_de_jd_session(self, account):
        try:
            response = requests.post(self.server+'/jd/de_session',json={
                'account':account
            })
            if response.status_code==200:
                return True
            return False
        except:
            return False

    def post_hd_anovel_content(self,data,key,now_time):
        try:
            response = requests.post(self.server+'?op=add_content',headers={
                'KEY':key,
                'TIMESTAMP':str(now_time)
                },data=data)
            return True
            pass
        except :
            return False
        pass
    def post_hd_img_content(self,data):
        try:
            response = requests.post(self.server+'?op=up',data=data)
            return response.content
            pass
        except :
            return False
        pass
    def post_yxgg_notice_data(self,data):
        try:
            response=requests.post(self.server+'/index.php?r=notice/apiadd',headers={},data=data)
            return True
            pass
        except :
            return False
        pass
    def post_yxgg_img_content(self,data):
        try:
            response = requests.post(self.server+'/index.php?r=notice/up',data=data)
            return response.content
            pass
        except Exception, e:
            return False
        pass
    def get_yxgg_newnotice(self):
        try:
            response = requests.get(self.server+'/index.php?r=notice/newnotice')
            return response.content
            pass
        except Exception, e:
            return False
        pass
    def get_yxgg_noticelist(self):
        try:
            response = requests.get(self.server+'/index.php?r=notice/noticelist')
            return response.content
            pass
        except Exception, e:
            return False
        pass
    def cela(self):
        return 'lslls'
        pass



client = ApiClient()

if __name__=='__main__':

    print (client.post_log('hehe', '/Users/yang/projects/yangmao/python-task-executor/logs/iphone_2017-10-13-11:00:15_140736899208128.log'))

