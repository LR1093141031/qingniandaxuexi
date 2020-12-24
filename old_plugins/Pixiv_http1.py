import requests
import os
import time
import json
import re
from lxml import etree
from hyper.contrib import HTTP20Adapter
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning) #关报错

pixiv = requests.session()

path = r'./pixiv'
#download_path = r'C:/Users/MSI-PC/Desktop/jojo'

def Getrank(r18 = False):
        rank_head = {
                ':authority': 'www.pixiv.net',
                ':method': 'GET',
                ':path': '/ranking.php?mode=daily_r18',
                ':scheme': 'https',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'cookie': 'p_ab_id=0; p_ab_id_2=3; p_ab_d_id=1345951712; first_visit_datetime_pc=2020-03-20+19%3A19%3A11; yuid_b=GHkRhoI; a_type=0; b_type=2; __utmc=235335808; _fbp=fb.1.1598279801128.774244369; _ga=GA1.2.664530923.1594351285; PHPSESSID=27199888_FvQ8jCKtr8yhZmFicCTsvQYSmmeJLmUe; c_type=21; privacy_policy_agreement=2; ki_r=; login_ever=yes; adr_id=AXzxrLrFF26gi7DXdUi5HO235YoWcrDgilnfD4BIGa26i9w0; __utmz=235335808.1599704607.5.3.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __cfduid=d3c8315391bd2f1fed55b0b566bd087201601435540; ki_s=; __utma=235335808.664530923.1594351285.1601696209.1602767130.8; categorized_tags=6sZKldb07K~8Vlr9rDUAd~AT6ypFBMnT~Ig5OcZugU6~OEXgaiEbRa~OT-C6ubi9i~_bee-JX46i~aLBjcKpvWL~b8b4-hqot7~jYnWl04aAC~xg1UenZfbd; tags_sended=1; first_visit_datetime=2020-10-15+22%3A08%3A39; webp_available=1; __utmv=235335808.|2=login%20ever=yes=1^3=plan=normal=1^5=gender=female=1^6=user_id=27199888=1^9=p_ab_id=0=1^10=p_ab_id_2=3=1^11=lang=zh=1^20=webp_available=yes=1; limited_ads=%7B%22responsive%22%3A%22%22%2C%22t_header%22%3A%22%22%7D; __adpon_uid=c36696e1-eead-42aa-9bc2-b9bc15090198; _gid=GA1.2.1489244657.1602767992; tag_view_ranking=liM64qjhwQ~0xsDLqCEW6~JwOnNobdvo~CmIov8_f5j~CZnOKinv48~_YQZKxAGgg~TAE-gr5obV~uvBGOtCzqF~xe8_207kqj~zZZn32I7eS~3gc3uGrU1V~RTJMXD26Ak~xXhq3SGORQ~rxNSXJvQUh~dD3787FF73~cbmDKjZf9z~mIBxNOpKNs~d8fHMcEG3R~VIOKa7rioU~pNtQi6YIt-~-sp-9oh8uv~jYnWl04aAC~0rFsG_VyY9~KN7uxuR89w~5oPIfUbtd6~TWrozby2UO~8Vlr9rDUAd~xi1_CfbLI5~W7cVeVEFxJ~zhidwuyCQH~qtVr8SCFs5~WVrsHleeCL~-k4xbUv_zd~MM6RXH_rlN~GWJojdnBMY~JM99SoMFHa~jrclGyQTmB~lRHALpj_iJ~aLBjcKpvWL~fUS-Ay2M9Z~I2lfHE5kDb~Me5rTOmxXm~FgYArp6riX~MkgAbGkXH6~QqOL4vbk6n~jH0uD88V6F~6n5sWl9nNm~WPlzUoQVT7~DpO7Lofslr~cwLG8ks7Vj~TptCt3Vpq6~OBJrLjuGCM~qSrf3MWq5h~N8wKmgxh7L~KLTjgBW-On~_g3rODJw8z~KUeYMPwpE9~821uj_yCkp~Txs9grkeRc~bDXre79-DK~kffGOewQdf~TZUoZ8Dws9~jvjiJrlzjm~Ar4oQTjv_h~KB3wNuihPi~yvELB8t0gh~B0g2JuW38N~vMp-NoNmIL~NsbQEogeyL~VPNwFrrT5B~fjusYzDstX~lVtXNTbHwc~8PQySawYFv~VqqXyMy80A~qHQdncSkNX~q3eUobDMJW~DADQycFGB0~48VzExzvzQ~Q37dF1fIOY~y5sdaIG8mR~aKhT3n4RHZ~RthHN5LPvq~Bd2L9ZBE8q~8p2ehmu0sL~jkcivN39wT~TmJBC3K3bw~qWFr0Atl5X~faHcYIP1U0~gpglyfLkWs~sqGkVxMuMR~0KPRxmAt2Y~HPUdhjStR6~djzzAJsMWw~1WbOIM4PU9~mhnCHVwap8~1D1VEfvFR5~UgKpepT-dC~xg1UenZfbd~M8DuQl4sDv~XhOHJMaDOw; __utmt=1; ki_t=1598279846257%3B1602767327005%3B1602769175966%3B4%3B10; __cf_bm=496c0b76689073415a3be7f3018a414c2ed23de2-1602769267-1800-AX5ONyChpZhFGFoqaoTDt9ytrHJu/4Q2aqJk60Ubh1IYY1WUnleKD7q3kssuiz0XLrb3H5eb0qILzTbgZE8mj77F4IQ6u/Z6tTz9tTOJB8BlfQaKwQeXjg/6bIaIvVhQkIqOkoewBSDL+of+DT28gHFoECUds8dI6cXBwpAkfJRpUrB73ke1qjsF4aFIuFJAIA==; __utmb=235335808.9.10.1602767130',
                'referer': 'https://www.pixiv.net/ranking.php',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'
                }

        if (r18 == False) or (r18 == None):  # 是否为r18模式
                payload = {'mode': 'daily'}
        else:
                payload = {'mode': 'daily_r18'}
        try:

                pixiv.mount('https://www.pixiv.net/ranking.php?mode=daily_r18', HTTP20Adapter())
                r = pixiv.get("https://www.pixiv.net/ranking.php", params=payload, headers=rank_head, verify=False, stream = True, timeout = 8)
        except TimeoutError:
                return '请求超时'

        print(r.headers) #头部

        #re获取排行榜总数
        rankhtml = r.content.decode('utf-8')
        #print(rankhtml)
        ranknum = re.findall('ranking-item', rankhtml)
        #print(len(ranknum))

        #获取排行名称与id
        rankhtml = etree.HTML(rankhtml)
        today_rank = {}
        rank_id = []

        for n in range(len(ranknum)):
                xpath = f"/html/body/div[@id='wrapper']/div[@class='layout-body']/div[@class='_unit']/div[@class=\
                'ranking-items-container']/div[@class='ranking-items adjust']/section[{n}]"
                items = rankhtml.xpath(xpath)
                for i in items:
                        pic_name = i.attrib['data-title']
                        pic_user = i.attrib['data-user-name']
                        pic_id = i.attrib['data-id']
                        pic_rank = i.attrib['data-rank-text']#.replace('#','')
                        rank_id.append(pic_id)
                        name_id = {f'{pic_rank}' + f' 作品：{pic_name}'+f' 作者：{pic_user}' : pic_id}
                        today_rank.update(name_id)
        if (r18 == False) or (r18 == None):
                print('今日常规榜单获取成功')
        else:
                print('今日r18榜单获取成功')
        #print(today_rank)
        return today_rank


