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
        app_log_path = sys.path[0] + '/logs/hd/{2}/{0}_{1}.log'.format(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'),
                                                                       random.randint(100000, 9999999),datetime.now().strftime('%Y_%m_%d'))
        self.context.logger = getLogger(app_log_path, True)
        self.context.app_log_path = app_log_path
        hym.core.default_logger = self.context.logger
        # requests初始化
        requests.packages.urllib3.disable_warnings()
        self.context.session = requests.session()
        self.context.session.verify = False
        log_path = sys.path[0] + '/logs/request_log/{2}/{0}_{1}.log'.format(time.strftime('%Y-%m-%d_%H-%M-%S_'),
                                                                        random.randint(1000000, 9999999),datetime.now().strftime('%Y_%m_%d'))
        if not os.path.isdir(os.path.split(log_path)[0]):
            os.makedirs(os.path.split(log_path)[0])
            pass
        logger().info('request log path: {0}'.format(log_path))
        requestLogAdapter = RetryAdapter(self.check_retry, log_path, max_retries=5)
        self.context.session.mount('http://', requestLogAdapter)
        self.context.session.mount('https://', requestLogAdapter)
        self.context.session.headers.update({
            '(Request-Line)': 'GET /htm/novel1/27695.htm HTTP/1.1',
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240',
            'Accept':'text/html, application/xhtml+xml, image/jxr, */*',
            'Accept-Language':'zh-CN',
     })
        self.context.request = self.request
        #初始化redis链接
        #self.context.redis=function.link_redis()
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

class getAnovel(Step):
    """docstring for getAnovel"""
    def execute(self, arguments):
        response=self.context.request('GET','https://www.306aa.com')
        host=response.url
        response=self.context.request('GET',host+'/xiaoshuo/list-都市激情-4.html')
        strs=response.content
        a=xt.fromstring(strs)
        #都市激情11431-19345 人妻交换18074-19335 校园春色19339-17971
        #ul=a.xpath('//ul[@class="textList"]')
        ul=a.xpath('//ul')
        lens=len(ul)
        li=ul[lens-1].xpath('li')
        y=0
        listss={}
        for x in li:
            href=x.xpath('a/@href')
            title=x.xpath('a/text()')
            listss[y]={
            'href':host+str(href[0]),
            'title':title
            }
            y+=1
            pass
        self.context.AnovelLists=listss
        

class getAnovelContent(Step):
    """docstring for getAnovelContent"""
    def execute(self, arguments):
        list_i=19#19
        dataLists=self.context.AnovelLists
        response=self.context.request('GET',dataLists[list_i]['href'])
        strs=response.content
        a=xt.fromstring(strs)
        novelContent=a.xpath('//div[@class="content"]')
        novelContentText=xt.tostring(novelContent[0])
        tylpi=2#1为收费其他为不收费
        data={
        'info[thumb]':'',
        'info[relation]':'',
        'info[inputtime]':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'info[islink]':0,
        'info[template]':'',
        'info[allow_comment]':1,
        'info[readpoint]':'',#收费点数
        'info[paytype]':'',
        'status':99,
        'info[catid]':15,#栏目id 14收费小说 15免费小说
        'info[title]':dataLists[list_i]['title'],
        'style_color':'',
        'style_font_weight':'',
        'info[keywords]':dataLists[list_i]['title'],
        'info[copyfrom]':'',
        'copyfrom_data':0,
        'info[description]':dataLists[list_i]['title'],#简介
        'info[lure]':'',#收费小说的免费查看部分
        'page_title_value':'',
        'info[content]':novelContentText,
        'page_title_value':'',
        'add_introduce':1,
        'introcude_length':200,
        'auto_thumb':1,
        'auto_thumb_no':1,
        'info[paginationtype]':0,
        'info[maxcharperpage]':10000,
        'info[posids][]':-1,
        'info[groupids_view]':1,
        'info[voteid]':'',
        'dosubmit':'保存后自动关闭'
        }
        if tylpi==1:
            data={
            'info[thumb]':'',
            'info[relation]':'',
            'info[inputtime]':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'info[islink]':0,
            'info[template]':'',
            'info[allow_comment]':1,
            'info[readpoint]':'35',#收费点数
            'info[paytype]':'',
            'status':99,
            'info[catid]':14,#栏目id 14收费小说 15免费小说
            'info[title]':dataLists[list_i]['title'],
            'style_color':'',
            'style_font_weight':'',
            'info[keywords]':dataLists[list_i]['title'],
            'info[copyfrom]':'',
            'copyfrom_data':0,
            'info[description]':dataLists[list_i]['title'],#简介
            'info[lure]':novelContentText[50:1700],#收费小说的免费查看部分
            'page_title_value':'',
            'info[content]':novelContentText,
            'page_title_value':'',
            'add_introduce':1,
            'introcude_length':200,
            'auto_thumb':1,
            'auto_thumb_no':1,
            'info[paginationtype]':0,
            'info[maxcharperpage]':10000,
            'info[posids][]':-1,
            'info[groupids_view]':1,
            'info[voteid]':'',
            'dosubmit':'保存后自动关闭'
            }
            pass
        s_now_time=datetime.now()
        now_time=int(time.mktime(time.strptime(s_now_time.strftime('%Y-%m-%d %H:%M:%S'),"%Y-%m-%d %H:%M:%S")))
        key=function.SetKey(s_now_time,'/api.php?op=add_content')
        api_client.client.post_hd_anovel_content(data,key,now_time)

