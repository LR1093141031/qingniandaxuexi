import random
from nonebot import on_command, CommandSession
import re


@on_command('r', aliases=['随机', '骰子'], only_to_me=False)  # qq机器人用
async def r(session: CommandSession):  # qq机器人用命令体
    factor = session.state['factor']
    num = re.findall(r'(\d{1,2})d', factor)[0]
    faces = re.findall(r'd(\d{1,2})', factor)[0]
    if num.isdigit() and faces.isdigit():
        num = int(num)
        faces = int(faces)
        if 0 < num <= 12 and 0 < faces <= 12:
            ran = []
            ran_char = ''
            for i in range(num):
                x = random.randint(1, faces)
                ran.append(x)
                ran_char += f"{x} "
            await session.send(f"{num}个{faces}面骰子，分别为{ran_char},总计{sum(ran)}")
        else:
            await session.send("喵喵喵?这数可以这么大的嘛？")
    else:
        await session.send('喵喵喵?')


@r.args_parser  # qq机器人用命令解析器
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    session.state['factor'] = session.current_arg_text.strip()
    # print(session.state['signature'])
