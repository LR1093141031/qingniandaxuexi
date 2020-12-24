import requests
import os
import time
import json
import re
import sys
from lxml import etree
import PIL.Image as Image
import random
from nonebot import on_command, CommandSession
sys.path.append('./')
import time

download_path = os.path.split(os.path.realpath(__file__))[0] + '/data/daxuexi'
top_part_path = download_path

daxuexi = requests.session()

@on_command('qingnian', aliases=('大学习', '青年大学习'),  only_to_me=False) #qq机器人用

async def qingnian(session: CommandSession): #qq机器人用命令体
    url = Get_Latest_ID()
    if url == '请求超时':
        await session.send('请求超时,请重试！如无法解决联系管理')
        return
    else:
        await session.send('搜索最新大学习成功！正在下载中......')
    report = End_Pic_Download(url)
    if report == '下载超时':
        await session.send('下载超时,请重试！如无法解决联系管理')
    else:
        await session.send('下载成功！正在修改中......')
    paste_report = Pic_Paste()
    if paste_report != False:
        await session.send(f'[CQ:image,file=file:///{download_path}/Final.jpg]')
    else:
        await  session.send('改图失败! 参数有误,请联系管理!')

@qingnian.args_parser #qq机器人用命令解析器
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()

def Get_Latest_ID(): #下载图片ID函数 用于自动搜索最新一期大学习 并返回图片url
    Get_ID_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': '',
        'Host': 'news.cyol.com',
        'If-Modified-Since': '',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    }
    try:
        ID_html = daxuexi.get('http://news.cyol.com/node_67071.htm', headers=Get_ID_headers, stream=True, timeout=10)
        print(ID_html)
    except TimeoutError:
        return '请求超时'
    ID_html_Context = ID_html.content.decode('utf-8')
    ID_html_tree = etree.HTML(ID_html_Context)
    xpath = r"/html/body/div[4]/dl/dd/ul/li[1]/a" #/html/body/div[4]/dl/dd/ul/li[1]/a
    items = ID_html_tree.xpath(xpath)
    #print(items[0].attrib['href'])
    End_Pic_Url = items[0].attrib['href']
    End_Pic_Url = End_Pic_Url.replace(r'index.html', r'images/end.jpg')  #普通大学习
    End_Pic_Url = End_Pic_Url.replace(r'm.html', r'images/end.jpg')      #特辑
    print(End_Pic_Url)
    return End_Pic_Url


#Get_Latest_ID()


def End_Pic_Download(pic_url : str, latesd_name = 'latest'): #下载图片函数 用于输入url下载图片 与上个函数串联用就行
    Download_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': '',
        'Host': 'h5.cyol.com',
        'If-Modified-Since': '',
        'If-None-Match': '',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    }
    try:
        end_pic = daxuexi.get(pic_url, headers=Download_headers, stream=True, timeout=10)
        #print(pic_url, end_pic)
        if end_pic.status_code == 200:
            print('大学习图片下载请求返回200，正常')
        else:
            print('图片网页不存在，或状态不正确,状态码:', end_pic.status_code)
            return False
    except requests.exceptions.ConnectTimeout:
        print('Connection超时报错=======================')
        return '下载超时'
    except requests.exceptions.ConnectionError:  # 下载超时抛错
        print('Connection错误报错 目标===================')
        return '下载超时'

    with open(f'{download_path}/{latesd_name}.jpg', 'wb') as f:
        f.write(end_pic.content)
        print(f'图片ID{latesd_name}下载完成')
        return f'{latesd_name}.jpg'

#End_Pic_Download('http://h5.cyol.com/special/daxuexi/9xbajfslc4/images/end.jpg')

def Pic_Paste(latesd_name = 'latest'): #不写传入了，嫌麻烦直接写死 图片粘贴函数，与上两个函数串联直接用 注意图片位置
    try:
        img = Image.new('RGB', (828, 1414), (255, 255, 255))
        num = random.randint(1, 9) #自己p的上面那个头部图片数量，这就是个随机找个图，图路径名注意下1-9
        img.paste(Image.open(f"{top_part_path}/{num}.jpg"), (0, 0, 828, 70))
        img.paste(Image.open(f"{download_path}/{latesd_name}.jpg"), (0, 70, 828, 1414))
        img.save(f"{download_path}/Final.jpg", "JPEG")
        return True
    except:
        print('改图失败')
        return False

#URL = Get_Latest_ID()
#End_Pic_Download(URL)
#Pic_Paste()