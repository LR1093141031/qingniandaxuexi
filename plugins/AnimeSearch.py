from nonebot import on_command, CommandSession
import sys
import os
import time
sys.path.append(os.path.split(os.path.realpath(__file__))[0])
from .module import TraceMoe, Tx

download_path = os.path.split(os.path.realpath(__file__))[0] + '/data/temp'
if not os.path.exists(download_path):
    os.makedirs(download_path)


@on_command('TraceMoetu', aliases=('搜番', '识番', 'tracemoe'), only_to_me=False)
async def TraceMoetu(session: CommandSession):
    pic_url = session.get('pic_id', prompt='TraceMoe搜番 请发送图片或url链接')
    tracemoe = TraceMoe.TraceMoe()
    tx_report = Tx.img_downloader(download_path, pic_url)
    result_text = ''
    time_start = time.time()
    if tx_report is False:
        await session.send('无法识别到图片或url,请重试')
        return False
    else:
        search_img = tx_report

    '(img_url, correct_rate, result_title, result_content)'
    result_dict = tracemoe.search(search_img)
    if result_dict:
        result_title = result_dict['result_title']
        correct_rate = result_dict['correct_rate']
        result_content = result_dict['result_content']
        result_img = tracemoe.pic_download(download_path)
        for i in range(len(result_img)):
            result_text += f'标题:{result_title[i]}\n相似度:{correct_rate[i]}\n{result_content[i]}\n[CQ:image,file=file:///{result_img[i]}]\n'
        await session.send(result_text)
    else:
        await session.send(tracemoe.state)

    time_stop = time.time()
    time_use = time_stop - time_start
    result_text += f'本次搜索用时{int(time_use)}秒'
    print(type(result_text))
    await session.send(result_text)


@TraceMoetu.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        if stripped_arg:
            session.state['pic_url'] = stripped_arg
