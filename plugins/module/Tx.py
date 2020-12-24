import re
import httpx
from retrying import retry
# 


@retry(stop_max_attempt_number=2, wait_fixed=100)  # 自动重试3次，间隔0.1秒
def img_downloader(self, download_path: str, pic_url: str):
    print('SauceNao.tx_download,输入url:', pic_url)
    if re.search(r"\[CQ:.*\]", pic_url) is not None:
        print('QQ图片下载器输入含有CQ码，处理中')
        pic_url = re.search(r"\[CQ:.*\]", pic_url)[0]  # 获得纯净CQ码
        CQcode = pic_url

        file_name = re.findall(r"file=(.*?)\.", CQcode, flags=0)[0]  # 获得下载图片的名称，不包括格式image
        if file_name is not None:
            pic_download_name = file_name
        else:
            pic_download_name = 'temp'
        print(pic_download_name)

        url = re.findall(r"url=(.*)\]", CQcode, flags=0)[0].replace(r"','", '/')  # 获得纯净url
        print(url)
        pic_url = url
    else:  # 直接传入图片url，尝试解析
        if re.search(r"^https:.*", pic_url) is not None:
            print('QQ图片下载器输入为URl，处理中')
            print(pic_url)
            pic_download_name = re.findall(r"\d{4,8}", pic_url, flags=0)[0]  # 随便取几个数字
            if pic_download_name is None:
                pic_download_name = 'temp'
        else:
            self.state = '输入url非cq码或http链接，下载不执行'
            print('输入url非cq码或http链接，下载不执行')
            return False

    pic = self.tx.get(url=pic_url, headers=self.search_img_download_headers)
    print('tx图片格式', pic.headers['Content-Type'])
    img_type = pic.headers['Content-Type'].replace('image/', '')  # 获得下图片格式，tx的下载格式总是这个
    # ============================================11.29修改 现在从返回的headers中读取下载的图片格式
    pic_download_name = pic_download_name + f".{img_type}"

    with open(f'{download_path}/{pic_download_name}', 'wb') as f:
        f.write(pic.content)
        print(f'图片ID{download_path}/{pic_download_name}下载完成')
        return f'{download_path}/{pic_download_name}'


def tx_download(self, download_path: str,  pic_url: str):  # Tx聊天图单线程 pic_download_id : str,
    # 图片下载

    if re.search(r"\[CQ:.*\]", pic_url) != None:
        print('QQ图片下载器输入含有CQ码，处理中')
        pic_url = re.search(r"\[CQ:.*\]", pic_url)[0]
        CQcode = pic_url
        #print(CQcode)
        Filecode = re.findall(r"file=(.*?),", CQcode, flags=0)[0]#.replace('file=', '').replace(',', '')
        if Filecode != None:
            pic_download_id = Filecode
        else:
            pic_download_id = 'temp.jpg'
        print(Filecode)
        Url = re.findall(r"url=(.*)\]", CQcode, flags=0)[0].replace(r"','", '/')#.replace('url=', '').replace(']', '').replace(r"','", '/')
        print(Url)
        pic_url = Url
    else:
        if re.search(r"^https:.*", pic_url) != None:
            print('QQ图片下载器输入为URl，处理中')
            print(pic_url)
            pic_download_id = re.findall(r"new/(.*?)/", pic_url, flags=0)[0] + '.jpg'
            if pic_download_id == None:
                pic_download_id = 'temp.jpg'
        else:
            print('输入url非cq码或http链接，下载不执行')
            return False

    pic_download_head = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'gchat.qpic.cn',
        #'If-Modified-Since': 'Wed, 29 Jul 2020 12:55:42 GMT',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}

    try:
        pic = requests.get(pic_url, headers=pic_download_head, stream=True, verify=False, timeout=20)
    except requests.exceptions.ConnectTimeout:
        # PixivDownload(pic_download_id, pic_url)
        print('Connection超时报错=======================')
        return '下载超时'
    except requests.exceptions.ConnectionError:  # 下载超时抛错
        # PixivDownload(pic_download_id, pic_url)
        print('Connection错误报错 目标===================')
        return '下载超时'

    #============================================8.23临时加上的 gohttp版本特性
    pic_download_id = pic_download_id.replace('image', 'jpg')

    with open(f'{download_path}/{pic_download_id}', 'wb') as f:
        f.write(pic.content)
        print(f'图片ID{download_path}/{pic_download_id}下载完成')
        return f'{download_path}/{pic_download_id}'
