from nonebot import on_command, CommandSession
import sys
import os

sys.path.append(os.path.split(os.path.realpath(__file__))[0])
# import random
# from PIL import Image
# import numpy as np
import time
import SauceNao
import Group_Permission

download_path = os.path.split(os.path.realpath(__file__))[0] + '/data/temp'
if not os.path.exists(download_path):
    os.makedirs(download_path)


@on_command('SauceNaotu', aliases=('搜图', '识图', '找图', 'Sauce搜图', 'SauceNao搜图'), only_to_me=False)
async def SauceNaotu(session: CommandSession):
    permission = Group_Permission.Permission()  # 检查权限
    if session.ctx['message_type'] == 'group':  # 这里不确定是否只检查群权限
        enable = permission.permission_check(session.ctx['group_id'], 'SauceNaotu')
        print('=========', enable)
        if enable is False:
            await session.send('无权限执行该命令')
            return
        else:
            pass

    saucenao = SauceNao.SauceNao()
    pic_url = session.get('pic_id', prompt='SauceNao搜图 请发送图片或url链接')
    tx_report = saucenao.tx_download(download_path, pic_url)

    if tx_report is False:
        await session.send('无法识别到图片或url,请重试')
        return False

    time_start = time.time()

    if tx_report is not False:
        saucenao_dict = saucenao.search(tx_report)  # (img_url, correct_rate, result_title, result_content)
        if saucenao_dict is False:
            await session.send(saucenao.state)
            return True

        result_num = len(saucenao_dict['img_url'])

        if result_num == 0:
            await session.send('SauceNao无搜索结果')
            return True
    else:
        await session.send(saucenao.state)
        return True

    sauce_report = saucenao.pic_download(download_path)  # 下载全部结果图片，返回为列表

    search_text = f'''SauceNao搜图结果\n{result_num}个搜索结果\n'''

    for i in range(result_num):
        search_text = search_text + f'''标题:{saucenao_dict['result_title'][i]}\n相似度:{saucenao_dict['correct_rate']
        [i]}\n{saucenao_dict['result_content'][i]}\n[CQ:image,file=file:///{sauce_report[i]}]\n'''
    else:
        pass

    time_stop = time.time()
    time_use = time_stop - time_start
    search_text += f'本次搜索用时{int(time_use)}秒'
    await session.send(search_text)


@SauceNaotu.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        # 该命令第一次运行（第一次进入命令会话）
        if stripped_arg:
            # 第一次运行参数不为空，意味着用户直接将城市名跟在命令名后面，作为参数传入
            # 例如用户可能发送了：天气 南京
            print('================stripped', stripped_arg)
            session.state['pic_url'] = stripped_arg
        return
    else:
        if (session.ctx['raw_message'] is None) or (session.ctx['raw_message'] == ''):
            print('--------------------raw', session.ctx['raw_message'])
            session.pause('发送图片或url链接')