class getMovie(Step):
    """docstring for ClassName"""
    def execute(self, arguments):
        response=self.context.request('GET','https://www.306aa.com')
        host=response.url
        self.context.hostss=host
        response=self.context.request('GET',host+'/shipin/list-欧美精品.html')
        strs=response.content
        strs=response.content
        a=xt.fromstring(strs)
        tpl_img_content=a.xpath('//div[@id="tpl-img-content"]')
        li=tpl_img_content[0].xpath('li')
        y=0
        listss={}
        for x in li:
            href=x.xpath('a/@href')
            title=x.xpath('a/@title')
            img=x.xpath('a/img/@data-original')
            listss[y]={
            'href':host+str(href[0]),
            'title':title,
            'img_url':img[0]
            }
            y+=1
            pass
        self.context.MovieLists=listss

class getImgUp(Step):
    """获取图片上传图片"""
    def execute(self, arguments):
        list_i=1#列表连接条数选择那个连接到4了 最多19
        self.context.list_i=list_i
        response=self.context.request('GET',self.context.MovieLists[list_i]['img_url'])
        img_re=api_client.client.post_hd_img_content(response.content)
        img_hugf=self.context.MovieLists[list_i]['img_url']
        if img_re and img_re!='no':
            img_hugf='http://'+img_re
            pass
        self.context.thumd=img_hugf
        

class getMovieData(Step):
    """docstring for ClassName"""
    def execute(self, arguments):
        list_i=self.context.list_i#列表连接条数选择那个连接
        xianlu_i=0#选择那个线路值只有0-2
        dataLists=self.context.MovieLists
        response=self.context.request('GET',dataLists[list_i]['href'])
        strs=response.content
        a=xt.fromstring(strs)
        novelContent=a.xpath('//a[@class="btn btn-m btn-default"]')
        url=novelContent[xianlu_i].get('href')
        url=self.context.hostss+str(url)
        response=self.context.request('GET',url)
        strs_a=response.content
        s=xt.fromstring(strs_a)
        scriptContent=s.xpath('//script')
        scriptContentText=xt.tostring(scriptContent[0])
        char_1="var video      = '"
        char_2="';"
        nPos=scriptContentText.index(char_1)
        ePos=scriptContentText.index(char_2)
        u38=scriptContentText[nPos:ePos] #截取第一位到第三位的字符
        u38_re=u38[(len(char_1)):(len(u38))]#获取到的u38
        #获取选择线路的域名
        if xianlu_i==0:
            char_x_1="var m3u8_host  = '"
            pass
        if xianlu_i==1:
            char_x_1="var m3u8_host1 = '"
            pass
        if xianlu_i==2:
            char_x_1="var m3u8_host2 = '"
            pass
        n_x_Pos=scriptContentText.index(char_x_1)
        x_strs=scriptContentText[n_x_Pos:len(scriptContentText)]
        re_x_strs=x_strs[len(char_x_1):x_strs.index(char_2)]#获取到的线路域名
        u38_res=re_x_strs+u38_re
        tylpi=1#1为收费其他为不收费
        data={
        'info[thumb]':self.context.thumd,
        'info[relation]':'',
        'info[inputtime]':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'info[template]':'',
        'info[allow_comment]':1,
        'info[readpoint]':'',#收费点数
        'info[paytype]':0,
        'status':99,
        'info[catid]':20,#栏目id 16收费小说 17免费小说
        'info[title]':dataLists[list_i]['title'],
        'style_color':'',
        'style_font_weight':'',
        'info[keywords]':'',
        'info[description]':dataLists[list_i]['title'],#简介
        'info[musource]':u38_res,
        'info[paginationtype]':0,
        'info[maxcharperpage]':10000,
        'info[posids][]':-1,
        'info[groupids_view]':1,
        'info[islink]':0,
        'dosubmit':'保存后自动关闭'
        }
        if tylpi==1:
            data={
            'info[thumb]':self.context.thumd,
            'info[relation]':'',
            'info[inputtime]':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'info[template]':'',
            'info[allow_comment]':1,
            'info[readpoint]':'10',#收费点数
            'info[paytype]':0,
            'status':99,
            'info[catid]':21,#栏目id 16收费小说 17免费小说
            'info[title]':dataLists[list_i]['title'],
            'style_color':'',
            'style_font_weight':'',
            'info[keywords]':'',
            'info[description]':dataLists[list_i]['title'],#简介
            'info[musource]':u38_res,
            'info[paginationtype]':0,
            'info[maxcharperpage]':10000,
            'info[posids][]':-1,
            'info[groupids_view]':1,
            'info[islink]':0,
            'dosubmit':'保存后自动关闭'
            }
            pass
        s_now_time=datetime.now()
        now_time=int(time.mktime(time.strptime(s_now_time.strftime('%Y-%m-%d %H:%M:%S'),"%Y-%m-%d %H:%M:%S")))
        key=function.SetKey(s_now_time,'/api.php?op=add_content')
        api_client.client.post_hd_anovel_content(data,key,now_time)
        
        
        


