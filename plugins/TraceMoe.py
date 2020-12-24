import httpx
import json
import os
import re
from retrying import retry

agency = None


class TraceMoe:
    def __init__(self):
        self.agency = agency
        self.state = 200
        self.numres = 5  # 预定返回结果数
        self.tracemoe_url = "https://trace.moe/api/search"
        self.tracemoe = httpx.Client(http2=False, verify=False, timeout=30, proxies=self.agency)

        self.img_url = []  # 匹配图片url
        self.correct_rate = []  # 准确率
        self.result_title = []  # 结果标题
        self.result_content = []  # 搜索结果副标题
        self.download_report = []  # 匹配图片下载确认，成功则为全路径 失败为False

    def search(self, img_file_full_path=None):
        file_name = os.path.basename(img_file_full_path)
        print(f'搜索图片名称:{file_name}')
        files = {"image": ('anime.png', open(img_file_full_path, 'rb'))}
        try:
            response = self.tracemoe.post(url=self.tracemoe_url, files=files)
            response_json = json.loads(response.text)
            print(f"TraceMoe搜索状态码{response.status_code}")
        except Exception as e:
            print(f"TraceMoe网络请求出错", e)
            self.state = 'TraceMoe网络请求出错'
            return False

        search_num = len(response_json['docs'])     # 搜索结果数
        if search_num == 0:
            print("TraceMoe搜索无结果")
            self.state = 'TraceMoe无搜索匹配结果'
            return False
        return self._parser(response_json)

    def _parser(self, response_json):
        for i in response_json['docs']:
            # 搜索结果副标题
            synonyms_chinese = i['synonyms_chinese'][0] if len(i['synonyms_chinese']) != 0 else ''
            title = i['title']
            self.result_title.append(f"{title} {synonyms_chinese}")
            # 搜索结果副标题
            episode = str(i['episode'])
            at = str(int(i['at'] // 60)) + '分' + str(int(i['at'] % 60)) + '秒'
            self.result_content.append(f"匹配位置 第{episode}集 {at}")
            # 准确率
            similarity = str(round(i['similarity'], 2) * 100)   #百分比化
            self.correct_rate.append(similarity + '%')
            # 匹配图片url
            url = f"https://trace.moe/thumbnail.php?anilist_id={i['anilist_id']}&file={i['filename']}&t={i['at']}&token={i['tokenthumb']}"
            self.img_url.append(url)

        results = {'img_url': self.img_url, 'correct_rate': self.correct_rate, 'result_title': self.result_title,
                  'result_content': self.result_content}
        return self._result_limit(results)

    def _result_limit(self, results):  # 限制下结果数量
        for key in results.keys():
            if len(results[key]) >= self.numres + 1:
                results[key] = results[key][1:self.numres + 1]
            print(results[key])
        return results

    @retry(stop_max_attempt_number=2, wait_fixed=200)  # 自动重试两次，停顿0.2秒)
    def pic_download(self, download_path: str,  img_url=None):
        if img_url is None:
            print('===TraceMoe未输入下载url，尝试全部下载===')
            img_url_list = self.img_url
        else:
            img_url_list = list(img_url)

        for url in img_url_list:
            pic = self.tracemoe.get(url=url)
            file_name = re.findall(r'file=(.*)&t=', url)[0]
            with open(f'{download_path}/{file_name}.jpg', 'wb') as pic_file:
                pic_file.write(pic.content)
            print(f'图片ID {file_name}下载完成')
            self.download_report.append(f"{download_path}/{file_name}.jpg")
        return self.download_report


if __name__ == '__main__':  # 测试例子
    a = TraceMoe()
    result = a.search(r'C:\Users\MSI-PC\Desktop\bmss\85267677.jpg')
    # 搜索图片全路径
    if result:  # 失败会返回False
        a.pic_download(download_path=r'C:\Users\MSI-PC\Desktop\bmss', img_url=None)
    else:
        print(a.state)
    # 匹配结果图片下载路径 图片url 不填url就默认将本次结果图片都下载