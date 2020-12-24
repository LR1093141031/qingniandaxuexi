from nonebot import on_command, CommandSession
import nonebot
import os
import sys
sys.path.append('./')
file_path = os.path.split(os.path.realpath(__file__))[0] + '/data/day'


#神社群 213104082 测试群 1045264581
@on_command('ctx', aliases=['info', 'test'])
async def test(session:CommandSession): #测试用模块
    info1 = session.ctx
    info2 = session.event.self_id
    info3 = session.event.user_id
    info4 = session.event.operator_id
    await session.send(f"ctx: {info1}  \n event.self_id:{info2}   \n   event.user_id:{info3}    \n     event.operator_id:{info4}    \n {session.ctx}")

@nonebot.scheduler.scheduled_job(
    'cron',
    # year=None,
    # month=None,
    # day=None,
    # week=None,
    day_of_week="mon,tue,wed,thu,fri,sat,sun",
    hour=6,
    minute=30,
    # second=None,
    # start_date=None,
    # end_date=None,
    # timezone=None,
)
async def _():
    path = file_path + '/morning.jpg'
    if not os.path.isfile(path):
        print("morning文件丢失？")
    morning_message = f"""唔姆~ 早上好啊~
[CQ:image,file=file:///{path}]
"""
    bot = nonebot.get_bot()
    await bot.send_group_msg(group_id=213104082, message=morning_message)
    #await bot.send_group_msg(group_id=1045264581, message=morning_message)


@nonebot.scheduler.scheduled_job(
    'cron',
    # year=None,
    # month=None,
    # day=None,
    # week=None,
    day_of_week="mon,tue,wed,thu,fri,sat,sun",
    hour=7,
    minute=1,
    # second=None,
    # start_date=None,
    # end_date=None,
    # timezone=None,
)
async def _():
    bot = nonebot.get_bot()
    message = '不起来学习了？ 穷人不配快乐了？ 有啥可睡的？ 打算25以前考厨师证？ '
    await bot.send_private_msg(user_id=1093141031, message=message)
