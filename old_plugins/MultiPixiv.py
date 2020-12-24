import threading
import sys
import os
relative_path = os.getcwd().replace(r"\\", r'/') + '/awesome/plugins'
sys.path.append(relative_path)
import Pixiv
import time

#download_path = r'C:/Users/MSI-PC/Desktop/jojo'

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
    #print(threads_num)

    for i in range(threads_num):
        while threads[i].isAlive():
            time.sleep(0.7)  #检查间隔
            continue
        else:
            threads_ack[i] = 1
            #time.sleep(0.3)  #检查间隔
            #threads_ack_chart = ''.join(['+' if i else '-' for i in threads_ack])  #图形化进程
            #print(threads_ack_chart)
            for j in threads_ack:
                threads_done = threads_done + j
            if threads_done == threads_num:
                print('线程监视完成')
                return True
            else:
                threads_done = 0
                pass



def Multi_url(ID_List : list):
    if ID_List == None:
        print('多线程url输入为空')
        return False

    threads = []
    #ID_List_New = []
    Url_List_New = []

    for ID in ID_List:
        t = MyThread(target=Pixiv.Geturl, args=(ID,))
        threads.append(t)

    threads_num = len(threads)

    for ti in range(threads_num):
        time.sleep(0.3)  # 线程启动间隔
        try:
            threads[ti].start()
        except:
            print(f'{ti}Url线程出错')
        if ti == threads_num - 1:  #启动所有线程后 监视线程
            time.sleep(0.2)
            Watch = threading.Thread(target=Threads_watchmen, args=(threads,))
            Watch.start()
            Watch.join()
            time.sleep(0.1)   #完成线程监视，读取返回结果
            for tj in range(threads_num):
                Url_List_New.append(threads[tj].get_result()) #可能为False
            print('全部Url请求完成')
            return Url_List_New
        else:
            pass


def Multi_download(download_path :str, pic_download_id : list, pic_url : list):
    if (download_path == None) or (pic_download_id == None) or (pic_url == None):
        print('输入参数缺失')
        return
    if len(pic_download_id) != len(pic_url):
        print('输入下载url与id不对称，请修改')

    #print(len(pic_download_id), len(pic_url))

    pic_num = len(pic_download_id)
    threads = []
    Pic_Name_New =[False] * pic_num

    for i in range(pic_num):
        t = MyThread(target=Pixiv.PixivDownload, args=(download_path, pic_download_id[i], pic_url[i]))
        threads.append(t)

    threads_num = len(threads)

    for j in range(threads_num):
        time.sleep(0.2)  # 线程启动间隔
        try:
            threads[j].start()
        except:
            print(f'{j}下载线程出错')

        if j == threads_num - 1:  #启动所有线程后 监视线程
            time.sleep(0.2)
            Watch = threading.Thread(target=Threads_watchmen, args=(threads,))
            Watch.start()
            Watch.join()
            time.sleep(0.1)   #完成线程监视，读取返回结果

            for z in range(pic_num):     #完成线程下载，读取结果
                Pic_Name_New[z] = threads[z].get_result() #可能为False

            print('全部下载请求完成')
            return Pic_Name_New
        else:
            pass

'''
ID_List = []
try:
    List = Pixiv.Getrank(r18 = True)
    List = list(List.items())
    for i, j in List:
        ID_List.append(j)
    print(ID_List)
except:
    print('榜单获取失败')

IDs = ID_List[20:35]

UrlList = Multi_url(IDs)
#print(UrlList)
Multi_download(download_path, IDs, UrlList)
'''




'''
            if (False in Url_List_New) or ('请求超时'in Url_List_New): #处理未完成,重试仅一次
                Wrong_count = 0
                Wrong_index = []
                for index, IsthatFalse in enumerate(Url_List_New):
                    if (IsthatFalse == False) or (IsthatFalse == '请求超时'):
                        Wrong_index.append(index)
                        Wrong_count = Wrong_count + 1

                print(Wrong_index)
                print(f'url请求出现{Wrong_count}个错误或超时出现,正在重试中......')

                 threads = [] #重置下线程列表                                          /////不写重试了。太麻烦容易有bug

                for Wrong in Wrong_index:     #Wrong_Index中记录了错误出现序号
                    t0 = MyThread(target=Pixiv.Geturl, args=(ID_List[Wrong],))
                    threads.append(t0)
                for tz in range(len(threads)):
                    time.sleep(0.2)  # 线程启动间隔
                    try:
                        threads[tz].start()
                    except:
                        print(f'{ti}线程出错')
'''



'''
def test():

    for i in range(5):
        print('test ', i)
        time.sleep(1)

def test1():

    for i in range(3):
        print('test1 ', i)
        time.sleep(1)

thread = threading.Thread(target=test)
thread1 = threading.Thread(target=test1())

#thread.setDaemon(True)
#thread1.setDaemon(True)

thread1.start()
#thread1.join()

thread.start()
#thread.join()

for i in range(2):
    print('mainfunction ', i)
    time.sleep(1)

print(thread.isAlive())

'''










'''def main():
    pic_id = '87752722'
    p1 = threading.Thread(target=Pixiv.Geturl, args=(f'{pic_id}',))
    p1.setDaemon(True)
    p1.start()
    p1.join()
    #except Exception:
    #   print('catch that')

if __name__ == '__main__':
    main()'''