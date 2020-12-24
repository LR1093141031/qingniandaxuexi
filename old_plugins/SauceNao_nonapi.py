#import base64
import requests
import os
#import time
#import json
import re
from lxml import etree
from requests_toolbelt import MultipartEncoder
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from urllib3 import encode_multipart_formdata

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

Sauce = requests.session()

def SauceNao(full_path : str):  #这里要全路径
    #open(r'C:\Users\MSI-PC\Desktop\jojo\82736110.jpg', 'rb')
    if full_path == None or full_path == '':
        print('saucenao模块输入为空')
        return False

    file_name = os.path.basename(full_path)
    print(f'搜索图片名称:{file_name}')

    #try:
    m = MultipartEncoder(fields={"file": (f"{file_name}", open(full_path, 'rb'), "image/jpeg")}, boundary='----WebKitFormBoundaryHu0TGdaAI2Jd0Cau')          # 关键构建
    print(m, m.content_type)




    headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Cookie': '_ga=GA1.2.2001450287.1595473234; __gads=ID=c4d3be65848f62f0:T=1595473262:S=ALNI_MYpmtkq8iPlKECawsIehYZpaAboWA; __cfd\
    uid=daf2d5de3062e28287dfcff06af7ca00b1595473268; __utma=4212273.2001450287.1595473234.1595473740.1595473740.1; __utmc=4212273; \
    __utmz=4212273.1595473740.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _gid=GA1.2.1318296899.1595987422; token=5f213b662b\
    67e; user=41078; auth=c85f9c103368c2204042d99330245ef5742e2a60; _gat=1',
    'Content-Type': m.content_type,    # 关键参数
    'Host': 'saucenao.com',
    'Origin': 'https://saucenao.com'
    }
    #file = {"file": ("82713740.jpg", open(r'C:\Users\MSI-PC\Desktop\jojo\82736110.jpg', 'rb').read(), "image/jpeg")}
    response = Sauce.post('https://saucenao.com/search.php', data=m, headers=headers, stream=True, verify=False, timeout=20)
    print(response)
    #except:
     #   print("Saucenao请求出错，请重试")
      #  return ['NetworkError'], ['NetworkError'], ['NetworkError'], ['NetworkError']

    search_html = response.content.decode('utf-8', errors='ignore')     # 解码
    print(response.content)
    print(search_html)

    match_num = len(re.findall('resultimage', search_html)) #判断下有几个结果
    suspect_num = len(re.findall('result hidden', search_html))
    match_num = match_num - suspect_num
    print(f'寻找到{match_num}个匹配对象')

    if match_num == 0:
        print("无匹配对象")
        return [], [], [], []

    search_html = etree.HTML(search_html)               #etree化，做html解析

    #sauce小logo
    #smallloge_xpath = f"/html/body/div[@id='mainarea']/div[@id='middle']/div[@id='smalllogo']/img"  # /html/body/div[2]/div[3]/div[1]/img
    #smallloge_url = search_html.xpath(smallloge_xpath)[0].attrib['src']
    #smallloge_url = 'https://saucenao.com/' + smallloge_url
    #print(f'saucelogo url:{smallloge_url}')

    #页面内容主体
    #middle_xpath = r"/html/body/div[@id='mainarea']/div[@id='middle']"
    #middle_area = search_html.xpath(middle_xpath)
    #返回结果(全部)
    #result_path = r"/html/body/div[@id='mainarea']/div[@id='middle']/div[@class='result']"#f"/html/body/div[@id='mainarea']/div[@id='middle']/div[@class='result']/table[@class='resulttable']/tbody/tr"
    #result_html = search_html.xpath(result_path)
    #对返回结果迭代解析
    #print(f'当前返回结果主div分区{middle_area[0].attrib}')

    img_url = []        #匹配图片url
    for i in range(match_num):   #没办法 不能用相对xpath嵌套，就只好这样 获取匹配图片
        n = i + 2
        img_xpath = f"/html/body/div[2]/div[3]/div[{n}]/table/tr/td[1]/div/a/img"
        img_html = search_html.xpath(img_xpath)
        #print(img_html)
        for j in img_html:
            #print(j.get('src'))
            img_url.append(j.get('src'))
    print(img_url)

    correct_rate =[]     #匹配图片正确率
    for i in range(match_num):
        n =i + 2
        corr_xpath = f"/html/body/div[2]/div[3]/div[{n}]/table/tr/td[2]/div[1]/div[1]"
        corr_html = search_html.xpath(corr_xpath)
        #print(corr_html)
        for j in corr_html:
            #print(j.text)
            correct_rate.append(j.text)
    print(correct_rate)

    result_title = []     #结果标题
    for i in range(match_num):
        n = i + 2
        title_xpath = f"/html/body/div[2]/div[3]/div[{n}]/table/tr/td[2]/div[2]/div[1]"
        title_html = search_html.xpath(title_xpath)
        #print(title_html)

        result_title.append('')

        for j in title_html[0]:
            #print(j)
            if j.text != None:
                result_title[i] = result_title[i] + j.text + ' '

        title0_xpath = f"/html/body/div[2]/div[3]/div[{n}]/table/tr/td[2]/div[2]/div[1]/text()"
        title0_html = search_html.xpath(title0_xpath)
        #print(title0_html)
        if len(title0_html):
            result_title[i] = result_title[i] + title0_html[0]

    print(result_title)


    result_content = []      #搜索结果副内容
    for i in range(match_num):
        n = i + 2
        result_content_xpath = f"/html/body/div[2]/div[3]/div[{n}]/table/tr/td[2]/div[2]/div[2]"
        result_content_html = search_html.xpath(result_content_xpath)

        result_content0_xpath = f"/html/body/div[2]/div[3]/div[{n}]/table/tr/td[2]/div[2]/div[2]/text()"
        result_content0_html = search_html.xpath(result_content0_xpath)

        result_content.append('')      #提前先加个空字符串

        for j in result_content_html[0]:
            #print(j.text, type(j.text))
            if j.text != None:
                result_content[i] = result_content[i] + j.text + ' '

        if len(result_content0_html):
            result_content[i] = result_content[i] + result_content0_html[0] + ' '
    print(result_content)

    return img_url, correct_rate, result_title, result_content







