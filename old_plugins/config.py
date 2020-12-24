import os
import sys
import re
import json




'''def config(div1 = None, div2 = None, trans_file_url = None):

    path = os.getcwd().replace('\\', '/')  #nonebot目录

    if div1 == None:
        print('config无基础类参数输入')
        return False

    try:                                               #判断下当前目录在哪吧 给不加载情况下调用config
        if os.path.isfile(f'{path}/config.json'):
            #print(f'{path}/config.json')
            with open(f'{path}/config.json', 'r', encoding='utf-8') as config_file:
                config_data = json.load(config_file)

        else:
            path = path +'/awesome/plugins'
            if os.path.isfile(f'{path}/config.json'):
                #print(f'{path}/config.json')
                with open(f'{path}/config.json', 'r', encoding='utf-8') as config_file:
                    config_data = json.load(config_file)

    except:
        print('config文件读取失败')
        return False

    #print('config读取成功')

    if div1 == 'CQcode':            #CQcode转换
        if div2 == None:
            print("config-CQcode div2 未指定内容")
            return False
        else:
            if div2 in config_data['CQcode']:
                data = config_data[div1][div2]

                if trans_file_url == None:
                    print('config未输入需转换file或url')
                    return False
                else:
                    data = data.replace('<what_remains>', str(trans_file_url))
                    #print('config_CQcode转换成功', data)
                    return data
            else:
                print("config无对应CQcode")
                return False

    else:                         #路径获取 这里是相对的 相对config.py路径
        if div1 in config_data:
            if div2 == None:
                print('config-path div2未指定内容')
                return False
            else:
                if div2 in config_data[div1]:
                    data = path + config_data[div1][div2]
                    #print('config_path转换成功', data)
                    return data
                else:
                    print('config-path div2 不存在')
                    return False
        else:
            print('config-path div1 不存在')
            return False
'''

#config('setu', 'download_path', 'www.www.jpg')