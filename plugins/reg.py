# from nonebot import on_command, CommandSession


# # on_command 装饰器将函数声明为一个命令处理器
# # 这里 weather 为命令的名字，同时允许使用别名「天气」「天气预报」「查天气」
# @on_command('weather', aliases=('天气', '天气预报', '查天气'))
# async def weather(session: CommandSession):
# 	# 从会话状态（session.state）中获取城市名称（city），如果当前不存在，则询问用户
# 	city=session.get('city', prompt='你想查询哪个城市的天气呢？')
# 	# 获取城市的天气预报
# 	weather_report=await get_weather_of_city(city)
# 	# 向用户发送天气预报
# 	await session.send(weather_report)


# # weather.args_parser 装饰器将函数声明为 weather 命令的参数解析器
# # 命令解析器用于将用户输入的参数解析成命令真正需要的数据
# @weather.args_parser
# async def _(session: CommandSession):
# 	# 去掉消息首尾的空白符
# 	stripped_arg=session.current_arg_text.strip()

# 	if session.is_first_run:
# 		# 该命令第一次运行（第一次进入命令会话）
# 		if stripped_arg:
# 			# 第一次运行参数不为空，意味着用户直接将城市名跟在命令名后面，作为参数传入
# 			# 例如用户可能发送了：天气 南京
# 			session.state['city']=stripped_arg
# 		return

# 	if not stripped_arg:
# 		# 用户没有发送有效的城市名称（而是发送了空白字符），则提示重新输入
# 		# 这里 session.pause() 将会发送消息并暂停当前会话（该行后面的代码不会被运行）
# 		session.pause('要查询的城市名称不能为空呢，请重新输入')

# 	# 如果当前正在向用户询问更多信息（例如本例中的要查询的城市），且用户输入有效，则放入会话状态
# 	session.state[session.current_key]=stripped_arg


# async def get_weather_of_city(city: str) -> str:
# 	# 这里简单返回一个字符串
# 	# 实际应用中，这里应该调用返回真实数据的天气 API，并拼接成天气预报内容
# 	return f'{city}的天气是……'
import subprocess,psutil,re,os,sys,asyncio,time
# from threading import Timer
from nonebot import on_command, CommandSession,on_natural_language, NLPSession, IntentCommand
from nonebot.permission import check_permission,GROUP_ADMIN
sys.path.append('../')
from configReg import *
from executeReg import killChrome,checkProcess

@on_command('reg', aliases=scriptNames)
async def reg(session: CommandSession):
	message=re.sub(r'\[CQ:at,qq=\d+\]','',session.ctx['raw_message']).strip()
	has_perm=await check_permission(session.bot, session.ctx, GROUP_ADMIN)
	fromUesr=session.ctx['user_id']
	flag=0
	for name in scriptNames:
		if name in message:
			if '.py' not in message:message=message.replace(name,f'{name}.py')
			flag=1;break
	if message=='终止':
		if has_perm:
			killChrome()
			time.sleep(1)
			await session.send(getHelpInfo('已终止！',session.ctx))
		else:
			await session.send(getHelpInfo('无权限！',session.ctx))
	elif message=='开户进度':
		result=await checkProgress()
		await session.send(getHelpInfo(f'开户进度：\n{result.strip()}',session.ctx))
	elif '权限' in message:
		if has_perm:
			adds=['增加权限','添加权限','新增权限']
			dels=['删除权限','移除权限','删掉权限']
			for i in adds:
				if i in message:
					result=await addAllowUser(message)
					await session.send(getHelpInfo(result,session.ctx))
			for i in dels:
				if i in message:
					result=await addAllowUser(message,type='del')
					await session.send(getHelpInfo(result,session.ctx))
		else:
			await session.send(getHelpInfo('无权限！',session.ctx))
	elif flag:
		message=' '.join(message.split())
		if fromUesr in allowUserId:
			if len(message.replace('--force','').split())==1:
				message=message.replace('.py','')
				await session.send(getHelpInfo(f'发送 {message} -h 查看用法\n发送 {message} default 使用全默认参数',session.ctx))
			elif '--getRegUrl' in message or '-h' in message:
				result=await executeCmd(message,0,0)
				await session.send(getHelpInfo(result,session.ctx,split='\n'))
			elif '-e p' in message:
				await session.send(getHelpInfo('暂不支持准生产环境~',session.ctx))
			else:
				if checkProcess('chromedriver.exe'):
					await session.send(getHelpInfo('检测到当前已有任务正在执行，请稍后再试！若要强行结束，请联系群主或管理员发送【终止】',session.ctx))
				else:
					if '-e s' in message:timeout=600;_s='\n10分钟内未完成将强制结束，请注意QQ消息并及时响应！'
					elif '-e k' in message or '-t 0' in message:_s='';timeout=600
					else:_s='';timeout=300
					await session.send(getHelpInfo(f'开始执行,最迟{int(timeout/60)}分钟内回复……\n发送【开户进度】可查询进度。{_s}',session.ctx))
					try:group=session.ctx['group_id']
					except KeyError:group=0
					await executeCmd(message,fromUesr,group,timeout)
		else:
			await session.send(getHelpInfo("无权限！",session.ctx))