def SauceNao_Download(download_path : str,  pic_url : str):  #单线程  这个模块只下载jog...  pic_download_id : str,
        #图片下载
        print("=====================", pic_url)
        host = pic_url.split('/')[2]
        try:
            pic_download_id = re.findall(r".*/(.*?\.jpg)", pic_url, flags=0)[0]
        except Exception as e:
            pic_download_id = re.findall(r"\d{5,15}", pic_url)[0] + r'.jpg'

        if pic_download_id is None:
            print('Sauce下载模块获取图片id失败')
            return False
        print(f'Sauce下载模块获取图片id:{pic_download_id}')

        pic_download_head =  {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': '_ga=GA1.2.2001450287.1595473234; __gads=ID=c4d3be65848f62f0:T=1595473262:S=ALNI_MYpmtkq8iPlKECawsIehYZpaAboWA; __cfd\
        uid=daf2d5de3062e28287dfcff06af7ca00b1595473268; __utma=4212273.2001450287.1595473234.1595473740.1595473740.1; __utmc=4212273; \
        __utmz=4212273.1595473740.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _gid=GA1.2.1318296899.1595987422; token=5f213b662b\
        67e; user=41078; auth=c85f9c103368c2204042d99330245ef5742e2a60; _gat=1',
        'Host': f'{host}',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'        }

        #(Rob, fix) = os.path.splitext(pic_url) #分离后缀名
        #print('图片格式', fix)

        if os.path.isfile(f'{download_path}/{pic_download_id}') and (os.path.getsize(f'{download_path}/{pic_download_id}') >= 10):
                print(f'图片ID{pic_download_id}已存在')
                return f'{download_path}/{pic_download_id}'   #返回图片名称
        else:

                try:
                        pic = Sauce.get(pic_url, headers=pic_download_head, stream=True, verify=False, timeout=10)
                except requests.exceptions.ConnectTimeout:
                        #PixivDownload(pic_download_id, pic_url)
                        print('Connection超时报错=======================')
                        return '下载超时'
                except requests.exceptions.ConnectionError: #下载超时抛错
                        #PixivDownload(pic_download_id, pic_url)
                        print('Connection错误报错 目标===================')
                        return '下载超时'

                        #print(pic.headers)

                with open(f'{download_path}/{pic_download_id}', 'wb') as f:
                        f.write(pic.content)
                        print(f'图片ID{pic_download_id}下载完成')
                        return f'{download_path}/{pic_download_id}'




def Tx_Download(download_path: str,  pic_url: str):  # Tx聊天图单线程 pic_download_id : str,
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

    # (Rob, fix) = os.path.splitext(pic_url) #分离后缀名
    # print('图片格式', fix)

    try:
        pic = Sauce.get(pic_url, headers=pic_download_head, stream=True, verify=False, timeout=20)
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



if __name__ == '__main__':
    result = SauceNao(r"C:\Users\MSI-PC\Desktop\bmss\['85243326'].jpg")
    print(result)

