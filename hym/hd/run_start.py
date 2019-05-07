# coding=utf-8
"""


"""
import sys
import os
import re


project_path = os.path.split(os.path.realpath(__file__))[0] + '/../..'
os.chdir(project_path)
sys.path.append(project_path)

from hym.core import Context, Pipeline
from hym.hd.steps import *

reload(sys)
sys.setdefaultencoding('utf-8')

if __name__ == '__main__':
	context=Context()

	steps=[
	Init,
	getNoticeList,
	getNoticeList1,
	#runs,
	#1.每隔一小时批量抓取接口中各种游戏的公告列表
	#2.对比数据库中需要更新的各种游戏公告游戏公告
	#3.
	#runs,
	#getMovie,
	#getImgUp,
	#getMovieData,
	# getAnovel,
	# getAnovelContent
	]
	pipeline=Pipeline(context, steps)
	pipeline.start()
	pass
#print function.random_time()
