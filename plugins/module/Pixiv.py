import os
import time
import re
import json
import httpx
from bs4 import BeautifulSoup
from retrying import retry
import threading
import zipfile
import imageio

agency = r'http://localhost:4780'  # 代理地址

pic_size = ['mini', 'thumb', 'small', 'regular', 'original']
# 获取图片url时，可选图片尺寸，在Pixiv.get_url方法后，获得返回值，或通过Pixiv.pic_url_dict['id'] 来获得该id图片所有尺寸url
# tag解析需要在Pixiv.get_url方法后 通过Pixiv.pic_tag_dict['id'] 来获得该id图片所有tag
# pic_tag_dict构造 {illuist_id:{"jp_tag":'ツムギ(プリコネ)', "cn_tag":'纺希（公主连结）'.......}.......}


class Pixiv:

    def __init__(self, r18=False):
        self.state = 200
        self.agency = agency  # 代理地址
        self.r18 = r18  # 初始化r18设定，可在其余方法中再次关启r18
        self.qbot_arrange = True  # get_rank qbot输出规范化
        self.enable_cache = True  # 是否启用缓存功能
        self.cache_time_gap = 3600  # 缓存刷新间隔(秒)
        self.pic_size_list = ['mini', 'thumb', 'small', 'regular', 'original']
        self.enable_tag_parser = True  # 是否启用图片tag解析

        self.is_that_gif = False  # 给gif解析用的 感觉更容易混乱了。

        self.module_path = os.path.dirname(__file__)  # 文件缓存目录
        self.page_1 = ''
        self.page_2 = ''

        self.pixiv = httpx.Client(http2=True, verify=False, proxies=self.agency)  # http2模式 代理

        self.Rank_Headers = {
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'cookie': '__cfduid=da9298b676dbf81e8d441ddd0a6df5ef71603884131; first_visit_datetime_pc=2020-10-28+20%3A22%3A12; p_ab_id=1; p_ab_id_2=3; p_ab_d_id=1500665255; yuid_b=QoeVZSI; __utmc=235335808; _fbp=fb.1.1603884141459.1674750365; _ga=GA1.2.1346609669.1603884138; _gid=GA1.2.1548075155.1603884187; __cf_bm=a223182f381623e01f939b442e9108f7139f502b-1603892990-1800-AeW4n4geJGVoQM66mut6iiOpxOWF+WY3M8vv9xHqFOjfG8jjdnz/30ZLO0WVSqt3NShXeQlvGH8LMIipxJM9Iry3QVz8ip04U1DaU9EmRlTI3LM0WcvoeIFksWVz7d2QQ6NhSmCIIOiH3DE2N9BFiakPfVdRgPWIsq+hgVcd5qDNtURB5hXP1VUSq7Xs1hGTTg==; device_token=dc3913c1fffdfa1374703f128820e752; PHPSESSID=27199888_cPIb1kQn1TjCepL3r7MoOLFzfsnaNLyN; c_type=21; privacy_policy_agreement=2; a_type=0; b_type=2; __utma=235335808.1346609669.1603884138.1603884138.1603893210.2; __utmz=235335808.1603893210.2.2.utmcsr=accounts.pixiv.net|utmccn=(referral)|utmcmd=referral|utmcct=/login; __utmv=235335808.|2=login%20ever=no=1^3=plan=normal=1^5=gender=female=1^6=user_id=27199888=1^9=p_ab_id=1=1^10=p_ab_id_2=3=1^11=lang=zh=1; __utmt=1; ki_t=1603893222448%3B1603893222448%3B1603893222448%3B1%3B1; ki_r=; __utmb=235335808.2.10.1603893210',
            'referer': 'https://www.pixiv.net/ranking.php',
        }
        self.Url_Headers = {
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'cookie': 'limited_ads=%7B%22responsive%22%3A%22%22%7D; p_ab_id=0; p_ab_id_2=3; p_ab_d_id=1345951712; first_visit_datetime_pc=2020-03-20+19%3A19%3A11; yuid_b=GHkRhoI; a_type=0; b_type=2; __utmc=235335808; _fbp=fb.1.1598279801128.774244369; _ga=GA1.2.664530923.1594351285; PHPSESSID=27199888_FvQ8jCKtr8yhZmFicCTsvQYSmmeJLmUe; c_type=21; privacy_policy_agreement=2; ki_r=; login_ever=yes; adr_id=AXzxrLrFF26gi7DXdUi5HO235YoWcrDgilnfD4BIGa26i9w0; __utmz=235335808.1599704607.5.3.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __cfduid=d3c8315391bd2f1fed55b0b566bd087201601435540; first_visit_datetime=2020-10-15+22%3A08%3A39; webp_available=1; __utmv=235335808.|2=login%20ever=yes=1^3=plan=normal=1^5=gender=female=1^6=user_id=27199888=1^9=p_ab_id=0=1^10=p_ab_id_2=3=1^11=lang=zh=1^20=webp_available=yes=1; limited_ads=%7B%22responsive%22%3A%22%22%2C%22t_header%22%3A%22%22%7D; __adpon_uid=c36696e1-eead-42aa-9bc2-b9bc15090198; ki_s=210803%3A0.0.0.0.0; _gid=GA1.2.996981156.1603791565; categorized_tags=0VZuk18GJB~3ze0RLmk59~6sZKldb07K~8Vlr9rDUAd~Ig5OcZugU6~OEXgaiEbRa~OT-C6ubi9i~_K7rbjS0MD~_bee-JX46i~aLBjcKpvWL~b8b4-hqot7~jYnWl04aAC~jfnUZgnpFl~m3EJRa33xU; __utma=235335808.664530923.1594351285.1603854538.1603861680.30; __cf_bm=09b794c403ae92f31ce6a157d74003239c0e5e83-1603861680-1800-Ad9PABTu7G0VfoP7/04LVycwDP2L/kmB7cUcvWXkx3VUGn2VSPSzOtk2UduwUtfaUM0XEdHS5356I1QeD8rFsX9pbFmxrBePJRzGrC+PJeflN+Ysc+hDsvv399QCM8He0tlAX9WBJNSC9HfzYJAHlxBz5yPBEjFMxEDuya6KKhl97sJ7whideC+2hbf9dzAlbg==; __utmt=1; tag_view_ranking=liM64qjhwQ~0xsDLqCEW6~JwOnNobdvo~CZnOKinv48~CmIov8_f5j~_YQZKxAGgg~TAE-gr5obV~uvBGOtCzqF~zZZn32I7eS~xe8_207kqj~3gc3uGrU1V~RTJMXD26Ak~xXhq3SGORQ~rxNSXJvQUh~dD3787FF73~cbmDKjZf9z~mIBxNOpKNs~d8fHMcEG3R~TWrozby2UO~KN7uxuR89w~VIOKa7rioU~pNtQi6YIt-~-sp-9oh8uv~jYnWl04aAC~1ra2aNvKnU~iQ0G1R6oGs~MM6RXH_rlN~-k4xbUv_zd~0rFsG_VyY9~zIv0cf5VVk~dqqWNpq7ul~k712URXStf~5oPIfUbtd6~faHcYIP1U0~ls-I-Yd_FD~8Vlr9rDUAd~xi1_CfbLI5~W7cVeVEFxJ~zhidwuyCQH~qtVr8SCFs5~WVrsHleeCL~_iaP-J1xu4~y8GNntYHsi~BU9SQkS-zU~OrK_VSfMRB~ICsokp9RfZ~xgA3yCXKWS~Aa5GphyXq3~HlDdLQY3rl~aKhT3n4RHZ~GWJojdnBMY~JM99SoMFHa~jrclGyQTmB~lRHALpj_iJ~aLBjcKpvWL~fUS-Ay2M9Z~I2lfHE5kDb~Me5rTOmxXm~FgYArp6riX~MkgAbGkXH6~QqOL4vbk6n~QieGHVEFAp~_K7rbjS0MD~_EOd7bsGyl~RthHN5LPvq~Bd2L9ZBE8q~jH0uD88V6F~6n5sWl9nNm~WPlzUoQVT7~DpO7Lofslr~cwLG8ks7Vj~TptCt3Vpq6~OBJrLjuGCM~qSrf3MWq5h~MQ5kmPUxWr~Y1xsKC1Dhb~nrxUvzd6tf~LS8MUzdViR~Iz8wZrq8OA~zua6IKRTwP~0WfxkC_83a~jxTkX87qFn~IxzCBHy4eN~-LwvviyTfq~BZjl-9zViZ~RsPWi2XNrX~cVXbK891Av~TKxZkzHnJH~4PDB5TRjMr~UniH1CHOF_~dg_40nEhSE~jfnUZgnpFl~N8wKmgxh7L~KLTjgBW-On~_g3rODJw8z~KUeYMPwpE9~821uj_yCkp~Txs9grkeRc~bDXre79-DK~kffGOewQdf; __utmb=235335808.4.10.1603861680; ki_t=1598279846257%3B1603854572938%3B1603861731118%3B9%3B30',
        }
        self.Download_Headers = {
            'accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'referer': 'https://www.pixiv.net/artworks/Host',
            'sec-fetch-dest': 'image',
        }
        self.Gif_Download_Headers = {
            'accept-encoding': 'identity',
            'origin': 'https://www.pixiv.net',
            'referer': 'https://www.pixiv.net/',
            'sec-ch-ua': '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
        }
        self.params_r18_page_1 = {'mode': 'daily_r18'}
        self.params_r18_page_2 = {'mode': 'daily_r18', 'p': '2', 'format': 'json'}
        self.params_regular_page_1 = {'mode': 'daily'}
        self.params_regular_page_2 = {'mode': 'daily', 'p': '2', 'format': 'json'}

        self.rank_num = []
        self.title_list = []
        self.artist_list = []
        self.pic_id_list = []

        self.pic_url_dict = {}  # {illuist_id:{'mini':url, 'thumb':url, 'small':url, 'regular':url, 'original':url}}

        self.pic_tag_dict = {}  # 层构造 {illuist_id:{"jp_tag":'ツムギ(プリコネ)', "cn_tag":'纺希（公主连结）'.......}.......}
        self.arranged_rank = []

    def get_rank(self, r18=False):  # 获取pixiv榜单
        self.r18 = r18
        print(f"Pixiv 获取{'r18' if self.r18 else '常规'}榜单 {f'启用{self.cache_time_gap}秒' if self.enable_cache else '未启用'}缓存")
        if self.enable_cache:  # 是否启用缓存功能
            self.page_1 = f"{self.module_path}/rank_page_1_{'r18' if self.r18 else 'regular'}.html"  # 缓存榜单文件路径，区分是否r18
            self.page_2 = f"{self.module_path}/rank_page_2_{'r18' if self.r18 else 'regular'}.json"
            if self._rank_cache_check():  # 检查缓存
                content_1, content_2 = self._rank_cache_read()
                return self._rank_parser(content_1, content_2)
        params_1 = self.params_r18_page_1 if r18 else self.params_regular_page_1
        params_2 = self.params_r18_page_2 if r18 else self.params_regular_page_2
        try:
            response_1 = self.pixiv.get('https://www.pixiv.net/ranking.php', params=params_1, headers=self.Rank_Headers)
            response_2 = self.pixiv.get('https://www.pixiv.net/ranking.php', params=params_2, headers=self.Rank_Headers)
            print(f"Pxiv榜单状态码:{response_1.status_code} {response_2.status_code}")
        except Exception as e:
            print(f'榜单数据获取失败，请重试{e}')
            self.state = f'榜单数据获取失败，请重试{e}'
            return False
        content_1 = response_1.content.decode('utf-8')
        content_2 = response_2.content.decode('utf-8')
        if self.enable_cache:
            self._rank_cache_write(content_1, content_2)
        return self._rank_parser(content_1, content_2)

    def get_rank_url(self, pic_id_range_start=0, pic_id_range_end=10):
        pic_id_list = self.pic_id_list[pic_id_range_start:pic_id_range_end]
        threads = []
        url_list = []
        for ID in pic_id_list:
            t = MyThread(target=Pixiv.get_url_single, args=(self, ID,))
            threads.append(t)
        threads_num = len(threads)
        for ti in range(threads_num):
            time.sleep(0.1)  # 线程启动间隔
            threads[ti].start()
            if ti == threads_num - 1:  # 启动所有线程后 启动监视线程
                time.sleep(0.1)
                Watchmen = threading.Thread(target=Threads_watchmen, args=(threads,))
                Watchmen.start()
                Watchmen.join()
                time.sleep(0.1)  # 完成线程监视，读取返回结果
                for tj in range(threads_num):
                    url_list.append(threads[tj].get_result())  # 可能为False
                    self.pic_url_dict.update({pic_id_list[tj]: url_list[tj]})
                print('全部Url请求完成')
                return url_list

    def get_rank_pic(self, download_path: str, pic_size='regular'):  # 多线程
        if not self.pic_url_dict:
            print('pic_download 多线程下载方法无法获得url，请先get_url获取')
            return False
        pic_download_url_dict = self.pic_url_dict
        pic_full_path = []
        pic_num = len(pic_download_url_dict)
        threads = []

        for i in range(pic_num):
            url = list(pic_download_url_dict.values())[i][pic_size]
            t = MyThread(target=Pixiv.pic_download_single, args=(self, download_path, url))
            threads.append(t)

        for j in range(pic_num):
            time.sleep(0.2)  # 线程启动间隔
            threads[j].start()

            if j == pic_num - 1:  # 启动所有线程后 监视线程
                time.sleep(0.2)
                Watch = threading.Thread(target=Threads_watchmen, args=(threads,))
                Watch.start()
                Watch.join()
                time.sleep(0.1)  # 完成线程监视，读取返回结果
                for z in range(pic_num):  # 完成线程下载，读取结果
                    pic_full_path.append(threads[z].get_result())  # 可能为False
                print('全部下载请求完成')
                return pic_full_path

    def _rank_parser(self, response_1_content, response_2_content):
        soup = BeautifulSoup(response_1_content, 'html.parser', from_encoding='utf-8')
        rank_items = soup.find_all(class_='ranking-item')
        for rank_item in rank_items:
            self.rank_num.append(rank_item['data-rank-text'].replace('#', ''))
            self.title_list.append(rank_item['data-title'])
            self.artist_list.append(rank_item['data-user-name'])
            self.pic_id_list.append(rank_item['data-id'])
        rankhtml_2 = json.loads(response_2_content)
        contents = rankhtml_2['contents']
        for rank_item in contents:
            self.rank_num.append(str(rank_item['rank']))
            self.title_list.append(rank_item['title'])
            self.artist_list.append(rank_item['user_name'])
            self.pic_id_list.append(rank_item['illust_id'])
        return self._rank_qbot_arrange() if self.qbot_arrange else self._rank_arrange()

    def _rank_cache_check(self) -> bool:  # True为无需更新，False为需要更新
        if os.path.isfile(self.page_1) and os.path.isfile(self.page_2):
            if os.stat(self.page_1).st_mtime + self.cache_time_gap < time.time():
                return False
            else:
                return True
        else:
            return False

    def _rank_cache_read(self):
        print(f"读取Pxivi {'r18' if self.r18 else '常规'}榜单缓存")
        with open(self.page_1, 'rb') as res_1:
            response_1_content = res_1.read()
        with open(self.page_2, 'rb') as res_2:
            response_2_content = res_2.read()
        return response_1_content, response_2_content

    def _rank_cache_write(self, response_1_content, response_2_content):
        print(f"写入Pxivi {'r18' if self.r18 else '常规'}榜单缓存")
        with open(self.page_1, 'w', encoding='utf-8') as res_1:
            res_1.write(response_1_content)
        with open(self.page_2, 'w', encoding='utf-8') as res_2:
            res_2.write(response_2_content)
        return True

    def _rank_arrange(self) -> dict:
        return {'rank': self.rank_num, 'title': self.title_list, 'artist': self.artist_list, 'id': self.pic_id_list}

    def _rank_qbot_arrange(self) -> list:
        for i in range(len(self.rank_num)):
            contents = f"#{self.rank_num[i]}  作品：{self.title_list[i]} 作者：{self.artist_list[i]} {self.pic_id_list[i]}"
            self.arranged_rank.append(contents)
        return self.arranged_rank

    @retry(stop_max_attempt_number=2, wait_fixed=200)  # 自动重试两次，停顿0.2秒)
    def pic_download_single(self, download_path: str, pic_url: str):
        if self.is_that_gif:  # 引流 节约下脑细胞
            return self.gif_download_single(download_path, pic_url)
        pic_name = pic_url.split('/')[-1]  # 仅限pixiv网站，图片url很规整
        if os.path.isfile(f'{download_path}/{pic_name}') and (os.path.getsize(f'{download_path}/{pic_name}') >= 1000):
            print(f'图片ID{pic_name}已存在')
            return f'{download_path}/{pic_name}'
        else:
            pic = self.pixiv.get(pic_url, headers=self.Download_Headers, timeout=20)
            with open(f'{download_path}/{pic_name}', 'wb') as f:
                f.write(pic.content)
            print(f'图片ID{pic_name}下载完成')
            return f'{download_path}/{pic_name}'

    @retry(stop_max_attempt_number=2, wait_fixed=200)  # 自动重试两次，停顿0.2秒
    def get_url_single(self, pic_id: str):
        pic_html = self.pixiv.get(f'https://www.pixiv.net/artworks/{pic_id}', headers=self.Url_Headers, timeout=8)
        if pic_html.status_code == '404':
            return False
        content = pic_html.content.decode('utf-8')
        soup = BeautifulSoup(content, 'html.parser', from_encoding='utf-8')
        preload_content = soup.find_all('meta', id='meta-preload-data')[0]['content']
        urls_json_form = json.loads('{' + re.findall(r'"urls":\{(.*?)\},', preload_content)[0] + '}')
        print(f'获取url，id={pic_id}')
        if self.enable_tag_parser:  # 是否tag解析
            self._tag_parer(content)
        return urls_json_form

    @retry(stop_max_attempt_number=2, wait_fixed=200)  # 自动重试两次，停顿0.2秒
    def pic_parser_single(self, pic_id: str):
        print('Pixiv单图解析')
        pic_html = self.pixiv.get(f'https://www.pixiv.net/artworks/{pic_id}', headers=self.Url_Headers, timeout=20)
        if pic_html.status_code == '404':
            return False
        content = pic_html.content.decode('utf-8')
        soup = BeautifulSoup(content, 'html.parser', from_encoding='utf-8')

        self.is_that_gif = True if re.findall('动图', soup.title.string) else False  # 是否为动图的分水岭
        if self.is_that_gif:
            print('该图片为gif图，请使用gif_download_single(url)来下载')

        preload_content = soup.find_all('meta', id='meta-preload-data')[0]['content']
        urls_json_form = json.loads('{' + re.findall(r'"urls":\{(.*?)\},', preload_content)[0] + '}')
        pic_title_singal = re.findall(r'"illustTitle":"(.*?)",', preload_content)[0]
        pic_artist_singal = re.findall(r'"userName":"(.*?)"\}', preload_content)[0]
        if self.enable_tag_parser:  # 是否tag解析
            self._tag_parer(content)
        return {'title': pic_title_singal, 'artist': pic_artist_singal, 'url': urls_json_form, 'tag': self.pic_tag_dict[pic_id]}

    def gif_download_single(self, download_path: str, url_unhandled: str):
        print('Pixiv动图下载')
        gif_host = 'https://i.pximg.net/img-zip-ugoira/img/'
        gif_host_tail = '_ugoira600x600.zip'
        gif_url = gif_host + re.findall(r'/img/(.*)_ugoira0.jpg', url_unhandled)[0] + gif_host_tail
        print(gif_url)
        zip_file_name = re.findall(r'.*/(.*?\.zip)', gif_url)[0]
        zip_file_path = f'{download_path}/{zip_file_name}'
        foder_name = os.path.splitext(zip_file_name)[0]
        foder_path = f'{download_path}/{foder_name}'
        gif_file = f'{download_path}/{foder_name}.gif'
        print(zip_file_name, foder_name, gif_file)
        if os.path.isfile(gif_file):
            print('gif已存在')
            return gif_file
        # 完成乱七八糟一堆路径或者名字的解析
        gif_response = self.pixiv.get(url=gif_url, headers=self.Gif_Download_Headers, timeout=60)
        print('gif完成下载，处理中')
        with open(zip_file_path, 'wb') as f:
            f.write(gif_response.content)
        zip_file = zipfile.ZipFile(zip_file_path)
        if os.path.isdir(foder_path):
            pass
        else:
            os.mkdir(foder_path)
        zip_file.extractall(foder_path)
        zip_file.close()
        os.remove(zip_file_path)
        # 完成原始文件下载
        pictures = os.listdir(foder_path)
        gif_frame = []
        for picture in pictures:
            gif_frame.append(imageio.imread(f'{foder_path}/' + picture))
            os.remove(f'{foder_path}/' + picture)
        os.rmdir(foder_path)
        # 卸磨杀驴 完成 拜拜
        imageio.mimsave(gif_file, gif_frame, duration=0.086)
        return gif_file


    def _tag_parer(self, content):  # 不能外部调用。只能通过get_url 方法，并开启tag解析，访问pic_tag_dict
        soup = BeautifulSoup(content, 'html.parser', from_encoding='utf-8')
        preload_content = soup.find_all('meta', id='meta-preload-data')[0]['content']
        illust_id = re.findall(r'"illust":\{"(.*?)"', preload_content)[0]
        print(f'处理tag，id={illust_id}')
        tags_json_form = json.loads('{' + re.findall(r'"tags":\[.*?\]', preload_content)[0] + '}')
        tag_dict = {}
        for tag in tags_json_form['tags']:
            jp_tag = tag['tag']
            cn_tag = tag['translation']['en'] if "translation" in tag else ''
            tag_dict.update({jp_tag:cn_tag})
        self.pic_tag_dict.update({illust_id: tag_dict})
        return self.pic_tag_dict


