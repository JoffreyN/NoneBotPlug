import requests,re
from bs4 import BeautifulSoup
from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
aliases=['番号','车牌','电影','美剧','电视剧','查找','资源']

@on_command('Car', aliases=aliases)
async def Car(session: CommandSession):
	message=re.sub(r'\[CQ:at,qq=\d+\]','',session.ctx['raw_message']).strip()
	# print('debug10415:',session.ctx)
	groupID=''
	if session.ctx['message_type']=='group':groupID=session.ctx['group_id']
	userID=session.ctx['user_id']
	for key in aliases:
		if key in message:
			message=message.replace(key,'')
			break
	if message:
		if groupID in [744674753]:
			# await session.send(getHelpInfo("这是正规群，不能开车！",session.ctx))
			pass
		else:
			if userID in [2806646694,305927790,760844602,273211016,1041531855]:
				result=await getRepText(message)
				await session.send(getHelpInfo(f"为你找到如下资源：\n{result}",session.ctx))
			else:
				# await session.send(getHelpInfo("非VIP用户！",session.ctx))
				pass
	else:
		await session.send(getHelpInfo(f'格式：{key} 关键词',session.ctx))

######################################################################################################################################################################################
@on_natural_language(keywords=aliases,only_to_me=False)
async def _(session: NLPSession):
	return IntentCommand(90.0, 'Car')
######################################################################################################################################################################################
async def getRepText(keyWord):
	soup=await getHtml(keyWord)
	if soup:
		n=1;repText=''
		for table in soup.select('table'):
			repText+=f"{n}、{table.select('tr')[0].select_one('a').text.replace(' ','')}\n\t{table.select('tr')[1].select('td')[0].text}\t{table.select('tr')[1].select('td')[1].text}\t{table.select('tr')[1].select('td')[2].text}\n\t磁力链接：{table.select('tr')[1].select('td')[3].select_one('a')['href']}\n"
			n+=1
		return repText.strip()
	else:
		return '网络连接错误！'

async def getHtml(keyWord):
	head={
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36',
		'Connection': 'close',
	}
	rep=requests.get(f'https://www.zhongzilou.com/list/{keyWord}/1')
	if rep.status_code==200:
		rep.encoding='utf-8'
		soup=BeautifulSoup(rep.text,'lxml')
		return soup
	else:
		print('连接失败！')
		return False
######################################################################################################################################################################################
def getHelpInfo(info,sessionCtx,split=' '):
	if sessionCtx['message_type']=='group':
		info=f"[CQ:at,qq={sessionCtx['user_id']}]{split}{info}"
	return info    