def Geturl(pic_download_id : str):
        url_head = {
                'Accept': 'text/html, application/xhtml+xml, application/xml; q=0.9, */*; q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN',
                'Connection': 'Keep-Alive',
                'Cookie': '__utmc=235335808; device_token=fd24789890b15db2a636a2ac22e45fff; __utmz=235335808.1586085125.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); login_bc=1; __utma=235335808.236072563.1586085125.1586085125.1590712428.2; privacy_policy_agreement=2; p_ab_d_id=1415587418; b_type=2; __utmb=235335808.6.10.1590712428; _gid=GA1.2.158047712.1590712445; __utmv=235335808.|2=login%20ever=yes=1^3=plan=normal=1^5=gender=female=1^6=user_id=27199888=1^9=p_ab_id=3=1^10=p_ab_id_2=2=1^11=lang=zh=1; c_type=21; _ga=GA1.2.236072563.1586085125; a_type=0; PHPSESSID=27199888_09mufYdjuRiM3YEJLMNdy7Rc4UUQMyMn; p_ab_id_2=2; p_ab_id=3; login_ever=yes; ki_t=1590712487785%3B1590712487785%3B1590712487785%3B1%3B1; ki_r=; first_visit_datetime_pc=2020-04-05+20%3A11%3A57; yuid_b=EWUiUBE',
                'Host': 'www.pixiv.net',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36}'

        }
        #图片网页
        try:
                p = pixiv.get(f'https://www.pixiv.net/artworks/{pic_download_id}', headers = url_head, verify=False, stream = True, timeout = 8)
                if p.status_code == 404:         #404不算是链接异常
                        print('--------------------404-------------------')
                        return '404'
        except requests.exceptions.ReadTimeout:
                print('----------------------请求超时-----------------------')
                return'请求超时'
        except requests.exceptions.InvalidURL:
                print('----------------------无效url------------------------')
                return '无效URL'
        else:
                #print(p.headers)
                #print(p.content)
                pichtml = p.content.decode('utf-8')
                #print(pichtml)
                pic_url = str(re.findall('"regular":".*?"', pichtml))
                pic_url = re.sub('"regular":"', '',  pic_url)
                pic_url = re.sub('"', '',  pic_url)
                pic_url = pic_url.replace("['", '')
                pic_url = pic_url.replace("']", '')
                print(pic_url, 'url获取成功')
                return pic_url


