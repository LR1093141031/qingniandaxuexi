# coding=utf-8

import os
import random

import httpx
from bs4 import BeautifulSoup
from PIL import Image, ImageFont, ImageDraw

# 大学习完成图 及缓存图下载路径 在此处修改 为该模块文件位置/data/daxuexi
# PIL修改所需文件也需在这个文件内
download_path = os.path.split(os.path.realpath(__file__))[0] + '/data/daxuexi'
if not os.path.exists(download_path):
    os.makedirs(download_path)

class QingNianDaXueXi:
    """
    青年大学习 爬虫 伪图脚本
    """
    def __init__(self):
        self.title = ''  # 青年大学习标题暂存
        self.search_url = 'http://news.cyol.com/gb/channels/vrGlAKDl/index.html'
        self.index_url = ''
        self.image_url = ''

        self.agency = None
        self.daxuexiClient = httpx.Client(http2=False, proxies=self.agency, verify=False)

    def search(self):
        """
        search方法，获取最新大学习相关信息。
        :return: 依次返回最新一期大学习主标题、网页url、完成图url
        """
        # 搜索最新一期大学习 及其完成图url
        search_html = self.daxuexiClient.get(url=self.search_url, timeout=10)
        print(f'大学习搜索返回:{search_html.status_code}')
        search_content = search_html.content.decode('utf-8')

        soup = BeautifulSoup(search_content, 'html.parser')
        url = soup.find(class_="movie-list").find('li').find('a')['href']  # 最新一期大学习网页
        self.index_url = url.replace(r'm.html', r'index.html')  # 跳转后的学习网页
        self.image_url = self.index_url.replace(r'index.html', r'images/end.jpg')  # 大学习完成图url

        # 获取最新一期大学习标题
        title_html = self.daxuexiClient.get(url=self.index_url, timeout=10)
        print(f'大学习标题返回:{title_html.status_code}')
        title_content = title_html.content.decode('utf-8')

        soup = BeautifulSoup(title_content, 'html.parser')
        self.title = soup.find(class_="cont_h").find('h1').string
        print(self.title)
        return self.title, self.index_url, self.image_url

    def finished_pic_download(self):
        """
        finished_pic_download，大学习完成图下载，
        :return: 返回下载的完成图全路径
        """
        finished_pic = self.daxuexiClient.get(url=self.image_url, timeout=10)
        with open(f'{download_path}/latest.jpg', 'wb') as f:
            f.write(finished_pic.content)
        print('青年大学习完成图下载完成')
        return f'{download_path}/latest.jpg'

    def finished_pic_modify(self):
        """
        finished_pic_modify，修饰完成图
        :return: 返回修改后图全路径
        """

        num = random.randint(1, 9)  # 头部图片文件名 这里为简单粗暴的1-9随机数，来选择对应文件名的贴图
        img = Image.new('RGB', (828, 1489), (255, 255, 255))
        img.paste(Image.open(f"{download_path}/{num}.jpg"), (0, 0, 828, 70))

        title_img = Image.open(f"{download_path}/title.jpg")
        title_draw = ImageDraw.Draw(title_img)
        font = ImageFont.truetype("simhei.ttf", 37, encoding="unic")  # 设置字体
        title_draw.text((80, 5), self.title, 'black', font)
        img.paste(title_img, (0, 70, 828, 145))

        img_result = Image.open(f"{download_path}/latest.jpg")
        img_result = img_result.resize((828, 1344))

        img.paste(img_result, (0, 145, 828, 1489))
        img.save(f"{download_path}/final.jpg")
        return f"{download_path}/final.jpg"


if __name__ == '__main__':
    daxuexi = QingNianDaXueXi()
    daxuexi.search()
    daxuexi.finished_pic_download()
    daxuexi.finished_pic_modify()