class MyThread(threading.Thread):
    def __init__(self, target, args):
        super(MyThread, self).__init__()
        self.target = target
        self.args = args
    def run(self):
        self.result = self.target(*self.args)
    def get_result(self):
        return self.result


def Threads_watchmen(threads: list):
    threads_num = len(threads)
    threads_ack = [0] * threads_num
    threads_done = 0
    for i in range(threads_num):
        while threads[i].isAlive():
            time.sleep(0.7)  # 检查间隔
            continue
        else:
            threads_ack[i] = 1
            # time.sleep(0.3)  #检查间隔
            # threads_ack_chart = ''.join(['+' if i else '-' for i in threads_ack])  #图形化进程
            # print(threads_ack_chart)
            for j in threads_ack:
                threads_done = threads_done + j
            if threads_done == threads_num:
                print('线程监视完成')
                return True
            else:
                threads_done = 0
                pass


if __name__ == '__main__':
    p = Pixiv()
    #a = p.get_rank(r18=True)
    #print(a)
    #b = p.get_rank_url(85, 100)
    #print(b)
    #c = p.get_rank_pic(r'C:\Users\MSI-PC\Desktop\bmss')
    #print(c)
    img_dict = p.pic_parser_single('86229507')
    gif = p.pic_download_single(r'C:\Users\MSI-PC\Desktop\bmss', img_dict['url']['original'])
    print(gif)
# 榜单系列方法与单图方法不同，榜单无法获得详细标签，仅单图解析可以获得
# gif 无法通过榜单系列方法获得，只能 先pic_parser_single，获取该gif的信息，然后通过类内量 is_that_gif 判断交由 pic_download_single，还是gif_download_single，gif_download_single会自行处理url，需要提供原图url