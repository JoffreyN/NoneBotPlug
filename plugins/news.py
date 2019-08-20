import requests,re
from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
aliases=[
	'今日头条','分类新闻','汉服新闻','房产新闻','科学探索','汽车新闻','互联网资讯','动漫资讯',
	'财经新闻','游戏资讯','CBA新闻','人工智能','区块链新闻','IT资讯','VR科技','美女图片',
	'奇闻异事','健康知识','旅游资讯','移动互联','军事新闻','苹果新闻','创业新闻','科技新闻',
	'足球新闻','NBA新闻','体育新闻','娱乐新闻','国际新闻','国内新闻','社会新闻','热搜榜'
]
# 接口列表 https://www.tianapi.com/openapilist.html
newsType={
	'社会新闻':5,'国内新闻':7,'国际新闻':8,'娱乐新闻':10,'美女图片':11,'体育新闻':12,
	'科技新闻':13,'奇闻异事':14,'健康知识':17,'旅游资讯':18,'苹果新闻':19,'NBA新闻':20,
	'VR科技':21,'IT资讯':22,'移动互联':23,'创业新闻':24,'足球新闻':26,'军事新闻':27,
	'区块链新闻':28,'人工智能':29,'CBA新闻':30,'游戏资讯':31,'财经新闻':32,'动漫资讯':33,
	'互联网资讯':34,'汽车新闻':35,'科学探索':36,'房产新闻':37,'汉服新闻':38,
}

@on_command('news', aliases=aliases)
async def news(session: CommandSession):
	message=re.sub(r'\[CQ:at,qq=\d+\]','',session.ctx['raw_message']).strip()
	# print('debug10415:',session.ctx)
	req=0
	if message in aliases:
		req=1;col=0
		if message=='今日头条':#综合新闻
			api='http://api.tianapi.com/topnews/'
		elif message=='热搜榜':
			api='http://api.tianapi.com/txapi/nethot/'
		elif message=='分类新闻':
			req=0;result='、'.join(newsType.keys())
			result=f'你想查看什么类别的新闻: \n{result}'
		else:#分类新闻
			col=newsType[message]
			api='http://api.tianapi.com/allnews/'
	if req:result=await getNews(api,col,message)
	await session.send(getHelpInfo(result,session.ctx))

######################################################################################################################################################################################
@on_natural_language(keywords=aliases,only_to_me=False)
async def _(session: NLPSession):
	return IntentCommand(90.0, 'news')
######################################################################################################################################################################################
async def getNews(api,col,message):
	key={
		'key':'b6b3315fa8baaa74cfaea46db473a417',
		'num':'10',
	}
	if col:key['col']=col
	rep=requests.get(api,params=key)
	if rep.status_code==200:
		try:
			resultJson=rep.json()
		except json.decoder.JSONDecodeError:
			return f'API接口返回异常: {api}\n{rep.text}'
	else:
		return f'API连接失败: {api}\n{rep.text}'
	n=0;result=''
	if 'topnews' in api:#头条新闻
		for news in resultJson['newslist']:
			n+=1
			# result=f'{result}{n}、【{news["title"]}】: {news["description"]}\n'
			result=f'{result}{n}、【{news["title"]}】: {news["description"]} 详情点击[CQ:emoji,id=128073] {news["url"]}\n'
		result=f'今日头条新闻: \n{result.strip()}'
	elif 'nethot' in api:#实时热搜
		for news in resultJson['newslist']:
			n+=1
			result=f'{result}{n}、{news["keyword"]}\n'
		result=f'实时热搜榜: \n{result.strip()}'
	elif 'allnews' in api:#分类新闻
		for news in resultJson['newslist']:
			n+=1
			# result=f'{result}{n}、【{news["title"]}】\n'
			result=f'{result}{n}、【{news["title"]}】\n    详情点击[CQ:emoji,id=128073] {news["url"]}\n'
		result=f'今日{message}: \n{result.strip()}'
	return result
######################################################################################################################################################################################
def getHelpInfo(info,sessionCtx,split=' '):
	if sessionCtx['message_type']=='group':
		info=f"[CQ:at,qq={sessionCtx['user_id']}]{split}{info}"
	return info