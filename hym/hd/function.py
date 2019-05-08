# coding=utf-8
import subprocess
import re
import string
import random
import json
import time
import os
import redis
from datetime import datetime
import hashlib
import lxml.html as xt
import requests
from hym import api_client

def conversion(strs):
	dw=None
	ints=''
	for x in strs:
		if x.isdigit() or x=='.':
			ints=ints+str(x)
			continue
			pass
		pass
		dw=x
	intf=1
	if dw=='亿':
		intf=100000000
		pass
	if dw=='万':
		intf=10000
		pass
	if dw=='千':
		intf=1000
		pass
	return int(float(ints)*intf)
	pass
def link_redis(host='127.0.0.1',port=6379,db=0):
	pool = redis.ConnectionPool(host=host, port=port, db=db)
	r = redis.Redis(connection_pool=pool)
	return r
	pass
def random_time():
	ints=random.randrange(1,500)
	return ints
	pass
def md5(strs):
	m=hashlib.md5()
	m.update(str(strs))
	return m.hexdigest()
	pass
def SetKey(time,url):
	time_s=int(time.strftime('%S'))
	time_i=int(time.strftime('%M'))
	mumber=int((time_s+time_i)/time_i)
	post_key=''
	i=0
	while i<mumber:
		post_key=md5(str(post_key)+str(url)+str(mumber)+str(time_s)+str(i))
		i+=1
		pass
	return post_key
	pass
def get_NewNotice():#/gicp/news/102/6637780.html返回最新的列表http://stzb.163.com/notice/2019/04/30/20399_811347.html
	#json_data='{"qq_pg":{"href":"https://pg.qq.com/gicp/news/102/6600643.html"},"wy_stzb":{"href":"//stzb.163.com/notice/2019/04/19/20399_809590.html"}}'
	#json_data='{"qq_pg":{"href":"https://pg.qq.com/gicp/news/102/6637780.html"},"wy_stzb":{"href":"http://stzb.163.com/notice/2019/04/23/20399_810226.html"}}'
	#json_data='{"qq_gp":{"href":"https://gp.qq.com/web20190423/detail_news.html?newsid=6646668"},"qq_pg":{"href":"https://pg.qq.com/gicp/news/102/6637780.html"},"wy_stzb":{"href":"http://stzb.163.com/notice/2019/04/30/20399_811348.html"}}'
	json_data=api_client.client.get_yxgg_newnotice()
	return json.loads(json_data)
	pass
def get_NoticeList():
	json_data1='{'
	json_data2='"qq_pg":{"href":"https://pg.qq.com/gicp/news/101/2/2003/1.html","company_name":"腾讯","name":"刺激战场","port_type":"wap"},'
	json_data3='"wy_stzb":{"href":"http://stzb.163.com/notice/","company_name":"网易","name":"率土之滨","port_type":"wap"}'
	#json_data4='"qq_pvp":{"href":"https://pvp.qq.com/webplat/info/news_version3/15592/24091/24092/24095/m15240/list_1.shtml","company_name":"腾讯","name":"王者荣耀","port_type":"wap"}'
	json_data_e='}'
	#json_data=str(json_data1+json_data2+json_data3+json_data_e)
	json_data=api_client.client.get_yxgg_noticelist()
	#print json_data
	return json.loads(json_data)
	pass
def clean_NoticeList(data,types,configs):
	config=get_NewNotice()
	if types=='qq_pg':
		return qq_pg_clean_NoticeList(data,config,configs)
		pass
	if types=='wy_stzb':
		return wy_stzb_clean_NoticeList(data,config,configs)
		pass
	if types=='qq_pvp':
		return qq_pvp_clean_NoticeList(data,config,configs)
		pass
	if types=='qq_gp':
		return qq_gp_clean_NoticeList(data,config,configs)
		pass
	return {}
	pass
def qq_gp_clean_NoticeList(data,config,configs):#腾讯和平精英
	datas=data.split(configs['rm']+'=')[1][:-1]
	datas=json.loads(datas)['msg']['result']
	y=0
	lists={}
	for x in datas:
		if not config.has_key('qq_gp'):
			lists[y]={
			'href':configs['detail_new_url']+x['iNewsId'],#和平精英原创地址
			'json_href':configs['detail_new_json_url']+x['iNewsId'],#和平精英数据接口地址
			'title':x['sTitle'],
			'time':x['sCreated'],
			'company_name':configs['company_name'],
			'name':configs['name'],
			'port_type':configs['port_type'],
			}
			y+=1
			continue
			pass
		if configs['detail_new_url']+x['iNewsId']!=config['qq_gp']['href']:
			lists[y]={
			'href':configs['detail_new_url']+x['iNewsId'],#和平精英原创地址
			'json_href':configs['detail_new_json_url']+x['iNewsId'],#和平精英数据接口地址
			'title':x['sTitle'],
			'time':x['sCreated'],
			'company_name':configs['company_name'],
			'name':configs['name'],
			'port_type':configs['port_type'],
			}
			pass
		if configs['detail_new_url']+x['iNewsId']==config['qq_gp']['href']:
			break
			pass
		y+=1
		pass
	lists_w={}
	w_y=0
	while w_y<len(lists):
		lists_w[w_y]=lists[len(lists)-1-w_y]
		w_y+=1
		pass
	return lists_w
	pass
