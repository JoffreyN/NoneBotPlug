import subprocess,re,time,sys,os,requests
from nonebot import on_command, CommandSession,on_natural_language, NLPSession, IntentCommand
from nonebot.permission import check_permission,GROUP_ADMIN
from configReg import menhuPath
from random import choice
sys.path.append(menhuPath)
alias1=['查短信','46短信','查失败短信','46失败短信']
alias2=['发版']
alias3=['关机']
alias4=['重置密码','重置支付密码']
alias5=['大总管审核']
alias6=['初始密码','已完成预授信','验证码','已完成人脸识别']
alias7=['更新cookie','更新Cookie','更新COOKIE']
aliases=alias1+alias2+alias3+alias4+alias5+alias6+alias7

@on_command('messageCenter',aliases=aliases)
async def messageCenter(session: CommandSession):
	message=re.sub(r'\[CQ:at,qq=\d+\]','',session.ctx['raw_message']).strip()
	# has_perm=await check_permission(session.bot,session.ctx,GROUP_ADMIN)
	has_perm=1 if session.ctx['user_id'] in [2806646694,1041531855] else 0
	loginID=0;tel='';t=0;op=0;types=0
	########################################################################################################
	for i in alias1:
		if i in message:
			tel=message.replace(i,'').strip()
			env='k' if '46' in i else 'c'
			status='FAILURE' if '失败' in i else 'SUCCESS'
			types=1;break
			
			# try:
			# 	tel=re.search(r'\d+',message).group()
			# except AttributeError:
			# 	pass
			# message=message.replace(tel,'').strip()
	########################################################################################################
	if not types:
		if '发版' in message:
			for i in ['?','吗','？','么','是不是','有没有']:
				if i in message:
					types=2;break
	########################################################################################################
	if not types:
		for i in alias4:
			t+=1
			if i in message:
				types=4
				loginID=message.replace(i,'').strip()
				break
	########################################################################################################
	if not types:
		for i in alias5:
			if i in message:
				types=5;op=''
				loginID=message.replace(i,'').strip()
				if loginID:
					# if 'h5' in loginID.lower():op=3
					# else:op=''
					if 'PC开户审核' in loginID:op=1;loginID=loginID.replace('PC开户审核','').strip()
					elif '资质更新审核' in loginID:op=2;loginID=loginID.replace('资质更新审核','').strip()
					elif 'H5审核' in loginID:op=3;loginID=loginID.replace('H5审核','').strip()
				break
	########################################################################################################
	if not types:
		code=0
		for i in alias6:
			if i in message:
				types=6
				try:
					code=re.search(r'\d+',message).group()
				except AttributeError:
					code=''
				message=message.replace(code,'').strip()
				break
	########################################################################################################
	if not types:
		if '更新' in message and 'cookie' in message:
			types=7;message=re.sub('更新|cookie','',message)
	########################################################################################################
	if types==1:
		_envDic={'k':'46环境','c':'综测环境'}
		result=await getSMS(tel,env,status)
		if result:
			if '1、' in result:
				if tel:
					await session.send(getHelpInfo(f'{_envDic[env]}查到 {tel} 如下最新几条短信：\n{result}',session.ctx))
				else:
					await session.send(getHelpInfo(f'{_envDic[env]}为你查到如下最新几条短信：\n{result}',session.ctx))
			else:
				await session.send(getHelpInfo(result,session.ctx))
		else:
			await session.send(getHelpInfo(f'{_envDic[env]}未查询到 {tel} 相关短信记录！',session.ctx))
	elif types==2:
		await session.send(getHelpInfo('正在查询，请稍候……',session.ctx))
		result=await checkbuild(message)
		await session.send(getHelpInfo(result,session.ctx))
	elif message in alias3:
		if has_perm:
			await session.send(getHelpInfo('好的，再见~',session.ctx))
			os.system('shutdown -h')#休眠
			# os.system('shutdown -s')#关机
		else:
			await session.send(getHelpInfo(choice(['无权限，请充值！','余额不足，请充值后重试！','你号没了']),session.ctx))
	elif types==4:
		if loginID:
			startTime=int(time.time())
			time.sleep(1)
			resultJson=await resetPwd(loginID,t)
			await session.send(getHelpInfo(resultJson['result'],session.ctx))
			if resultJson['tel']:
				result=await getNewPwd(loginID,resultJson['tel'],startTime)
				await session.send(getHelpInfo(result,session.ctx))
		else:
			await session.send(getHelpInfo(f'用法：{message} 【登录号】',session.ctx))
	elif types==5:
		if loginID:
			await session.send(getHelpInfo('好的，请稍等~',session.ctx))
			# print('debug:',loginID,op)
			result=await bbCheck(loginID,op)
			await session.send(getHelpInfo(result,session.ctx))
		else:
			await session.send(getHelpInfo(f'用法：{message} 【登录号】',session.ctx))
			 # 【审核类型(可不写)】\n说明：1、如果登录号中包含"h5",则审核类型默认为"H5审核"，否则取查询到的第一条结果\n\t  2、审核类型：PC开户审核、资质更新审核、H5审核
	elif types==6:
		if message in alias6:
			if code or message in ['已完成预授信','已完成人脸识别']:
				with open(message,'w',encoding='UTF-8') as file:file.write(code)
				await session.send(getHelpInfo('收到~',session.ctx))
			else:
				await session.send(getHelpInfo(f'格式：{message} xxx',session.ctx))
	elif types==7:
		cookie=0;platFrom=0
		if '大总管' in message:
			platFrom='BB_s'
			cookie=message.replace('大总管','').strip()
		elif '资金后台' in message:
			platFrom='MM_s'
			cookie=message.replace('资金后台','').strip()
		else:
			await session.send(getHelpInfo('目前仅支持 生产大总管 和 生产资金后台',session.ctx))
		if cookie and platFrom:
			with open(os.path.join(menhuPath,f'cookie/{platFrom}'),'w',encoding='UTF-8') as file:file.write(cookie)
			with open('已更新','w',encoding='UTF-8') as file:file.write('1')
			await session.send(getHelpInfo('已更新~',session.ctx))
		else:
			await session.send(getHelpInfo(f'用法：更新cookie 【大总管/资金后台】 【cookie】\n例如：更新cookie 资金后台 JSESSIONID=fd92af3e-7442-4205-8186-e2d7bee8106f',session.ctx))
