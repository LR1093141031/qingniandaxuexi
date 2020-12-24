from nonebot import on_command, CommandSession, permission
import nonebot
import re
import random
import time
import sys
import os
from . import Pixiv, md5


path = os.path.split(os.path.realpath(__file__))[0]
download_path_r18 = path + '/data/pixiv_r18'
download_path_general = path + '/data/pixiv_general'

if not os.path.exists(download_path_r18):
    os.makedirs(download_path_r18)
if not os.path.exists(download_path_general):
    os.makedirs(download_path_general)


@on_command('pixiv_rank', aliases=('P站今日榜单', 'p站今日榜单', 'p站榜单', 'P站榜单', '今日榜单', '榜单'), only_to_me=False)
async def pixiv_rank(session: CommandSession):
    rank_range = session.get('rank_range')  # 先获取参数并判断
    if rank_range is None:         #榜单范围解析
        k = 0
    else:
        if rank_range.isdigit() is True:
            if 10 <= int(rank_range) <= 90:
                k = int(rank_range)
            else:
                await session.send('榜单起始数字范围10-90(别问我为什么)')
                return
        else:
            await session.send('瞎鸡儿输啥呢？(黑人问号)')
            return

    if session.ctx['message_type'] == 'group':              # 判断裙主
        if session.state['r18']:
            bot = nonebot.get_bot()
            superuser_list = list(bot.config.SUPERUSERS)
            if int(session.ctx['user_id']) in superuser_list:  # 这里是nb1的老问题
                r18 = True
                await session.send(f'超权 Pixiv R18榜单顺位{k}-{k + 10}加载中，请稍后...')
            else:
                r18 = False
                await session.send(f'权限不足 Pixiv 常规榜单顺位{k}-{k+10}加载中，请稍后...')
        else:
            r18 = False
            await session.send(f'Pixiv 常规榜单顺位{k}-{k+10}加载中，请稍后...')
    else:
        await session.send(f'Pixiv R18榜单顺位{k}-{k + 10}加载中，请稍后...')
        r18 = True

    download_path = download_path_r18 if r18 else download_path_general

    start_time = time.time()  # 开始计时
    pixiv = Pixiv.Pixiv()
    try:
        rank_dict = pixiv.get_rank(r18=r18).items()  # 获取榜单信息
    except Exception as e:
        print(e)
        await session.send('榜单数据获取失败，请重试')
        return
    rank_dict = list(rank_dict)

    if r18:               # 榜单头
        rank_text = f'P站今日R18榜单,顺位#{k}-#{k + 10}\n'
    else:
        rank_text = f'P站今日常规榜单,顺位#{k}-#{k + 10}\n'

    pixiv.get_url(k, k + 10)
    pixiv.pic_download(download_path)
    id_list = []
    for i, j in rank_dict[k:k+10]:  # i 是作者什么的信息 j是图片id
        id_list.append(j)
        rank_text += f"{i} {j}\n"
        rank_text += f"[CQ:image,file=file:///{download_path}/{j}.jpg]\n"

    for j in id_list:
        if not md5.md5pic(f'{download_path}/{j}.jpg'):  # 改图模块，防裸奔
            await session.send('改图失败！')
            return

    end_time = time.time()
    rank_text += f'本次用时:{int(end_time - start_time)}秒'
    time.sleep(0.5)
    await session.send(rank_text)


@pixiv_rank.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    #stripped_arg = session.current_arg_text.split()
    session.state['r18'] = True if re.findall('[rR]18', session.current_arg_text) else False
    rank_range_text = session.current_arg_text.replace('r18', '').replace('R18', '')
    rank_range = re.findall(r"\d{1,3}", rank_range_text)
    session.state['rank_range'] = rank_range[0] if rank_range else None
    r18 = re.findall(r"[r,R]18", session.current_arg_text)
    session.state['r18mode'] = True if r18 else False


@on_command('pixiv_pic', aliases=('P站图片', 'p站图片', 'P站', 'p'), only_to_me=False)
async def pixiv_pic(session: CommandSession):
    pixiv = Pixiv.Pixiv()
    pic_id = session.get('pic_id', prompt='P站图片id？')
    pic_url = pixiv.get_url_single(pic_id)
    if pic_url == '请求超时':
        await session.send('url请求超时')
        return
    if not pic_url:
        await session.send('P站中无法搜索到该图片,请重试。')
        return
    pic_file = pixiv.pic_download_single(download_path_general, pic_url)
    if not pic_file:
        await session.send('下载请求超时')
        return
    await session.send(f"[CQ:image,file=file:///{pic_file}]")

@pixiv_pic.args_parser
async def _(session: CommandSession):
# 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        # 该命令第一次运行（第一次进入命令会话）
        if stripped_arg:
            # 第一次运行参数不为空，意味着用户直接将城市名跟在命令名后面，作为参数传入
            # 例如用户可能发送了：天气 南京
            session.state['pic_id'] = stripped_arg
        return

    if not stripped_arg:
        # 用户没有发送有效的城市名称（而是发送了空白字符），则提示重新输入
        # 这里 session.pause() 将会发送消息并暂停当前会话（该行后面的代码不会被运行）
        session.pause('等待输入P站图片ID')

    # 如果当前正在向用户询问更多信息（例如本例中的要查询的城市），且用户输入有效，则放入会话状态
    #session.state[session.current_key] = stripped_arg

@nonebot.scheduler.scheduled_job(
    'cron',
    # year=None,
    # month=None,
    # day=None,
    # week=None,
    day_of_week="mon,tue,wed,thu,fri,sat,sun",
    hour=12,
    minute=random.randint(1, 30),
    # second=None,
    # start_date=None,
    # end_date=None,
    # timezone=None,
)
async def _():
    k = random.randint(1, 87)
    f = random.randint(7, 12)
    r = random.randint(0, 5)
    group_list = [213104082, 114672965]
    message = ['涩图时间到啦~', '发点涩图。', '无内鬼来点se图~~', '今天的图马马虎虎吧！~', '差点忘了今日份的蛇图', '阿巴阿巴阿巴']
    pixiv = Pixiv.Pixiv()
    pixiv.get_rank()
    pixiv.get_url(k, k+f)
    pic_list = pixiv.pic_download(download_path_general)
    bot = nonebot.get_bot()
    for group in group_list:
        await bot.send_group_msg(group_id=group, message=message[r])
        for pic in pic_list:
            await bot.send_group_msg(group_id=group, message=f'[CQ:image,file=file:///{pic}]')