######################################################################################################################################################################################
# @reg.args_parser
# async def _(session: CommandSession):
# 	stripped_arg=session.current_arg_text.strip()
# 	if session.is_first_run:
# 		if stripped_arg:
# 			session.state['command']=stripped_arg
# 		return
# 	if not stripped_arg:
# 		session.pause('要查询的城市名称不能为空呢，请重新输入')
# 	session.state[session.current_key]=stripped_arg

# on_natural_language 装饰器将函数声明为一个自然语言处理器
# keywords 表示需要响应的关键词，类型为任意可迭代对象，元素类型为 str
# 如果不传入 keywords，则响应所有没有被当作命令处理的消息
@on_natural_language(keywords={'reg','添加权限','删除权限','移除权限','增加权限','新增权限','终止','开户进度'},only_to_me=False)
async def _(session: NLPSession):
	# 返回意图命令，前两个参数必填，分别表示置信度和意图命令名
	return IntentCommand(90.0, 'reg')
######################################################################################################################################################################################
async def executeCmd(cmd,fromUesr,group,timeout=300):
	# if len(cmd.split())==1:
	if '-h' in cmd or '--getRegUrl' in cmd:
		cmd=f'{menhuPath}/{cmd} --path {menhuPath}'
		result=subprocess.getoutput(cmd)
		if not result:result='执行失败，请重试！'
		result=filterResult(result)
		return result
	else:
		if 'default' in cmd:cmd=cmd.replace('default','').strip()
		killChrome()
		with open(cmdPath,'w',encoding='utf-8') as f:
			f.write(str({'cmd':f'{cmd} --path {menhuPath}','fromUesr':fromUesr,'group':group,'timeout':timeout}))
	######################################################################################################################
	# #无法获取报错信息，弃用！
	# pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,cwd='E:/Users/ZP/Desktop/5-2/py/menhu')
	# try:
	# 	result,errs=pipe.communicate(timeout=60)
	# 	# pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,cwd='E:/Users/ZP/Desktop/5-2/py/menhu').stdout
	# 	# result=subprocess.getoutput(cmd)
	# except subprocess.TimeoutExpired:
	# 	# return f'执行失败：{e}'
	# 	os.system('taskkill /IM chromedriver.exe /F')
	# 	# pipe.kill()
	# 	result,errs=pipe.communicate()
	# result=result.decode('gbk')
	######################################################################################################################

async def checkProgress():
	if os.path.exists(resultPath):
		result=open(resultPath,'r',encoding='utf-8').read()
		return result
	else:
		return '未查询到开户进度'

async def addAllowUser(message,type='add'):
	try:
		uesrId=re.search(r'\d+',message).group()
	except AttributeError:
		return '用法：添加/删除权限 QQ号'
	result=editUser(uesrId,type=type)
	return f'{uesrId} {result}'
######################################################################################################################################################################################
def filterResult(result):
	newResult=[]
	for info in result.split('\n'):
		if '正在' in info:continue
		newResult.append(info)
	return '\n'.join(newResult).strip()

def getHelpInfo(info,sessionCtx,split=' '):
	if sessionCtx['message_type']=='group':
		info=f"[CQ:at,qq={sessionCtx['user_id']}]{split}{info}"
	return info

def editUser(uesrId,type='add'):
	global allowUserId
	configRegPath=os.path.join(os.path.split(os.path.dirname(__file__))[0],'configReg.py')
	configReg=open(configRegPath,'r',encoding='utf-8').readlines()
	exec(configReg[0])
	if type=='add':
		allowUserId.append(int(uesrId))
		result='权限添加成功！'
	elif type=='del':
		try:
			allowUserId.remove(int(uesrId))
			result='权限删除成功！'
		except ValueError:
			result='本无权限，无需删除'
	configReg[0]=f'allowUserId={allowUserId}\n'
	with open(configRegPath,'w',encoding='utf-8') as f:
		f.writelines(configReg)
	return result
