from nonebot import on_command, CommandSession

@on_command('webguide', aliases=('网址', '网站', '网址导航'),  only_to_me=False) #qq机器人用

async def webguide(session: CommandSession): #qq机器人用命令体
    await session.send("""
==网站导航==
动画搜图:https://trace.moe/
Pixiv搜图:https://saucenao.com/
中文搜资源导航页:https://qssily.com/    
Bt里站:https://nyaa.si/
番资源:http://acgheaven.org/
人人电影网:http://www.rrdyw.cc/
幻之字幕组:https://www.mabors.com/
搜图导航:https://m.cnbeta.com/view/188146.htm
日系里站:https://sukebei.nyaa.si/
有发现的网站可以找miku补充
""")

@webguide.args_parser #qq机器人用命令解析器
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()