######################################################################################################################################################################################
@on_natural_language(keywords=aliases,only_to_me=False)
async def _(session: NLPSession):
	return IntentCommand(90.0, 'messageCenter')
######################################################################################################################################################################################
async def bbCheck(loginID,op):
	from checkBboss import bbossCheck
	resultJson=bbossCheck(loginID=loginID,env='c',op=str(op),path=menhuPath,robot=1)
	try:
		if resultJson['auditSta']=='审核通过':
			result=f"{resultJson['bizName']} {resultJson['operatorUserCode']} {resultJson['auditSta']}"
		else:
			result=f"{resultJson['auditSta']} {resultJson['respCode']} {resultJson['respMsg']}"
	except KeyError:
		result=resultJson['result']
	return result

async def getSMS(tel,env,status):
	from MClogin import getSMScode
	result=getSMScode(tel,waiteSec=0,robot=1,menhuPath=menhuPath,env=env,status=status)
	return result

async def checkbuild(message):
	from isBuilding import checkBuild
	result=checkBuild()
	if result:
		if '异常' not in result:
			result=f'是的，在发版：{result}'
	else:
		result='未检测到在发版'
	return result

async def getNewPwd(loginID,tel,startTime):#获取初始密码
	cookiePath=os.path.join(menhuPath,'cookie/OM_c')
	cookie=open(cookiePath,'r',encoding='UTF-8').read()
	head={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36','Cookie':cookie,'Connection':'close'}
	n=10
	while n:
		rep=requests.get(f'http://116.228.151.161:18191/admin/smsManager/queryRecordForPage?mobile={tel}',headers=head)
		try:
			repJson=rep.json()
		except json.decoder.JSONDecodeError:
			if '登录' in r.text:
				return 'cookieOM失效，请5分钟后重试'
			else:
				return f'系统异常：{rep.text}'
		if repJson['errorMsg']=='成功':
			try:
				for dicts in repJson['data']:
					if loginID in dicts['content']:
						if time.mktime(time.strptime(dicts['sendDate'], '%Y-%m-%d %X'))-startTime>=0:
							return 	dicts['content']
			except IndexError:
				n-=1
				continue
		else:
			print(repJson)
			n-=1
			continue

async def resetPwd(loginID,t=1):
	_d={1:'登录',2:'支付'}
	omCookiePath=os.path.join(menhuPath,'cookie/OM_c')
	cookie=open(omCookiePath,'r',encoding='utf-8').read()
	head={
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
		'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
		'Cookie':cookie,
		'Connection':'close',
	}
	tel=await getTel(loginID,head)
	if tel.isdigit():
		key={
			'userCode':loginID,
			'mobile':tel,
			'passwordType':f'PT0{t}',
			'stamp':'',
		}
		for i in range(10):
			rep=requests.post('http://116.228.151.161:18191/admin/user/resetPwd',headers=head,data=key)
			try:
				repJson=rep.json()
			except json.decoder.JSONDecodeError:
				if '登录' in rep.text:
					return {'result':'cookieMC失效，请5分钟后重试','tel':0}
				else:
					return {'result':f'系统异常：{rep.text}','tel':0}
			if repJson['success']:
				return {'result':f'{loginID} 重置{_d[t]}密码成功','tel':tel}
		return {'result':f'{loginID} 重置{_d[t]}密码失败: {repJson}','tel':0}
	else:
		return {'result':tel,'tel':0}

# {"result":1,"errorCode":"OSS08000000","errorMsg":"成功","success":true,"auditBiz":false}

async def getTel(loginID,head):
	rep=requests.get(f'http://116.228.151.161:18191/admin/user/queryUser?entLoginName={loginID}',headers=head)
	try:
		repJson=rep.json()
	except json.decoder.JSONDecodeError:
		if '登录' in rep.text:
			return 'cookieMC失效，请5分钟后重试'
		else:
			return f'系统异常：{rep.text}'
	return repJson['data'][0]['mobile']
######################################################################################################################################################################################
def getHelpInfo(info,sessionCtx,split=' '):
	if sessionCtx['message_type']=='group':
		info=f"[CQ:at,qq={sessionCtx['user_id']}]{split}{info}"
	return info