import re,requests,jieba,time
from nonebot import on_command, CommandSession,on_natural_language, NLPSession, IntentCommand
from random import choice,randint

today=time.strftime('%Y%m%d')
myDictPath='memoryData/myDicts.txt'
memoryPath='memoryData/memory'
ragePoolPath='memoryData/ragePools'
jieba.load_userdict(myDictPath)
myDicts=list(map(lambda s:s.strip('\n'),open(myDictPath,'r',encoding='UTF-8').readlines()))
ragePools=eval(open(ragePoolPath,'r',encoding='UTF-8').read())
try:
	ragePool=ragePools[today]
except KeyError:
	ragePool=[0]*10
memory=eval(open(memoryPath,'r',encoding='UTF-8').read())

@on_command('chat')
async def chat(session: CommandSession):
	global memory
	message=re.sub(r'\[CQ:at,qq=\d+\]','',session.ctx['raw_message'],1).strip()
	nickname=session.ctx['sender']['nickname']
	fromUser=str(session.ctx['user_id'])
	message=message.replace('我',nickname)
	message=message.replace('你','我')
	#####################################################################################################
	remember=0;query=0;ask=0
	for n in ['记住','记下']:
		if n in message:
			message=message.replace(n,'').strip()
			remember=1;break
	#####################################################################################################
	if not remember and '是' in message and '是在' not in message:
		for i in myDicts:
			if i in message:
				key=i;query=1;break
		if not query:
			for i in jieba.cut(message):
				if i in ['的','地','得']:continue
				for j in memory:
					if i in j or j in i:
						key=j;rep=i;query=1;break
	#####################################################################################################
	if not query:
		for i in askList:
			if i in message:
				ask=1;break
	#####################################################################################################
	if message in ['?','？']:
		helpMesg='''
群主/管理员命令：
	添加权限 ：添加群员开户权限
	删除权限 ：删除群员开户权限
	终止 ：强制结束正在运行的开户进程
	关机 ：关机
普通命令：
	regPc ：PC端开户
	regH5 ：H5端开户
	regH5YTH ：H5一体化开户
	开户进度 ：查询开户进度
	查短信/46短信/查失败短信/46失败短信 ：查询消息中心短信发送记录，可指定手机号
	重置密码 ：重置门户账户密码
	重置支付密码 ：重置门户账户支付密码
	大总管审核 ：大总管审核申请
	更新cookie : 更新生产环境大总管、资金后台cookie
其它命令：
	出题 ：开始答题
	今日头条 ：查看今日热点头条新闻
	分类新闻 ：查看新闻分类，可直接按分类查看新闻
	热搜榜 ：查看实时热搜榜
'''
# 配对、抽签、求签、点歌、星座
		await session.send(getHelpInfo(f'常用命令介绍：\n{helpMesg.strip()}',session.ctx))
	elif remember:
		if message:
			if '是' in message:
				memList=re.split('是',message)
				memory[memList[0]]=memList[1]
				if '我' in message or fromUser in message:memory[memList[1]]=memList[0]
				addMyDicts(memList);saveMemory()
				await session.send(getHelpInfo(f'{choice(yes)}{choice(biaodian)}{n}了{choice(juhao)}',session.ctx))
				ragePool.append(0)
				saveRagePool()
			else:
				await session.send(getHelpInfo(f'{choice(kaitou)}...我{choice(notSure)}{choice(little)}{choice(doNot)}{choice(know)}{choice(jiewei)}{choice(biaodian)}换个简单的说法吧~',session.ctx))
		else:
			await session.send(getHelpInfo('你想让我帮你记住什么呢？',session.ctx))
	elif query:
		try:
			result=f'{rep}是{memory[key]}'
		except KeyError:
			keyList=getKey(key)
			result=f"{'、'.join(keyList)}是{key}"
		except UnboundLocalError:
			result=f'{key}是{memory[key]}'
		# result=aiteORnick(result,session.ctx)
		await session.send(getHelpInfo(result,session.ctx))
		ragePool.append(0)
		saveRagePool()
	else:
		if '点歌' in message:pass
		elif message.lower() not in ['开始答题','出题','关闭答题']:
			if ask:
				ragePool.append(1)
				saveRagePool()
			rage=choice(ragePool)
			result=' '
			if rage:
				evil=choice([0,0,1,0,0])
				if evil and ask:
					result=await getShortUrl(message)
				else:
					result=choice(['雨藕无瓜','一边玩儿去','不想理你','不知道','烦死了','闭嘴','多喝烫水','再问报警','吵死了','别来烦我'])
			else:
				yin=choice([0,0,0,0,0,1,0,0,0,0])
				if yin:
					result='嘤'*randint(1,4)
				else:
					ragePool.append(1)
					saveRagePool()
					result=await tuling(message)
			await session.send(getHelpInfo(result,session.ctx))
	delOldRagePool()
