import os
import re
from lxml import etree
import httpx
from retrying import retry
# 为网络不好的情况加的retry
agency = None
# 使用代理的话就修改为代理地址
api_key = '6dc42921e33dc26514cb96b1f3832c997397aea9'
# "6dc42921e33dc26514cb96b1f3832c997397aea9" '4a0c3fb88e0bbeac5248c5eed5df131129762f1a'
# agency 代理地址 api_key 为Saucenao网站的api许可，注册一个点账号信息就有了，也可以留空，100次访问/ip日


class SauceNao:

    def __init__(self):
        self.state = 200
        self.api_key = api_key
        self.agency = agency

        self.saucenao = httpx.Client(http2=False, verify=False, timeout=20, proxies=self.agency)
        # http1模式 调用SauceNao api

        self.saucenao_url = 'http://saucenao.com/search.php'
        self.api_mode = 0  # 0 =普通html, 1 = xml api（未实现）, 2 = json api
        self.minsim = '80!'  # 决定图片边缘细节
        self.numres = 5  # 预定返回结果数
        self.dbmask = 999  # 999为类型全开
        # forcing minsim to 80 is generally safe for complex images, but may miss some edge cases. If images being
        # checked are primarily low detail, such as simple sketches on white paper, increase this to cut down on false
        # positives.

        self.search_url = f'{self.saucenao_url}?output_type={self.api_mode}&numres={self.numres}&minsim= \
                            {self.minsim}&dbmask={999}&api_key={self.api_key}'

        self.result_img_download_headers = {}  # 可以自定headers,目前api不需要

        self.pic_id_list = []  # 返回结果图片名称列表，用于类内调用
        self.pic_url_list = []  # 返回结果图片url，用于类内调用
        self.img_url = []  # 匹配图片url
        self.correct_rate = []  # 准确率
        self.result_title = []  # 结果标题
        self.result_content = []  # 搜索结果副标题
        self.download_report = []  # 匹配图片下载确认，成功则为全路径 失败为False

    def search(self, img_file_full_path: str):
        file_name = os.path.basename(img_file_full_path)
        print(f'搜索图片名称:{file_name}')
        files = {'file': ("image.png", open(img_file_full_path, 'rb'))}
        try:
            response = self.saucenao.post(url=self.search_url, files=files)
            print('SauceNao搜索状态码:', response.status_code)
        except Exception as e:
            self.state = 'Saucenao请求出错'
            print('Saucenao请求出错', e)
            return False
        return self._parser(response)

    def _parser(self, response):
        search_html = response.content.decode('utf-8')  # 解码

        match_num = len(re.findall("resultimage", search_html))  # 判断下有几个结果
        suspect_num = len(re.findall("result hidden", search_html))
        match_num = match_num - suspect_num
        print(f'SauceNao搜索到{match_num}个匹配对象')

        if match_num == 0:
            self.state = 'SauceNao无匹配结果'
            print('SauceNao无搜索匹配结果')
            return False

        search_html = etree.HTML(search_html)  # etree化，做html解析，要在re搜索完可能结果后再etree

        for i in range(match_num):
            n = i + 2
            # 匹配图片url
            img_xpath = f"/html/body/div[2]/div[3]/div[{n}]/table/tr/td[1]/div/a/img"
            img_html = search_html.xpath(img_xpath)
            self.img_url.append(img_html[0].get('src'))
            # 匹配图片相似度
            corr_xpath = f"/html/body/div[2]/div[3]/div[{n}]/table/tr/td[2]/div[1]/div[1]"
            corr_html = search_html.xpath(corr_xpath)
            self.correct_rate.append(corr_html[0].text)
            # 匹配图片主标题
            title_xpath = f"/html/body/div[2]/div[3]/div[{n}]/table/tr/td[2]/div[2]/div[1]"
            title_html = search_html.xpath(title_xpath)
            self.result_title.append(title_html[0][0].text)
            # 匹配图片副标题
            title0_xpath = f"/html/body/div[2]/div[3]/div[{n}]/table/tr/td[2]/div[2]/div[1]/text()"
            title0_html = search_html.xpath(title0_xpath)
            self.result_title[i] += title0_html[0] if len(title0_html) else ''
            # 匹配图片文字说明
            result_content_xpath = f"/html/body/div[2]/div[3]/div[{n}]/table/tr/td[2]/div[2]/div[2]"
            result_content_html = search_html.xpath(result_content_xpath)
            result_content0_xpath = f"/html/body/div[2]/div[3]/div[{n}]/table/tr/td[2]/div[2]/div[2]/text()"
            result_content0_html = search_html.xpath(result_content0_xpath)
            result_content = ''
            for j in result_content_html[0]:
                result_content += j.text if j.text else '' + ' '
            result_content += result_content0_html[0] if len(result_content0_html) else ''
            self.result_content.append(result_content)

        if len(self.img_url) != match_num:
            self.state = 'SauceNao页面解析遇到结果数量不匹配错误'
            print('SauceNao页面解析遇到结果数量不匹配错误')
            return False

        results = {'img_url': self.img_url, 'correct_rate': self.correct_rate, 'result_title': self.result_title,
                  'result_content': self.result_content}
        return results

    def _result_limit(self, results):  # 限制下结果数量
        for key in results.keys():
            if len(results[key]) >= self.numres+1:
                results[key] = results[key][1:self.numres+1]
            print(results[key])
        return

    @retry(stop_max_attempt_number=2, wait_fixed=200)  # 自动重试2次，间隔0.2秒
    def pic_download(self, download_path: str, img_url=None):
        if img_url is None:
            print('===SauceNao未输入下载url，尝试全部下载===')
            img_url_list = self.img_url
        else:
            img_url_list = list(img_url)

        for url in img_url_list:
            pic = self.saucenao.get(url, headers=self.result_img_download_headers)
            try:  # 有时会遇到不包含文件名的url
                file_name = re.findall(r".*/(.*?\.jpg)", url)[0]
            except Exception as e:
                file_name = re.findall(r"\d{5,15}", url)[0] + r'.jpg'

            with open(f'{download_path}/{file_name}', 'wb') as f:
                f.write(pic.content)
                print(f'图片ID {file_name}下载完成')
                self.download_report.append(f'{download_path}/{file_name}')
        return self.download_report  # 列表 每个元素都是下载好的图片全路径


if __name__ == '__main__':  # 测试例子
    a = SauceNao()
    result = a.search(r'C:\Users\MSI-PC\Desktop\bmss\85262871.jpg')
    # 搜索图片全路径
    if result:  # 失败会返回False
        a.pic_download(download_path=r'C:\Users\MSI-PC\Desktop\bmss', img_url=None)
    else:
        print(a.state)
    # 匹配结果图片下载路径 图片url 不填url就默认将本次结果图片都下载
