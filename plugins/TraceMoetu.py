from nonebot import on_command, CommandSession
import sys
import os

sys.path.append(os.path.split(os.path.realpath(__file__))[0])
import time
import TraceMoe

'还是没改完=========================================================11.30'

download_path = os.path.split(os.path.realpath(__file__))[0] + '/data/temp'
if not os.path.exists(download_path):
    os.makedirs(download_path)


@on_command('TraceMoetu', aliases=('搜番', '识番', 'tracemoe'), only_to_me=False)
async def TraceMoetu(session: CommandSession):
    pic_url = session.get('pic_id', prompt='TraceMoe搜番 请发送图片或url链接')
    tracemoe = TraceMoe.TraceMoe()
    tx_report = tracemoe.tx_download(download_path, pic_url)

    time_start = time.time()

    if tx_report == False:
        await session.send('无法识别到图片或url,请重试')
        return False

    if tx_report == '下载超时':
        await session.send('图片接收失败，请重试')
        return False

    if tx_report != None:
        search_img = tx_report
        (img_url, correct_rate, result_title, result_content) = tracemoe.tracemoe(search_img)
        if 'NetworkError' in img_url:
            await session.send("请求失败啦！~")
            return

        result_num = len(img_url) if len(img_url) <= 5 else 5  # 限制下最大发图数量

        if result_num == 0:
            print('无搜索结果')
        else:
            if img_url[0] == 'NetworkError':
                await session.send('搜番请求出错或达到限制')
                raise ConnectionError('bot处理部分抛错 TraceMoe未完成搜索')

        result_img = []
        for i in range(result_num):
            result_img.append('')
            TraceMoe_Report = tracemoe.tracemoe_download(download_path, img_url[i])
            # TraceMoe_Report = download_path + '/' + TraceMoe_Report  # 这里读一下全路径
            result_img[i] += TraceMoe_Report
            if (result_img[i] is False) or (result_img[i] == '下载超时'):
                await session.send('返回结果图片下载失败')
            else:
                pass
    print('resuly_img===================', result_img)
    search_text = f'''TraceMoe搜番结果\n{result_num}个搜索结果\n'''

    if result_num != 0:
        for i in range(result_num):
            search_text = search_text + f'''标题:{result_title[i]}\n相似度:{correct_rate[i]}\n{result_content[i]}\n[CQ:image,file=file:///{result_img[i]}]\n'''
    else:
        pass

    time_stop = time.time()
    time_use = time_stop - time_start
    search_text += f'本次搜索用时{int(time_use)}秒'
    print(type(search_text))
    await session.send(search_text)


@TraceMoetu.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        if stripped_arg:
            session.state['pic_url'] = stripped_arg
