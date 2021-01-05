import re
import httpx
from retrying import retry
# 腾讯系数据 文件处理模块 自动CQ码解析


@retry(stop_max_attempt_number=2, wait_fixed=100)  # 自动重试3次，间隔0.1秒
def img_downloader(download_path: str, pic_url: str):
    print('tx图片下载器输入url:', pic_url)
    if re.search(r"\[CQ:.*\]", pic_url) is not None:
        print('输入为CQ码，处理中')
        pic_url = re.search(r"\[CQ:.*\]", pic_url)[0]  # 获得纯净CQ码
        CQcode = pic_url

        pic_url = re.findall(r"url=(.*)\]", CQcode, flags=0)[0].replace(r"','", '/')  # 获得纯净url
        name = re.findall(r"file=(.*?)\.", CQcode, flags=0)[0]  # 获得下载图片的名称，不包括格式image
        file_name = name if name is not None else 'temp'

    else:  # 直接传入图片url，尝试解析
        if re.search(r"^https:.*", pic_url) is not None:
            print('输入为URl，处理中')
            name = re.findall(r"\d{4,8}", pic_url, flags=0)[0]  # 随便取几个数字
            file_name = name if name is not None else 'temp'
        else:
            print('输入url非cq码或http链接，下载不执行')
            return False

    tx = httpx.Client(http2=False, timeout=10)
    pic = tx.get(url=pic_url)
    print('tx图片格式', pic.headers['Content-Type'])
    img_type = pic.headers['Content-Type'].replace('image/', '')  # 获得下图片格式，tx的下载格式总是这个
    file_name = f"{file_name}.{img_type}"

    with open(f'{download_path}/{file_name}', 'wb') as f:
        f.write(pic.content)
        print(f'图片ID{download_path}/{file_name}下载完成')
        return f'{download_path}/{file_name}'