def qq_pvp_clean_NoticeList(data,config,configs):#腾讯王者荣耀列表解析
	a=xt.fromstring(data)
	novelContent=a.xpath('//div[@class="art_lists"]')
	ul=novelContent[0].xpath('ul')
	li=ul[0].xpath('li')
	y=0
	lists={}
	for x in li:#https://pvp.qq.com
		href=x.xpath('a[@class="art_word"]/@href')
		if not config.has_key('qq_pvp'):
			title=x.xpath('a[@class="art_word"]/text()')
			time=x.xpath('span[@class="art_day"]/text()')
			lists[y]={
			'href':'https://pvp.qq.com'+href[0],
			'title':title[0],
			'time':time[0],
			'company_name':configs['company_name'],
			'name':configs['name'],
			'port_type':configs['port_type'],
			}
			y+=1
			continue
			pass
		if 'https://pvp.qq.com'+href[0]!=config['qq_pvp']['href']:
			title=x.xpath('a[@class="art_word"]/text()')
			time=x.xpath('span[@class="art_day"]/text()')
			lists[y]={
			'href':'https://pvp.qq.com'+href[0],
			'title':title[0],
			'time':time[0],
			'company_name':configs['company_name'],
			'name':configs['name'],
			'port_type':configs['port_type'],
			}
			pass
		if 'https://pvp.qq.com'+href[0]==config['qq_pvp']['href']:
			break
			pass
		y+=1
		pass
	lists_w={}
	w_y=0
	while w_y<len(lists):#倒序
		lists_w[w_y]=lists[len(lists)-1-w_y]
		w_y+=1
		pass
	return lists_w
	pass
def qq_pg_clean_NoticeList(data,config,configs):#腾讯刺激战场列表解析
	a=xt.fromstring(data)
	novelContent=a.xpath('//div[@class="news-detail"]')
	ul=novelContent[0].xpath('ul')
	li=ul[0].xpath('li')
	y=0
	lists={}
	for x in li:
		href=x.xpath('a/@href')
		if not config.has_key('qq_pg'):
			title=x.xpath('a/text()')
			time=x.xpath('span/text()')
			lists[y]={
			'href':'https://pg.qq.com'+href[0],
			'title':title,
			'time':time,
			'company_name':configs['company_name'],
			'name':configs['name'],
			'port_type':configs['port_type'],
			}
			y+=1
			continue
			pass
		if 'https://pg.qq.com'+href[0]!=config['qq_pg']['href']:
			title=x.xpath('a/text()')
			time=x.xpath('span/text()')
			lists[y]={
			'href':'https://pg.qq.com'+href[0],
			'title':title,
			'time':time,
			'company_name':configs['company_name'],
			'name':configs['name'],
			'port_type':configs['port_type'],
			}
			pass
		if 'https://pg.qq.com'+href[0]==config['qq_pg']['href']:
			break
			pass
		y+=1
		pass
	lists_w={}
	w_y=0
	while w_y<len(lists):
		lists_w[w_y]=lists[len(lists)-1-w_y]
		w_y+=1
		pass
	return lists_w
	pass
def wy_stzb_clean_NoticeList(data,config,configs):#网易率土之滨列表解析
	a=xt.fromstring(data)
	novelContent=a.xpath('//ul[@class="txt-list"]')
	li=novelContent[0].xpath('li')
	y=0
	lists={}
	for x in li:
		div=x.xpath('div[@class="item-inner"]')
		href=div[0].xpath('a/@href')
		href[0]='http://'+href[0][2:len(href[0])]#处理率土之滨列表的链接
		if not config.has_key('wy_stzb'):
			title=div[0].xpath('a/@title')
			time=None
			lists[y]={
			'href':href[0],
			'title':title[0].decode('utf-8'),
			'time':time,
			'company_name':configs['company_name'],
			'name':configs['name'],
			'port_type':configs['port_type'],
			}
			y+=1
			continue
			pass
		if href[0]!=config['wy_stzb']['href']:
			title=div[0].xpath('a/@title')
			time=None
			lists[y]={
			'href':href[0],
			'title':title[0].decode('utf-8'),
			'time':time,
			'company_name':configs['company_name'],
			'name':configs['name'],
			'port_type':configs['port_type'],
			}
			pass
		if href[0]==config['wy_stzb']['href']:
			break
			pass
		y+=1
		pass
	lists_w={}
	w_y=0
	while w_y<len(lists):#倒序
		lists_w[w_y]=lists[len(lists)-1-w_y]
		w_y+=1
		pass
	return lists_w
	pass
