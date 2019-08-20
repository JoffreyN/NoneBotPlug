import re,shelve,time,linecache
from random import randint,choice,shuffle
from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
aliases=('抽签','解签')

@on_command('chouqian', aliases=aliases)
async def chouqian(session: CommandSession):
	# print('debug10415',session.ctx)
	message=re.sub(r'\[CQ:at,qq=\d+\]','',session.ctx['raw_message']).strip()
	qq=session.ctx['user_id']
	if '抽签'==message:
		result=await ChouQian(qq)
		await session.send(getHelpInfo(result,session.ctx))
	elif '解签'==message:
		result=await JieQian(qq)
		await session.send(getHelpInfo(result,session.ctx))

######################################################################################################################################################################################
@on_natural_language(keywords=aliases,only_to_me=False)
async def _(session: NLPSession):
	return IntentCommand(90.0, 'chouqian')
######################################################################################################################################################################################
async def ChouQian(qq):
	qianData=Myshelve(qq)
	qianData.delOldData()
	try:
		qian=qianData.read()
		return f"你今天已经抽过签啦~\n签位: {qian['签位']}\n{qian['签文']}\n解签请发送【解签】"
	except KeyError:
		qianPoolPath='chouqianData/qianPool.txt'
		# countQianPool=len(open(qianPoolPath,'rU',encoding='utf-8').readlines())
		# qian=eval(linecache.getline(qianPoolPath,randint(1,countQianPool)))
		qianPool=open(qianPoolPath,'rU',encoding='utf-8').readlines()
		shuffle(qianPool)#乱序排序
		qian=eval(re.findall(r'\{.+\}',choice(qianPool))[0])#随机选一个
		qianData.save(qian)
	return f"\n签位: {qian['签位']}\n{qian['签文']}\n解签请发送【解签】"

async def JieQian(qq):
	qianData=Myshelve(qq)
	try:
		qian=qianData.read()
		return f"\n解签: {qian['签位']}\n{qian['解签']}"
	except KeyError:
		return '你今天还没有抽过签哦~'

class Myshelve(object):
	def __init__(self,qq,savePath='chouqianData'):
		self.qq=qq
		self.savePath=f'{savePath}/chouqian'
		self.date=time.strftime('%Y%m%d')
	
	def save(self,qian):
		with shelve.open(self.savePath) as db:
			try:
				data=db[self.date]
			except KeyError:
				data={}
			data[self.qq]=qian
			db[self.date]=data
	
	def read(self):
		with shelve.open(self.savePath) as db:
			qian=db[self.date][self.qq]
		return qian
	
	def delOldData(self):
		with shelve.open(self.savePath) as db:
			for key in db.keys():
				if time.mktime(time.strptime(self.date,'%Y%m%d'))-time.mktime(time.strptime(key,'%Y%m%d'))>=259200:#删除三天前的数据
					del db[key]
######################################################################################################################################################################################
def getHelpInfo(info,sessionCtx,split=' '):
	if sessionCtx['message_type']=='group':
		info=f"[CQ:at,qq={sessionCtx['user_id']}]{split}{info}"
	return info.strip()

# def test():
# 	os.remove('chouqian.bak')
# 	os.remove('chouqian.dat')
# 	os.remove('chouqian.dir')
# 	data=shelve.open('chouqian')
# 	data['20190610']={2806646694:{'签位':'观音灵签 第一签 上签 钟离成道','签文':'开天辟地作良缘，吉日良时万物全；若得此签非小可，人行忠正帝王宣。','解签':'受拥而发。'},1041531855:{'签位':'观音灵签 第一签 上签 钟离成道','签文':'开天辟地作良缘，吉日良时万物全；若得此签非小可，人行忠正帝王宣。','解签':'受拥而发。'},}
# 	data['20190611']={2806646694:{'签位':'观音灵签 第一签 上签 钟离成道','签文':'开天辟地作良缘，吉日良时万物全；若得此签非小可，人行忠正帝王宣。','解签':'受拥而发。'},1041531855:{'签位':'观音灵签 第一签 上签 钟离成道','签文':'开天辟地作良缘，吉日良时万物全；若得此签非小可，人行忠正帝王宣。','解签':'受拥而发。'},}
# 	data['20190612']={468415313:{'签位':'观音灵签 第一签 上签 钟离成道','签文':'开天辟地作良缘，吉日良时万物全；若得此签非小可，人行忠正帝王宣。','解签':'受拥而发。'},1324165413:{'签位':'观音灵签 第一签 上签 钟离成道','签文':'开天辟地作良缘，吉日良时万物全；若得此签非小可，人行忠正帝王宣。','解签':'受拥而发。'},}
# 	data.close()

def test():
	import os,shelve
	os.chdir(r'E:\Users\ZP\Desktop\5-2\py\myNonebot')
	db=shelve.open('chouqianData/chouqian')
	del db['20190613']
	db.close()