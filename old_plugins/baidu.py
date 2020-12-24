from nonebot import on_command, CommandSession
import urllib.parse
#pattern = re.compile(r"百度.*")
@on_command('baidu', aliases=('百度', '百度搜索', '搜索'), only_to_me=False)
async def baidu(session: CommandSession):
    search_info = session.state['search_info']
    if (search_info == None) or (search_info == ''):
        await session.send("(缓缓打出一个问号--？)")
        return 
    search_quote = urllib.parse.quote(search_info)
    await session.send(f'https://m.baidu.com/s?&tn=baidu&wd={search_quote}&pn=0')
    #await session.send(f"[CQ:xml,data=<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><msg serviceID=\"1\"><item><title>RBQ自动搜索响应</title></item><source name=\"BaiDu\" icon=\"https://s1.ax1x.com/2020/06/24/Nw9EnS.jpg\" action=\"\" appid=\"-1\" /></msg>]")
    #await session.send(f'[CQ:xml,data=https://m.baidu.com/s?&tn=baidu&wd={search_quote}&pn=0,\
    #title=百度搜索:{search_info},content=RBQ自动搜索响应,image=https://s1.ax1x.com/2020/06/24/Nw9EnS.jpg]')
@baidu.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    session.state['search_info'] = stripped_arg