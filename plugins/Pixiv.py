import os
import time
import re
import json
from lxml import etree
import httpx
from bs4 import BeautifulSoup
from retrying import retry
import threading

'所有模块都会自行重新尝试，如果失败，会返回False值，然后再根据State属性（可能为数字字符串404 200 或纯字符串） 来向上级返回错误类型'
agency = r'http://localhost:4780'


class MyThread(threading.Thread):
    def __init__(self, target, args):
        super(MyThread, self).__init__()
        self.target = target
        self.args = args

    def run(self):
        self.result = self.target(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return False


def Threads_watchmen(threads : list):
    threads_num = len(threads)
    threads_ack = [0] * threads_num
    threads_done = 0
    # print(threads_num)

    for i in range(threads_num):
        while threads[i].isAlive():
            time.sleep(0.7)  #检查间隔
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


class Pixiv:

    def __init__(self, debug=False, log=False):
        self.state = 200
        if debug:
            print('Pixiv模块开启全局debug')
        self.debug = debug

        try:
            self.agency = agency
        except NameError as e:
            self.agency = r'http://localhost:4780'

        self.pixiv = httpx.Client(http2=True, verify=False, proxies=self.agency)  # http2模式 代理

        self.Rank_Headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application\
            /signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'cookie': '__cfduid=da9298b676dbf81e8d441ddd0a6df5ef71603884131; first_visit_datetime_pc=2020-10-28+20%3A22%3A12; p_ab_id=1; p_ab_id_2=3; p_ab_d_id=1500665255; yuid_b=QoeVZSI; __utmc=235335808; _fbp=fb.1.1603884141459.1674750365; _ga=GA1.2.1346609669.1603884138; _gid=GA1.2.1548075155.1603884187; __cf_bm=a223182f381623e01f939b442e9108f7139f502b-1603892990-1800-AeW4n4geJGVoQM66mut6iiOpxOWF+WY3M8vv9xHqFOjfG8jjdnz/30ZLO0WVSqt3NShXeQlvGH8LMIipxJM9Iry3QVz8ip04U1DaU9EmRlTI3LM0WcvoeIFksWVz7d2QQ6NhSmCIIOiH3DE2N9BFiakPfVdRgPWIsq+hgVcd5qDNtURB5hXP1VUSq7Xs1hGTTg==; device_token=dc3913c1fffdfa1374703f128820e752; PHPSESSID=27199888_cPIb1kQn1TjCepL3r7MoOLFzfsnaNLyN; c_type=21; privacy_policy_agreement=2; a_type=0; b_type=2; __utma=235335808.1346609669.1603884138.1603884138.1603893210.2; __utmz=235335808.1603893210.2.2.utmcsr=accounts.pixiv.net|utmccn=(referral)|utmcmd=referral|utmcct=/login; __utmv=235335808.|2=login%20ever=no=1^3=plan=normal=1^5=gender=female=1^6=user_id=27199888=1^9=p_ab_id=1=1^10=p_ab_id_2=3=1^11=lang=zh=1; __utmt=1; ki_t=1603893222448%3B1603893222448%3B1603893222448%3B1%3B1; ki_r=; __utmb=235335808.2.10.1603893210',
            #'cookie': 'p_ab_id=0; p_ab_id_2=3; p_ab_d_id=1345951712; first_visit_datetime_pc=2020-03-20+19%3A19%3A11; yuid_b=GHkRhoI; a_type=0; b_type=2; __utmc=235335808; _fbp=fb.1.1598279801128.774244369; _ga=GA1.2.664530923.1594351285; PHPSESSID=27199888_FvQ8jCKtr8yhZmFicCTsvQYSmmeJLmUe; c_type=21; privacy_policy_agreement=2; ki_r=; login_ever=yes; adr_id=AXzxrLrFF26gi7DXdUi5HO235YoWcrDgilnfD4BIGa26i9w0; __utmz=235335808.1599704607.5.3.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __cfduid=d3c8315391bd2f1fed55b0b566bd087201601435540; first_visit_datetime=2020-10-15+22%3A08%3A39; webp_available=1; __utmv=235335808.|2=login%20ever=yes=1^3=plan=normal=1^5=gender=female=1^6=user_id=27199888=1^9=p_ab_id=0=1^10=p_ab_id_2=3=1^11=lang=zh=1^20=webp_available=yes=1; limited_ads=%7B%22responsive%22%3A%22%22%2C%22t_header%22%3A%22%22%7D; __adpon_uid=c36696e1-eead-42aa-9bc2-b9bc15090198; ki_s=210803%3A0.0.0.0.0; _gid=GA1.2.996981156.1603791565; __utma=235335808.664530923.1594351285.1603818211.1603854538.29; __utmt=1; tags_sended=1; categorized_tags=0VZuk18GJB~3ze0RLmk59~6sZKldb07K~8Vlr9rDUAd~Ig5OcZugU6~OEXgaiEbRa~OT-C6ubi9i~_K7rbjS0MD~_bee-JX46i~aLBjcKpvWL~b8b4-hqot7~jYnWl04aAC~jfnUZgnpFl~m3EJRa33xU; __cf_bm=ee92e7aa11708f415612952ebbbe6a26869cf884-1603854538-1800-AVfJa+E1FwlzTUmy+jsOdBu8jBoDmb3LfW7rfIro1ZZ1xav64+UFiu4BxR9282hJCa+vh6CUlXKsg7k917L5kpbyjG8R+YQpKm2IUApOLviGS0yTfXU56anFnsT2C8Fenloyu/KK4fiW5rF6DhYwA+07ulRuM4v3yXkkxts1ZY9Y3d6GJkPQYhFCXB2BXNQwoQ==; tag_view_ranking=liM64qjhwQ~0xsDLqCEW6~JwOnNobdvo~CZnOKinv48~CmIov8_f5j~_YQZKxAGgg~TAE-gr5obV~uvBGOtCzqF~zZZn32I7eS~xe8_207kqj~3gc3uGrU1V~RTJMXD26Ak~xXhq3SGORQ~rxNSXJvQUh~dD3787FF73~cbmDKjZf9z~mIBxNOpKNs~d8fHMcEG3R~TWrozby2UO~KN7uxuR89w~VIOKa7rioU~pNtQi6YIt-~-sp-9oh8uv~jYnWl04aAC~1ra2aNvKnU~iQ0G1R6oGs~MM6RXH_rlN~-k4xbUv_zd~0rFsG_VyY9~zIv0cf5VVk~dqqWNpq7ul~k712URXStf~5oPIfUbtd6~faHcYIP1U0~ls-I-Yd_FD~8Vlr9rDUAd~xi1_CfbLI5~W7cVeVEFxJ~zhidwuyCQH~qtVr8SCFs5~WVrsHleeCL~xgA3yCXKWS~Aa5GphyXq3~HlDdLQY3rl~aKhT3n4RHZ~GWJojdnBMY~JM99SoMFHa~jrclGyQTmB~lRHALpj_iJ~aLBjcKpvWL~fUS-Ay2M9Z~I2lfHE5kDb~Me5rTOmxXm~FgYArp6riX~MkgAbGkXH6~QqOL4vbk6n~QieGHVEFAp~_K7rbjS0MD~_EOd7bsGyl~RthHN5LPvq~Bd2L9ZBE8q~jH0uD88V6F~6n5sWl9nNm~WPlzUoQVT7~DpO7Lofslr~cwLG8ks7Vj~TptCt3Vpq6~OBJrLjuGCM~qSrf3MWq5h~MQ5kmPUxWr~Y1xsKC1Dhb~nrxUvzd6tf~LS8MUzdViR~Iz8wZrq8OA~zua6IKRTwP~0WfxkC_83a~jxTkX87qFn~IxzCBHy4eN~-LwvviyTfq~BZjl-9zViZ~RsPWi2XNrX~cVXbK891Av~TKxZkzHnJH~4PDB5TRjMr~UniH1CHOF_~dg_40nEhSE~jfnUZgnpFl~N8wKmgxh7L~KLTjgBW-On~_g3rODJw8z~KUeYMPwpE9~821uj_yCkp~Txs9grkeRc~bDXre79-DK~kffGOewQdf~TZUoZ8Dws9~jvjiJrlzjm~Ar4oQTjv_h~KB3wNuihPi~yvELB8t0gh; ki_t=1598279846257%3B1603854572938%3B1603854572938%3B9%3B26; __utmb=235335808.4.10.1603854538',
            'referer': 'https://www.pixiv.net/ranking.php',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147\
            .135 Safari/537.36'
        }
        self.Url_Headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'cookie': 'limited_ads=%7B%22responsive%22%3A%22%22%7D; p_ab_id=0; p_ab_id_2=3; p_ab_d_id=1345951712; first_visit_datetime_pc=2020-03-20+19%3A19%3A11; yuid_b=GHkRhoI; a_type=0; b_type=2; __utmc=235335808; _fbp=fb.1.1598279801128.774244369; _ga=GA1.2.664530923.1594351285; PHPSESSID=27199888_FvQ8jCKtr8yhZmFicCTsvQYSmmeJLmUe; c_type=21; privacy_policy_agreement=2; ki_r=; login_ever=yes; adr_id=AXzxrLrFF26gi7DXdUi5HO235YoWcrDgilnfD4BIGa26i9w0; __utmz=235335808.1599704607.5.3.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __cfduid=d3c8315391bd2f1fed55b0b566bd087201601435540; first_visit_datetime=2020-10-15+22%3A08%3A39; webp_available=1; __utmv=235335808.|2=login%20ever=yes=1^3=plan=normal=1^5=gender=female=1^6=user_id=27199888=1^9=p_ab_id=0=1^10=p_ab_id_2=3=1^11=lang=zh=1^20=webp_available=yes=1; limited_ads=%7B%22responsive%22%3A%22%22%2C%22t_header%22%3A%22%22%7D; __adpon_uid=c36696e1-eead-42aa-9bc2-b9bc15090198; ki_s=210803%3A0.0.0.0.0; _gid=GA1.2.996981156.1603791565; categorized_tags=0VZuk18GJB~3ze0RLmk59~6sZKldb07K~8Vlr9rDUAd~Ig5OcZugU6~OEXgaiEbRa~OT-C6ubi9i~_K7rbjS0MD~_bee-JX46i~aLBjcKpvWL~b8b4-hqot7~jYnWl04aAC~jfnUZgnpFl~m3EJRa33xU; __utma=235335808.664530923.1594351285.1603854538.1603861680.30; __cf_bm=09b794c403ae92f31ce6a157d74003239c0e5e83-1603861680-1800-Ad9PABTu7G0VfoP7/04LVycwDP2L/kmB7cUcvWXkx3VUGn2VSPSzOtk2UduwUtfaUM0XEdHS5356I1QeD8rFsX9pbFmxrBePJRzGrC+PJeflN+Ysc+hDsvv399QCM8He0tlAX9WBJNSC9HfzYJAHlxBz5yPBEjFMxEDuya6KKhl97sJ7whideC+2hbf9dzAlbg==; __utmt=1; tag_view_ranking=liM64qjhwQ~0xsDLqCEW6~JwOnNobdvo~CZnOKinv48~CmIov8_f5j~_YQZKxAGgg~TAE-gr5obV~uvBGOtCzqF~zZZn32I7eS~xe8_207kqj~3gc3uGrU1V~RTJMXD26Ak~xXhq3SGORQ~rxNSXJvQUh~dD3787FF73~cbmDKjZf9z~mIBxNOpKNs~d8fHMcEG3R~TWrozby2UO~KN7uxuR89w~VIOKa7rioU~pNtQi6YIt-~-sp-9oh8uv~jYnWl04aAC~1ra2aNvKnU~iQ0G1R6oGs~MM6RXH_rlN~-k4xbUv_zd~0rFsG_VyY9~zIv0cf5VVk~dqqWNpq7ul~k712URXStf~5oPIfUbtd6~faHcYIP1U0~ls-I-Yd_FD~8Vlr9rDUAd~xi1_CfbLI5~W7cVeVEFxJ~zhidwuyCQH~qtVr8SCFs5~WVrsHleeCL~_iaP-J1xu4~y8GNntYHsi~BU9SQkS-zU~OrK_VSfMRB~ICsokp9RfZ~xgA3yCXKWS~Aa5GphyXq3~HlDdLQY3rl~aKhT3n4RHZ~GWJojdnBMY~JM99SoMFHa~jrclGyQTmB~lRHALpj_iJ~aLBjcKpvWL~fUS-Ay2M9Z~I2lfHE5kDb~Me5rTOmxXm~FgYArp6riX~MkgAbGkXH6~QqOL4vbk6n~QieGHVEFAp~_K7rbjS0MD~_EOd7bsGyl~RthHN5LPvq~Bd2L9ZBE8q~jH0uD88V6F~6n5sWl9nNm~WPlzUoQVT7~DpO7Lofslr~cwLG8ks7Vj~TptCt3Vpq6~OBJrLjuGCM~qSrf3MWq5h~MQ5kmPUxWr~Y1xsKC1Dhb~nrxUvzd6tf~LS8MUzdViR~Iz8wZrq8OA~zua6IKRTwP~0WfxkC_83a~jxTkX87qFn~IxzCBHy4eN~-LwvviyTfq~BZjl-9zViZ~RsPWi2XNrX~cVXbK891Av~TKxZkzHnJH~4PDB5TRjMr~UniH1CHOF_~dg_40nEhSE~jfnUZgnpFl~N8wKmgxh7L~KLTjgBW-On~_g3rODJw8z~KUeYMPwpE9~821uj_yCkp~Txs9grkeRc~bDXre79-DK~kffGOewQdf; __utmb=235335808.4.10.1603861680; ki_t=1598279846257%3B1603854572938%3B1603861731118%3B9%3B30',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'
        }
        self.Download_Headers = {
            'accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'referer': 'https://www.pixiv.net/artworks/Host',
            'sec-fetch-dest': 'image',
            'sec-fetch-mode': 'no-cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'
        }
        self.params_1_r18 = {'mode': 'daily_r18'}
        self.params_2_r18 = {'mode': 'daily_r18', 'p': '2', 'format': 'json'}
        self.params_1 = {'mode': 'daily'}
        self.params_2 = {'mode': 'daily', 'p': '2', 'format': 'json'}

        self.pic_id_list = []
        self.pic_url_list = []

    # @retry(stop_max_attempt_number=2, wait_fixed=500) #自动重试3次，间隔0.5秒
    def get_rank(self, r18=False):
        self.state = 200
        print(f'get_rank执行 获取{"r18" if r18 else "常规"}榜单')
        pixiv = httpx.Client(http2=True, verify=False, proxies=self.agency)  # http2模式 get_rank使用独立的session
        params_1 = self.params_1_r18 if r18 else self.params_1
        params_2 = self.params_2_r18 if r18 else self.params_2
        #try:
        #    try:
        response_1 = pixiv.get('https://www.pixiv.net/ranking.php', params=params_1, headers=self.Rank_Headers)
        time.sleep(0.2)  #访问第二页之前停顿下
        response_2 = pixiv.get('https://www.pixiv.net/ranking.php', params=params_2, headers=self.Rank_Headers)
     #   except Exception as e:
     #       self.State = 'get_rank ConnectionError 请求出现错误'
     #       return False       #这里可以直接if判断一下请求结果 来判断是不是有内容的,或者根据state来判断

        print(response_1.status_code, response_2.status_code)

        try:
            rankhtml_1 = response_1.content.decode('utf-8')
            ranknum = re.findall('ranking-item', rankhtml_1)
            # 获取排行名称与id
            rankhtml = etree.HTML(rankhtml_1)
            today_rank = {}
            #rank_id = []
            for n in range(len(ranknum)):
                xpath = f"/html/body/div[@id='wrapper']/div[@class='layout-body']/div[@class='_unit']/div[@class=\
                            'ranking-items-container']/div[@class='ranking-items adjust']/section[{n}]"
                items = rankhtml.xpath(xpath)
                for i in items:
                    pic_name = i.attrib['data-title']
                    pic_user = i.attrib['data-user-name']
                    pic_id = i.attrib['data-id']
                    pic_rank = i.attrib['data-rank-text']
                    #rank_id.append(pic_id)
                    name_id = {f'{pic_rank}' + f' 作品：{pic_name}' + f' 作者：{pic_user}': f'{pic_id}'}
                    self.pic_id_list.append(pic_id)
                    today_rank.update(name_id)     #把第一个页面的榜单加进去
        except Exception:
            today_rank = {}
            self.state = '请求页面1解析出错'
            print(self.state)

        try:
            rankhtml_2 = response_2.content.decode('utf-8')
            #with open('p2.json', 'w') as f:
            #    f.write(rankhtml_2)
            rankhtml_2 = json.loads(rankhtml_2)
            contents = rankhtml_2['contents'] #主字典
            pic_rank = 50
            for rank_item in contents:
                pic_name = rank_item['title']
                pic_user = rank_item['user_name']
                pic_id = rank_item['illust_id']
                pic_rank += 1
                name_id = {f'#{pic_rank}' + f' 作品：{pic_name}' + f' 作者：{pic_user}': f'{pic_id}'}
                self.pic_id_list.append(pic_id)
                today_rank.update(name_id)        #把第二个页面的榜单加进去
        except Exception:
            self.state = '请求页面2解析出错'
            print(self.state)

        if self.debug:
            print(f"请求1:{response_1.status_code}\n请求2:{response_2.status_code}\n模块状态：{self.state}\n请求1正文{response_1.text}\n请求2正文{response_2.text}")
        return today_rank

    def get_url(self, pic_id_range_start=0, pic_id_range_end=10):
        pic_id_list = self.pic_id_list[pic_id_range_start:pic_id_range_end]
        threads = []
        url_list = []

        for ID in pic_id_list:
            #print(ID)
            t = MyThread(target=Pixiv.get_url_single, args=(self, ID,))
            threads.append(t)
        threads_num = len(threads)
        for ti in range(threads_num):
            time.sleep(0.2)  # 线程启动间隔
            threads[ti].start()
            if ti == threads_num - 1:  # 启动所有线程后 监视线程
                time.sleep(0.2)
                Watch = threading.Thread(target=Threads_watchmen, args=(threads,))
                Watch.start()
                Watch.join()
                time.sleep(0.1)  # 完成线程监视，读取返回结果
                for tj in range(threads_num):
                    url_list.append(threads[tj].get_result())  # 可能为False
                print('全部Url请求完成')
                self.pic_url_list = url_list     #给类里面的url_list赋值
                return url_list

    def pic_download(self, download_path = None):         #多线程
        if not self.pic_url_list:
            print('pic_download 多线程下载方法无法获得url，请先get_url获取')
            return False
        if download_path == None:
            print('pic_download下载地址为空')
            return False
        pic_download_url_list = self.pic_url_list
        pic_full_path = []
        pic_num = len(pic_download_url_list)
        threads = []

        for i in range(pic_num):
            t = MyThread(target=Pixiv.pic_download_single, args=(self, download_path, pic_download_url_list[i]))
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

    @retry(stop_max_attempt_number=2, wait_fixed=200) #自动重试两次，停顿0.2秒)
    def pic_download_single(self, download_path: str, pic_url: str):
        if download_path is None or download_path == '' or pic_url is None or pic_url =='':
            print('pic_download_single 输入下载路径或下载链接为空')
            return False
        pic_download_id = re.findall("/(\d{5,12})_", pic_url)[0]      #正则从url里获取一下id  匹配  /85253969_ 样式
        if os.path.isfile(f'{download_path}/{pic_download_id}.jpg') and (os.path.getsize(f'{download_path}/{pic_download_id}.jpg') >= 1000):
            print(f'图片ID{pic_download_id}已存在')
            return f'{download_path}/{pic_download_id}.jpg'  # 返回图片全路径
        else:
            pic = self.pixiv.get(pic_url, headers=self.Download_Headers, timeout=20)
            with open(f'{download_path}/{pic_download_id}.jpg', 'wb') as f:
                f.write(pic.content)
                print(f'图片ID{pic_download_id}下载完成')
                return f'{download_path}/{pic_download_id}.jpg'


    @retry(stop_max_attempt_number=2, wait_fixed=200) #自动重试两次，停顿0.2秒
    def get_url_single(self, pic_id=None): #url 单独 session
        if not pic_id:
            print('get_url_single 输入为空')
            return False
        pic_size = "regular"
        pic_html = self.pixiv.get(f'https://www.pixiv.net/artworks/{pic_id}', headers=self.Url_Headers, timeout=8)
        if pic_html.status_code == '404':
            return False
        pichtml = pic_html.content.decode('utf-8')
        pic_url = str(re.findall('"regular":".*?"', pichtml))
        pic_url = re.sub('"regular":"', '', pic_url)
        pic_url = re.sub('"', '', pic_url)
        pic_url = pic_url.replace("['", '')
        pic_url = pic_url.replace("']", '')
        print(pic_url, 'url获取成功')
        return pic_url



if __name__ == '__main__':
    p = Pixiv()
    a = p.get_rank(r18=True)
    print(p.state)
    b = p.get_url(85, 100)
    print(b)
    c = p.pic_download(r'C:\Users\MSI-PC\Desktop\bmss')
    print(c)