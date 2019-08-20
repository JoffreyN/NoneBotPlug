import os,time,requests
from threading import Timer
from subprocess import Popen,PIPE,getoutput
from configReg import menhuPath,timeout,resultPath,cmdPath
from config import API_ROOT

def executeReg(cmdJson):
	timeArray=time.strftime('%Y%m%d%H%M%S',time.localtime())
	protectPids=checkProcess('py.exe')
	my_timer=Timer(cmdJson['timeout'],shutDown,[protectPids])
	my_timer.start()
	try:
		result=getoutput(f"{menhuPath}/{cmdJson['cmd'].replace('--force','')} --robot")
	finally:
		my_timer.cancel()
		delRegResult()#删除缓存结果
	if not result:result='执行失败，请重试！'
	sendMessage(cmdJson,filterResult(result))#发送结果

def filterResult(result):
	newResult=[]
	for info in result.split('\n'):
		if '正在' in info or '……' in info or '白名单' in info or '未找到' in info:continue
		newResult.append(info)
	return '\n'.join(newResult).strip()

def sendMessage(cmdJson,message):
	head={
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
		'Content-Type':'application/json',
		'Connection':'close'
	}
	if cmdJson['group']:
		key={
			'group_id':cmdJson['group'],
			'message':f"[CQ:at,qq={cmdJson['fromUesr']}]\n{message}"
		}
		r=requests.post(f'{API_ROOT}/send_group_msg',headers=head,json=key)
		if r.status_code==200:
			result=r.json()
			if result['status']!='ok':
				print('发送信息失败：',result)
				with open(f'sendFailed_{time.strftime("%Y%m%d%H%M%S")}.txt','w',encoding='UTF-8') as file:
					file.write(f'{result}\n{message}')
		else:
			print('发送请求错误：',r.text)
	else:
		key={
			'user_id':cmdJson['fromUesr'],
			'message':message,
		}
		r=requests.post(f'{API_ROOT}/send_private_msg',headers=head,json=key)
		if r.status_code==200:
			result=r.json()
			if result['status']!='ok':
				print('发送信息失败：',result)
				with open(f'sendFailed_{time.strftime("%Y%m%d%H%M%S")}.txt','w',encoding='UTF-8') as file:
					file.write(f'{result}\n{message}')
		else:
			print('发送请求错误：',r.text)

# def sendMessage(cmdJson,message):
# 	sender=MyRequests(waitSec=(1,2),resultRetry=lambda s:s.json()['status']!='ok')
# 	if cmdJson['group']:
# 		key={
# 			'group_id':cmdJson['group'],
# 			'message':f"[CQ:at,qq={cmdJson['fromUesr']}]\n{message}"
# 		}
# 		r=sender.post(f'{API_ROOT}/send_group_msg',json=key)
# 		if r.status_code==200:
# 			result=r.json()
# 			if result['status']!='ok':print('发送信息失败：',result)
# 		else:
# 			print('发送请求错误：',r.text)
# 	else:
# 		key={
# 			'user_id':cmdJson['fromUesr'],
# 			'message':message,
# 		}
# 		r=requests.post(f'{API_ROOT}/send_private_msg',headers=head,json=key)
# 		if r.status_code==200:
# 			result=r.json()
# 			if result['status']!='ok':print('发送信息失败：',result)
# 		else:
# 			print('发送请求错误：',r.text)

def shutDown(protectPids):
	# print('TimeoutError!')
	killChrome()
	for pyPid in checkProcess('py.exe'):
		if pyPid not in protectPids:
			try:os.system(f'taskkill /F /PID {pyPid}')
			except Exception as error:print(error)

def killChrome(kd=1,kc=1):
	kc=0
	if kd:
		try:os.system('taskkill /F /IM chromedriver.exe')
		except Exception as error:print(error)
	if kc:
		try:os.system('taskkill /F /IM chrome.exe')
		except Exception as error:print(error)

def checkProcess(processName):
	pipe=Popen(f'tasklist /FI "IMAGENAME eq {processName}"',shell=True,stdout=PIPE).stdout
	strs=pipe.read().decode('gbk')
	pids=[]
	for i in strs.strip().split('\r\n'):
		strList=i.split()
		if strList[0]==processName:
			pids.append(strList[1])
	return pids

def delRegResult():
	try:
		os.remove(resultPath)
	except:
		print('没有 robotRegResult.txt')

if __name__ == '__main__':
	while True:
		if os.path.exists(cmdPath):
			try:
				cmdJson=eval(open(cmdPath,'r',encoding='utf-8').read())
				executeReg(cmdJson)
			finally:
				os.remove(cmdPath)
		time.sleep(1)
	# print(executeReg('regPc.py -a n'))