class runs(Step):
    """docstring for runs"""
    def execute(self, arguments):
        response=self.context.request('GET','https://mmslt1.com/uploads/thumb/20180928/zw_nFNweAD.jpg')
        img_re=api_client.client.post_hd_img_content(response.content)
        if img_re and img_re!='no':
            print img_re
            pass
        print img_re
        # response=self.context.request('GET',response.url+'/htm/movielist1/')
        # #response.encoding = response.apparent_encoding
        # strs=response.content
        # a=xt.fromstring(strs)
        # ul=a.xpath('//ul[@class="movieList"]')
        # li=ul[0].xpath('li')
        # y=0
        # listss={}
        # for x in li:
        #     img=x.xpath('a/img/@src')
        #     href=x.xpath('a/@href')
        #     title=(x.xpath('a/h3')[0]).text
        #     listss[y]={
        #     'title':title,
        #     'img':img[0],
        #     'href':response.url+str(href[0]),
        #     }
        #     y+=1
        #     pass
        # print listss
        # tl=response.text
        # strs=tl.decode("iso-8859-1")
        # strs=strs.encode("utf-8")
        # print strs

class getNoticeList(Step):#获取需要更新的游戏的公告地址列表
    """docstring for NoticeList"""
    def execute(self, arguments):
        notice_list=function.get_NoticeList()
        listss={}
        for x in notice_list.items():
            response=self.context.request('GET',x[1]['href'])
            texts=response.content.decode(response.apparent_encoding)
            listss[x[0]]=function.clean_NoticeList(texts,x[0],x[1])
            pass
        self.context.NoticeList=listss
        #print listss

class getNoticeList1(Step):#根据地址列表获取公告并且上传到服务器
    """docstring for NoticeList"""
    def execute(self, arguments):
        if self.context.NoticeList['qq_pg']:
            y=0
            while self.context.NoticeList['qq_pg'].has_key(y):
                response=self.context.request('GET',self.context.NoticeList['qq_pg'][y]['href'])
                Article=function.qq_pg_clean_NoticeArticle(response.content,self.context.NoticeList['qq_pg'][y])
                api_client.client.post_yxgg_notice_data(Article)
                logger().info(Article)
                logger().info('qinqinqin')
                y+=1
                pass
            pass
        if self.context.NoticeList['wy_stzb']:
            ws=0
            while self.context.NoticeList['wy_stzb'].has_key(ws):
                #print self.context.NoticeList['wy_stzb']
                response=self.context.request('GET',self.context.NoticeList['wy_stzb'][ws]['href'])
                response.encoding = response.apparent_encoding
                texts=response.text
                Article=function.wy_stzb_clean_NoticeArticle(texts,self.context.NoticeList['wy_stzb'][ws])
                api_client.client.post_yxgg_notice_data(Article)
                logger().info(Article)
                logger().info('qinqinqin')
                ws+=1
                pass
            pass
        if self.context.NoticeList['qq_pvp']:
            pvp=0
            while self.context.NoticeList['qq_pvp'].has_key(pvp):
                response=self.context.request('GET',self.context.NoticeList['qq_pvp'][pvp]['href'])
                Article=function.qq_pvp_clean_NoticeArticle(response.content,self.context.NoticeList['qq_pvp'][pvp])
                api_client.client.post_yxgg_notice_data(Article)
                logger().info(Article)
                logger().info('qinqinqin')
                pvp+=1
                pass
            pass
        #print self.context.NoticeList
        	