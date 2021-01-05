import httpx
from bs4 import BeautifulSoup
import os
import re
from retrying import retry
agency = None  # 使用代理的话就修改为代理地址


class Ascii2d:
    def __init__(self):
        self.agency = agency
        self.state = 200
        self.numres = 3  # 预定返回结果数
        self.ascii2d_url = "https://ascii2d.net/search/multi"
        self.img_url_prefix = 'https://ascii2d.net/'
        self.ascii2d = httpx.Client(http2=False, verify=False, timeout=30, proxies=self.agency)

        self.img_url = []  # 匹配图片url
        self.correct_rate = []  # 准确率，Ascii2d没有准确率
        self.result_title = []  # 结果标题
        self.result_content = []  # 搜索结果副标题
        self.download_report = []  # 匹配图片下载确认，成功则为全路径 失败为False
        self.herf = []  # 所有匹配结果对应超链接，不返回，需要自行访问

        self.button_word = ['色合検索', '特徴検索', '詳細登録']

    def search(self, img_file_full_path: str):
        file_name = os.path.basename(img_file_full_path)
        print(f'搜索图片名称:{file_name}')
        files = {'file': ("image.png", open(img_file_full_path, 'rb'))}
        try:
            response = self.ascii2d.post(url=self.ascii2d_url, files=files)
            print('Ascii2d搜索状态码:', response.status_code)
        except Exception as e:
            self.state = 'Ascii2d请求出错'
            print('Ascii2d请求出错', e)
            return False
        return self._parser(response)

    def _parser(self, response):
        soup = BeautifulSoup(response, 'html.parser', from_encoding='utf-8')
        items = soup.find_all(class_='row item-box')
        print(f'Ascii2d搜索到{len(items)}个匹配对象')
        if len(items) <= 1:
            self.state = 'Ascii2d无匹配结果'
            print('Ascii2d无搜索匹配结果')
            return False
        for item in items:
            url = self.img_url_prefix + item.find('img')['src']  # 获取页面全部结果图url
            self.img_url.append(url)
            detail_a = item.find_all('a')  # 图片描述
            # detail_strong = item.find_all('strong')  # 图片描述_加粗 这个不常见
            title = detail_a[0].string # + (detail_strong[0].string if detail_strong else '')  # 图片描述标题
            self.result_title.append(title)
            content = detail_a[1].string  # 图片描述副标题
            self.result_content.append(content)

            herf = ''
            herf += detail_a[0]['herf'] if (detail_a[0].string not in self.button_word) and ('herf' in detail_a[0]) else ''
            herf += ' ' + detail_a[1]['herf'] if (detail_a[1].string not in self.button_word) and ('herf' in detail_a[0]) else ''
            self.herf.append(herf)

            self.correct_rate.append(None)

        results = {'img_url': self.img_url, 'correct_rate': self.correct_rate, 'result_title': self.result_title,
              'result_content': self.result_content}

        return self._result_limit(results)

    def _result_limit(self, results):  # 限制下结果数量
        for key in results.keys():
            if len(results[key]) >= self.numres+1:
                results[key] = results[key][1:self.numres+1]
            print(results[key])
        return results

    @retry(stop_max_attempt_number=2, wait_fixed=200)  # 自动重试2次，间隔0.2秒
    def pic_download(self, download_path: str, img_url=None):
        if img_url is None:
            print('===Ascii2d未输入下载url，尝试全部下载===')
            img_url_list = self.img_url[1:self.numres+1]
        else:
            img_url_list = list(img_url)

        for url in img_url_list:
            pic = self.ascii2d.get(url)
            self.state = f'Saucenao-pic_download 下载错误'
            file_name = re.findall(r".*/(.*?\.jpg)", url)[0]
            with open(f'{download_path}/{file_name}', 'wb') as f:
                f.write(pic.content)
                print(f'图片ID {file_name}下载完成')
                self.download_report.append(f'{download_path}/{file_name}')
        return self.download_report  # 列表 每个元素都是下载好的图片全路径


if __name__ == '__main__':  # 测试例子
    a = Ascii2d()
    result = a.search(r'C:\Users\MSI-PC\Desktop\bmss\85262871.jpg')
    # 搜索图片全路径
    if result:  # 失败会返回False
        pass
        a.pic_download(download_path=r'C:\Users\MSI-PC\Desktop\bmss', img_url=None)
    else:
        print(a.state)
    # 匹配结果图片下载路径 图片url 不填url就默认将本次结果图片都下载