def PixivDownload(download_path : str, pic_download_id : str, pic_url : str):
        #图片下载

        pic_download_head = {
                'Accept': 'image/png, image/svg+xml, image/*; q=0.8, */*; q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN',
                'Connection': 'Keep-Alive',  #keep-alive
                #'Cookies':'__utmc=235335808; device_token=fd24789890b15db2a636a2ac22e45fff; __utmz=235335808.1586085125.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); login_bc=1; __utma=235335808.236072563.1586085125.1586085125.1590712428.2; privacy_policy_agreement=2; p_ab_d_id=1415587418; b_type=2; __utmb=235335808.6.10.1590712428; _gid=GA1.2.158047712.1590712445; __utmv=235335808.|2=login%20ever=yes=1^3=plan=normal=1^5=gender=female=1^6=user_id=27199888=1^9=p_ab_id=3=1^10=p_ab_id_2=2=1^11=lang=zh=1; c_type=21; _ga=GA1.2.236072563.1586085125; a_type=0; PHPSESSID=27199888_09mufYdjuRiM3YEJLMNdy7Rc4UUQMyMn; p_ab_id_2=2; p_ab_id=3; login_ever=yes; ki_t=1590712487785%3B1590712487785%3B1590712487785%3B1%3B1; ki_r=; first_visit_datetime_pc=2020-04-05+20%3A11%3A57; yuid_b=EWUiUBE',
                'Host': 'i.pximg.net',
                #'Upgrade - Insecure - Requests': '1',
                'Referer': f'https://www.pixiv.net/artworks/{pic_download_id}',
                #'Sec-Fetch-Mode': 'no-cors',
                #'Sec-Fetch-Site': 'cross-site',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        }

        #(Rob, fix) = os.path.splitext(pic_url) #分离后缀名
        #print('图片格式', fix)

        if os.path.isfile(f'{download_path}/{pic_download_id}.jpg') and (os.path.getsize(f'{download_path}/{pic_download_id}.jpg') >= 1000):
                print(f'图片ID{pic_download_id}已存在')
                return f'{pic_download_id}.jpg'   #返回图片名称
        else:
                if (pic_url == False) or (pic_url == '请求超时'):
                        return False


                try:
                        pic = pixiv.get(pic_url, headers = pic_download_head, stream = True, verify = False, timeout = 20)
                except requests.exceptions.ConnectTimeout:
                        #PixivDownload(pic_download_id, pic_url)
                        print('Connection超时报错=======================')
                        return '下载超时'
                except requests.exceptions.ConnectionError: #下载超时抛错
                        #PixivDownload(pic_download_id, pic_url)
                        print('Connection错误报错 目标===================')
                        return '下载超时'

                        #print(pic.headers)

                with open(f'{download_path}/{pic_download_id}.jpg', 'wb') as f:
                        f.write(pic.content)
                        print(f'图片ID{pic_download_id}下载完成')
                        return f'{pic_download_id}.jpg'



rank = Getrank(r18=True)
print(rank)
#pic_download_id = '80229295'
#url = Geturl(pic_download_id)
#PixivDownload(pic_download_id, url)



'''
def __login(username: str, password:str):
    session = requests.session()
    head = {
        'accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'content-type': 'application/x-www-form-urlencoded',
        'Host': 'accounts.pixiv.net',
        'Origin': 'https://accounts.pixiv.net',
        'Referer': 'https://accounts.pixiv.net/login?return_to=https%3A%2F%2Fwww.pixiv.net%2F&lang=zh&source=pc&view_type=page',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    }

    key_response = session.get('https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index', verify=False)
    print(key_response.headers)
    post_key = re.findall('<input type="hidden" name="post_key" value=".*?">',
                          key_response.text)[0]
    post_key = re.findall('value=".*?"', post_key)[0]
    post_key = re.sub('value="', '', post_key)
    post_key = re.sub('"', '', post_key)
    print(post_key)
    # 将传入的参数用字典的形式表示出来，return_to可以去掉
    data = {
        'pixiv_id': username,
        'password': password,
        'return_to': 'https://www.pixiv.net/',
        'post_key': post_key,
        'ref': 'wwwtop_accounts_index',
        #'captcha': '',
        #'g_recaptcha_response': '',
        'source': 'pc',
        #'ref': ''
    }

    # 将data post给登录页面，完成登录
    log = session.post("https://accounts.pixiv.net/api/login?lang=zh", headers=head, data=data,  verify=False)
    print(log.content)
    return session

loginsession = __login('1093141031@qq.com', 'lr8864846')

'''
