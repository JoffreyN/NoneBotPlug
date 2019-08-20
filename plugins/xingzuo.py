import re,requests,time
from bs4 import BeautifulSoup
from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
aliases=('白羊','金牛','双子','巨蟹','狮子','处女','天秤','天蝎','射手','摩羯','水瓶','双鱼')
xingzuoDic={'白羊':'aries','金牛':'taurus','双子':'gemini','巨蟹':'cancer','狮子':'leo','处女':'virgo','天秤':'libra','天蝎':'scorpio','射手':'sagittarius','摩羯':'capricorn','水瓶':'aquarius','双鱼':'pisces'}

@on_command('xingzuo', aliases=aliases)
async def xingzuo(session: CommandSession):
	message=re.sub(r'\[CQ:at,qq=\d+\]','',session.ctx['raw_message']).strip()
	for constellation in aliases:
		if constellation in message:break
		else:constellation=False
	if constellation:
		result=await getFortune(constellation)
		await session.send(getHelpInfo(result,session.ctx))

######################################################################################################################################################################################
@on_natural_language(keywords=aliases,only_to_me=False)
async def _(session: NLPSession):
	return IntentCommand(90.0, 'xingzuo')
######################################################################################################################################################################################

async def getFortune(constellation):
	result=f"{constellation}座{time.strftime('%Y{y}%m{m}%d{d}').format(y='年',m='月',d='日')}运势：\n"
	for i in range(5):
		html=getHtml(xingzuoDic[constellation])
		if html:
			soup=BeautifulSoup(html,'lxml')
			result=f'{result}{getOverview(soup)}{getDetail(soup)}'
			return result.strip()
		time.sleep(5)
	return '查询失败，网络错误！'

def getHtml(name):
	head={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
	r=requests.get(f'http://www.xzw.com/fortune/{name}',headers=head)
	if r.status_code==200:
		r.encoding='utf-8'
		return r.text
	else:
		print('连接失败！')
		return False
	
def getOverview(soup):
	overview='【运势概览】\n';n=1
	for li in soup.select_one('.c_main').select_one('ul').select('li'):
		if n in [1,3,9]:end='\t'
		elif n in [5,7]:end='\t\t'
		else:end='\n'
		em=li.select_one('em')
		if em:
			label=li.select_one('label').text
			star=getStar(re.search(r'\d+',em['style']).group())
			overview=f"{overview}\t{label}{star}{end}"
		else:
			if n==7:
				lenth=len(li.text.split('：')[1])
				if lenth==2:end='\t\t'
				elif lenth==3:end='\t'
				elif lenth==4:end=''
			overview=f"{overview}\t{li.text}{end}"
		n+=1
	return overview.replace('短评','每日短评')

def getDetail(soup):
	detail='【运势详解】\n'
	for i in range(1,6):
		detail=f"{detail}\t{soup.select_one(f'.p{i}').text}：{soup.select_one(f'.p{i}').next_sibling.text}\n"
	return detail

def getStar(num):
	num=int(int(num)/16)
	return f'{"★"*num}{"☆"*(5-num)}'[:5]
######################################################################################################################################################################################
def getHelpInfo(info,sessionCtx,split=' '):
	if sessionCtx['message_type']=='group':
		info=f"[CQ:at,qq={sessionCtx['user_id']}]{split}{info}"
	return info