######################################################################################################################################################################################
@on_natural_language(keywords=None,only_to_me=1)
async def _(session: NLPSession):
	return IntentCommand(80.0, 'chat')
######################################################################################################################################################################################
async def tuling(message):
	key={
		"reqType":0,
		"perception":{"inputText": {"text":message}},
		"userInfo":{"apiKey":"b5e4028eca0e4df0824cfb3c31949607","userId":"448968"}
	}
	rep=requests.post('http://openapi.tuling123.com/openapi/api/v2',json=key)
	repJson=rep.json()
	if repJson['intent']['code']>8008:
		return repJson['results'][0]['values']['text']
	else:
		print(repJson)

async def getShortUrl(keywords):
	from urllib import parse
	urlList=['https://cnm.buhuibaidu.me/?s=','http://baidu.apphb.com/?q=','http://iwo.im/?q=','http://lab.mkblog.cn/lmbtfy/?','http://tool.ouzero.com/tools/baidu/?','https://92acg.cn/?','http://if2.cc/baidu/?']
	longUrl=f'{choice(urlList)}{parse.quote(keywords)}'
	head={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36','Connection':'close'}
	key={'url':longUrl,'key':'5d2849748e676d0671ca3782@b7b56a44bbc7b73c0ad5359c037f8bb8','expireDate':time.strftime('%Y-%m-%d',time.localtime(time.time()+(1*24*60*60)))}
	rep=requests.get(f'http://suo.im/api.htm',params=key,headers=head)
	if rep.status_code==200:
		return rep.text
	else:
		return '百度一下,你就知道'
######################################################################################################################################################################################
def getHelpInfo(info,sessionCtx,split=' '):
	time.sleep(randint(1,3))
	if sessionCtx['message_type']=='group':
		info=f"[CQ:at,qq={sessionCtx['user_id']}]{split}{info}"
	return info

def saveMemory():
	global memory
	with open(memoryPath,'w',encoding='UTF-8') as file:
		file.write(str(memory))

def addMyDicts(keyList):
	global myDicts
	myDicts.extend(keyList)
	with open(myDictPath,'a',encoding='UTF-8') as f:
		for key in keyList:
			f.write(f'{key}\n')

def getKey(kword):
	global memory
	keyList=[]
	for i,j in memory.items():
		if kword in j or j in kword:
			keyList.append(i)
	return keyList

def saveRagePool():
	global ragePool,ragePools,today
	ragePools[today]=ragePool
	with open(ragePoolPath,'w',encoding='UTF-8') as file:
		file.write(str(ragePools))

def delOldRagePool():
	global ragePools,today
	dels=[]
	for key in ragePools:
		if time.mktime(time.strptime(today,'%Y%m%d'))-time.mktime(time.strptime(key,'%Y%m%d'))>=259200:#删除三天前的数据
			dels.append(key)
	for key in dels:
		del ragePools[key]
	saveRagePool()

# def aiteORnick(info,sessionCtx):
# 	if sessionCtx['user_id'] in info:
# 		if sessionCtx['message_type']=='group':
# 			info=
kaitou=['额','呃','嗯','emmmm','唔']
askList=['什么','啥','多少','？','?','如何','怎样','谁','怎么办']
juhao=['~','！','!','。',' ']
biaodian=['，',',','~','！','!',' ','...','…']
yes=['嗯嗯','好的','行','没问题','OK']
notSure=['似乎','好像']
little=['','有点','有点点','有一点','有一点点','有点儿','有点点儿','有一点儿','有一点点儿']
doNot=['不太','不大','不']
know=['理解','明白']
jiewei=['呢','额','呃','']