def qq_gp_clean_NoticeArticle(data,configs):#和平精英处理每篇公告的内容并返回提交服务器的数据
	time.sleep(3)
	datas=data.split('searchObj=')[1][:-1]
	datas=json.loads(datas)
	sContent=datas['msg']['sContent']
	a=xt.fromstring(sContent)
	imgUrl=a.xpath('//img/@src')
	im_y=0
	while im_y<len(imgUrl):
		newImgUrl=get_imgUp(imgUrl[im_y])
		thImgUrl=imgUrl[im_y].split("?")
		sContent=sContent.replace(thImgUrl[0],newImgUrl)
		im_y+=1
		pass
	reData={
	'notice_content':sContent,
	'notice_title':configs['title'],
	'notice_url':configs['href'],
	'game_name':configs['name'],
	'port_type':configs['port_type'],
	'game_company':configs['company_name'],
	'notice_time':configs['time'],
	}
	return reData
	pass
def qq_pg_clean_NoticeArticle(data,configs):#处理每篇公告的内容并返回提交服务器的数据
	time.sleep(3)
	a=xt.fromstring(data)
	articleBox=a.xpath('//div[@class="article-box"]')
	articleBoxStr=get_inner_html(articleBox[0])
	img=xt.fromstring(articleBoxStr)
	imgUrl=img.xpath('//img/@src')
	notice_time=a.xpath('//span[@class="detail-date"]/text()')
	im_y=0
	while im_y<len(imgUrl):
		newImgUrl=get_imgUp(imgUrl[im_y])
		thImgUrl=imgUrl[im_y].split("?")
		articleBoxStr=articleBoxStr.replace(thImgUrl[0],newImgUrl)
		im_y+=1
		pass
	reData={
	'notice_content':str(articleBoxStr),
	'notice_title':configs['title'][0],
	'notice_url':configs['href'],
	'game_name':configs['name'],
	'port_type':configs['port_type'],
	'game_company':configs['company_name'],
	'notice_time':notice_time[0],
	}
	return reData
	pass
def wy_stzb_clean_NoticeArticle(data,configs):
	time.sleep(3)
	a=xt.fromstring(data)
	articleBox=a.xpath('//div[@class="artText"]')
	articleBoxStr=get_inner_html(articleBox[0])
	img=xt.fromstring(articleBoxStr)
	imgUrl=img.xpath('//img/@src')
	notice_time=a.xpath('//span[@class="artDate"]/text()')
	im_y=0
	while im_y<len(imgUrl):
		newImgUrl=get_imgUp(imgUrl[im_y])
		articleBoxStr=articleBoxStr.replace(imgUrl[im_y],newImgUrl)
		im_y+=1
		pass
	reData={
	'notice_content':str(articleBoxStr),#str(articleBoxStr),
	'notice_title':configs['title'],
	'notice_url':configs['href'],
	'game_name':configs['name'],
	'port_type':configs['port_type'],
	'game_company':configs['company_name'],
	'notice_time':notice_time[0],
	}
	return reData
	pass
def qq_pvp_clean_NoticeArticle(data,configs):
	time.sleep(3)
	a=xt.fromstring(data)
	articleBox=a.xpath('//div[@class="art_dmain"]')
	articleBoxStr=get_inner_html(articleBox[0])#将对象转换问html
	img=xt.fromstring(articleBoxStr)
	imgUrl=img.xpath('//img/@src')
	notice_time=a.xpath('//span[@id="Freleasetime"]/text()')
	im_y=0
	while im_y<len(imgUrl):
		if '../' in imgUrl[im_y]:
			im_y+=1
			continue
			pass
		thImgUrl_h=imgUrl[im_y]
		if not('https:' in imgUrl[im_y]) and not('http:' in imgUrl[im_y]):
			imgUrl[im_y]='https:'+imgUrl[im_y]
			pass
		newImgUrl=get_imgUp(imgUrl[im_y])
		thImgUrl=thImgUrl_h
		if '?' in thImgUrl_h:
			thImgUrls=thImgUrl_h.split("?")
			thImgUrl=thImgUrls[0]
			pass
		articleBoxStr=articleBoxStr.replace(thImgUrl,newImgUrl)
		im_y+=1
		pass
	reData={
	'notice_content':str(articleBoxStr),
	'notice_title':configs['title'],
	'notice_url':configs['href'],
	'game_name':configs['name'],
	'port_type':configs['port_type'],
	'game_company':configs['company_name'],
	'notice_time':notice_time[0],
	}
	return reData
	pass
def get_inner_html(node):
	html=xt.tostring(node)
	p_begin = html.find('>') + 1
	p_end = html.rfind('<')
	return html[p_begin: p_end]
	pass
def get_imgUp(urls):#获取图片上传服务器返回上传后地址
	response = requests.get(urls,None,proxies=None, timeout=30)
	rul=api_client.client.post_yxgg_img_content(response.content)
	return 'http://'+rul
	pass
def create_17_number():#随机生成17位数字
	no1=random.randint(20000000,899999999)
	no2=random.randint(1000000,99999999)
	re=str(no1)+str(no2)
	return re
	pass
def ces():
	print api_client.client.cela()
	pass