# coding=utf-8
import subprocess
import re
import string
import random
import json
import time
import os
import redis

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