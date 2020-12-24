from nonebot import on_command, CommandSession
import os
import random
from PIL import Image
import numpy as np
import re
import time
import sys
import os
sys.path.append(os.path.split(os.path.realpath(__file__))[0])
import md5

file_path = os.path.split(os.path.realpath(__file__))[0] + '/data'
file_path_r18 = file_path + '/pixiv_r18'
file_path_general = file_path + '/pixiv_general'

# on_command 装饰器将函数声明为一个命令处理器

@on_command('setu', aliases=('来张涩图', '来张色图', '来张黄图', '来份色图',\
                             '来份涩图', '来亿份色图', '来亿份涩图', '亿份涩图', '来一份涩图', \
                             '来一份色图'), only_to_me=False)

async def setu(session: CommandSession): #消息发送
    if session.ctx['message_type'] == 'group':
        pic_name, pic_report = await get_setu(r18=False, Anti=False)
    else:
        raw_message = session.ctx['raw_message'] #亿份涩图功能
        Million = re.findall('.*(亿).*', raw_message)
        if '亿' in Million:
            pic_num = random.randint(10, 20)
            for i in range(pic_num):
                pic_pause = round(random.uniform(0, 0.5), 1)
                pic_name, pic_report = await get_setu(r18=True, Anti=False)

                if pic_name == None:
                    await  session.send("图片出错或改图失败")
                    return
                else:
                    await session.send(f"[CQ:image,file=file:///{pic_report}]")
                time.sleep(pic_pause)

            time.sleep(1)
            await session.send('！！')
            return True  #结束循环

        else:
            pic_name, pic_report = await get_setu(r18=True, Anti=False)

    if pic_name == None:
        await  session.send("图片出错或改图失败")
        return

    print(pic_name, pic_report)
    await session.send(f"""涩图一枚注意查收~\n图片id:{pic_name}""")
    time.sleep(0.2)
    await session.send(f'[CQ:image,file=file:///{pic_report}]')

# weather.args_parser 装饰器将函数声明为 weather 命令的参数解析器
# 命令解析器用于将用户输入的参数解析成命令真正需要的数据
@setu.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()


#path = 'C:\\Users\\Administrator\\Desktop\\酷Q Air\\data\\image\\setu'
#Qbotpath = 'setu'

async def get_setu(r18:bool, Anti:bool):
    if r18:
        path = file_path_r18
    else:
        path = file_path_general

    temp_path = ''
    temp_name = 'temp.jpg'

    pictures = []
    picture = ''
    for picture in os.listdir(path):
        pictures.append(picture)
    img_name = random.sample(pictures, 1)[0]
    img_path = f'{path}/{img_name}'

    if md5.md5pic(img_path):
        return img_name, img_path
    else:
        return None, None

'''
@on_command('_md5pic')
async def _md5pic(session: CommandSession):
    #path = 'C:\\Users\\Administrator\\Desktop\\酷Q Air\\data\\image\\setu'
    for md5i in md5pic(path):
        md5pic_report = md5i
        await session.send(md5pic_report)

@_md5pic.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()
   

def md5pic(path): #全文件夹刷新改图脚本
    pictures = []
    k = 0
    count = 0
    picture = ""
    a = np.random.randint(0,254)
    b = np.random.randint(0,254)
    c = np.random.randint(0,254)
    #path = 'C:\\Users\\MSI-PC\\Desktop\\pixiv' #酷Q Air\\data\\image\\
    for eachfile in os.listdir(path):
        count += 1
    for picture in os.listdir(path):       
        #print(picture)
        img = Image.open(f'{path}\\{picture}')
        #img.load()
        img.putpixel((0,0),(a,b,c,a))
        img = img.convert('RGB')
        img.save(f'{path}\\{picture}')
        k+=1
        if (count >= 500) and (k%100 == 0):
            yield (f'{k}/{count}')
        if (count < 500)and (count >= 50) and (k%10 == 0):
            yield (f'{k}/{count}')
        if (count <= 10):
            yield (f'{k}/{count}')
'''
        
