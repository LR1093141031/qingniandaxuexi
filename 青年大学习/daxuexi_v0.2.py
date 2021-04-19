# coding=utf-8

import os
import random

import httpx
from bs4 import BeautifulSoup
from PIL import Image, ImageFont, ImageDraw

# 下载及暂存路径
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
        search方法，无返回值，仅用作搜索调用，可在调用后访问获取的url
        """
        search_html = self.daxuexiClient.get(url=self.search_url, timeout=10)
        print(f'大学习搜索返回:{search_html.status_code}')
        search_content = search_html.content.decode('utf-8')
        return self._parser(search_content)

    def _parser(self, search_content):
        """
        _parser内部方法，无返回值，用于搜索最新大学习网页
        """
        soup = BeautifulSoup(search_content, 'html.parser', from_encoding='utf-8')
        self.index_url = soup.find()

