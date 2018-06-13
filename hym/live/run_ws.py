# coding=utf-8
import socket
import time
from threading import Thread
import threading
import hashlib
import base64
import struct
import json

#print base64.b64encode(hashlib.sha1('dGhlIHNhbXBsZSBub25jZQ=='+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11').digest())
def ProcessData(data):
	code_len = ord(data[1]) & 127 
	if code_len==126:
		masks=data[4:8]
		datas=data[8:]
		pass
	elif code_len==127:
		masks=data[10:14]
		datas=data[14:]
	else:
		masks=data[2:6]
		datas=data[6:]
	i=0
	raw_str=''
	for d in datas:
		raw_str+=chr(ord(d) ^ ord(masks[i%4]))
		i+=1
		pass
	return raw_str
	pass
def ProcessSendData(data):
	token="\x81"
	length=len(data)
	if length<126:
		token+=struct.pack("B",length)
		pass
	elif length<=0xFFFF:
		token+=struct.pack("!BH",126,length)
	else:
		token+=struct.pack("!BQ",127,length)
	return '%s%s' % (token,data)
	pass
class returnCrossDomain(Thread):
	"""docstring for returnCrossDomain"""
	def __init__(self, connection, address, thread_list):
		Thread.__init__(self)
		self.con = connection
		self.address=address#自己链接的地址
		self.thread_list=thread_list
		self.isHandleShake = False
	def run(self):
		while True:
			if not self.isHandleShake:#建立握手
				clientData=self.con.recv(1024)
				if not clientData:
					try:#在没有握手成功的情况下关闭了链接
						clientData.close()
						pass
					except :
						ki=0
						for c in self.thread_list:
							if c[1]==self.address:
								self.thread_list.pop(ki)
								pass
							ki+=1
							pass
						break
					pass
				dataList=clientData.split('\r\n')
				header={}
				#print clientData
				for data in dataList:
					if ': ' in data:
						unit=data.split(': ')
						header[unit[0]]=unit[1]
						pass
					pass
				secKey=header['Sec-WebSocket-Key']
				resKey=base64.b64encode(hashlib.sha1(str(secKey)+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11').digest())
				response = '''HTTP/1.1 101 Switching Protocols\r\n'''
				response += '''Upgrade: websocket\r\n'''
				response += '''Connection: Upgrade\r\n'''
				response += '''Sec-WebSocket-Accept: %s\r\n'''%(resKey,)
				response += '''WebSocket-Protocol: chat\r\n\r\n'''
				self.con.send(response)
				members_list={}
				mk=0
				for m in self.thread_list:
					members_list[mk]=str(m[1][0])+':'+str(m[1][1])
					mk+=1
					pass
				re_data={
				'name':str(self.address[0])+'-'+str(self.address[1]),
				'ip':str(self.address[0]),
				'port':str(self.address[1]),
				'data':'加入聊天室',
				'members_list':members_list,
				'early_state':1
				}
				re_str=json.dumps(re_data)
				for l in self.thread_list:
					l[2].send(ProcessSendData(re_str))
					pass
				self.isHandleShake=True
				pass
			else:#已经建立
				try:
					data=self.con.recv(1024)#此处会阻塞，直到客户端发来信息
					data=ProcessData(data)#获取信息编码
					print self.thread_list
					if '@' in data:#其实私聊和群聊不需要更新用户列表的，只有在有用户退出时才更新用户列表(私聊格式@127.0.0.1:52019@我找3号)
						strs_a=data.split('@')
						strs_a_r=strs_a[1].split(':')
						for o in self.thread_list:
							if (str(o[1][0])==strs_a_r[0] and str(o[1][1])==strs_a_r[1]) or (str(o[1][0])==str(self.address[0]) and str(o[1][1])==str(self.address[1])):
								o[2].send(ProcessSendData(str(self.address[0])+'-'+str(self.address[1])+':'+str(strs_a[2])))
								pass
							pass
						continue
						pass
					if data=='qiut':#有用户退出
						data=str(self.address)+'退出'
						ki=0
						for c in self.thread_list:
							if c[1]==self.address:
								self.thread_list.pop(ki)
								pass
							ki+=1
							pass
						self.con.shutdown(2)
						self.con.close()
						#更新在线用户列表
						members_list={}
						mk=0
						for m in self.thread_list:
							members_list[mk]=str(m[1][0])+':'+str(m[1][1])
							mk+=1
							pass
						print members_list
						re_data={
						'name':str(self.address[0])+'-'+str(self.address[1]),
						'ip':str(self.address[0]),
						'port':str(self.address[1]),
						'data':data,
						'members_list':members_list
						}
						re_str=json.dumps(re_data)
						for ls in self.thread_list:
							ls[2].send(ProcessSendData(re_str))
							pass
						break
						pass
					members_list={}
					mk=0
					for m in self.thread_list:
						members_list[mk]=str(m[1][0])+':'+str(m[1][1])
						mk+=1
						pass
					re_data={
					'name':str(self.address[0])+'-'+str(self.address[1]),
					'ip':str(self.address[0]),
					'port':str(self.address[1]),
					'data':data,
					'members_list':members_list
					}
					re_str=json.dumps(re_data)
					for l in self.thread_list:
						try:
							l[2].send(ProcessSendData(re_str))#将编码转为二进制，当收到消息后循环所有链接资源发送消息
							pass
						except :
							break
					pass
				except :
					break
					pass
			pass
		pass

def main():
	sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	sock.bind(('localhost',888))
	sock.listen(100)
	thread_list=[]
	while True:
		try:
			connection,address = sock.accept()
			t=returnCrossDomain(connection,address,thread_list)
			thread_list.append((t,address,connection))
			t.start()
		except :
			time.sleep(1)
		pass
	pass

if __name__ == '__main__':
	main()