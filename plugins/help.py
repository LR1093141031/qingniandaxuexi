from nonebot import on_command, CommandSession

@on_command('help', aliases=('帮助', '帮助菜单', '功能', '你会什么'\
            '怎么玩', '有什么功能', '菜单'),  only_to_me=False)

async def help(session: CommandSession):

    await session.send('''RBQ帮助菜单：)
以下所有功能需要加RBQ为好友
1.p站查图 
p站图片 / p站 /p ＋ 图片ID   
例：“p 83658499”
2.色图一份
来份涩图/ 来份色图 /来亿份色图   
例：“来份涩图”
3.p站榜单 （群聊常规，私聊为r18）
p站榜单 / 今日榜单 / 榜单 ＋ 榜单起始位置   
例：“榜单 20”
4.青年大学习完成图
大学习 / 青年大学习
5.百度url（暂无法使用）
百度 / 百度搜索 +搜索内容
例：“百度 miku酱”
6.SauceNao Ascii2d混合搜图（截图或图片要裁掉黑边框）
搜图/识图
7. WhatAnime搜番（截图或图片要裁掉黑边框）
搜番/识番
8.骰娘
r 骰子数d面数
例：r 2d6''')


@help.args_parser  # qq机器人用命令解析器
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()
