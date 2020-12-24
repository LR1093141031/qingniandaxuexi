import os
import json
import time
from nonebot import on_command, CommandSession

check_in_file = os.path.split(os.path.realpath(__file__))[0] + '/checkin_log.json'


@on_command('checkin', aliases=['签到', '每日签到', '打卡'],  only_to_me=False)  # qq机器人用
async def checkin(session: CommandSession):  # qq机器人用命令体
    log = check_in_log(check_in_file)
    checkin_data = log.read()

    user_id = str(session.ctx['user_id'])
    try:
        name = session.ctx['sender']['card'] if 'card' in session.ctx['sender'] else session.ctx['sender']['nickname']
    except Exception as e:
        print("无法获取name", e)
        return
    signature = session.state['signature']    # 个性签名 不输入就是空字符串
    if len(signature) > 100:                             # 判断下是不是过长了
        signature = ''                                   # 太长了就强行弄成空的
        await session.send('哇，太长了吧......RBQ经受不住')

    time_now = time.localtime()[:5]

    if user_id not in checkin_data:          # 无记录 则新增记录
        log_new = {user_id: {"time_all": 1, "continuing": 0, "signature": f"{signature}", "last_time": [time_now[0], time_now[1], time_now[2], time_now[3], time_now[4]]}}  # 年月日时分
        checkin_data.update(log_new)
        await session.send(f"""✿博梦神社✿\n{name} 金光闪闪第一次打卡""")
        log.save(checkin_data)

    else:
        if user_id in checkin_data:           # 有记录
            last_time = checkin_data[user_id]['last_time']
            if signature != '':                                 # 这里逻辑神tm诡异难懂
                checkin_data[user_id]['signature'] = signature       # 如果签名更新的话 就写入保存下
                log.save(checkin_data)

            else:
                signature = checkin_data[user_id]['signature']       # 没有就读取旧的

            time_log = last_time[0]*10000 + last_time[1]*100 + last_time[2]  # 比较用的int型时间 判断到天为止，是否有记录
            time_now_int = time_now[0]*10000 + time_now[1]*100 + time_now[2]

            if time_log == time_now_int:                                   # 今日已打卡,且有记录 就不写文件保存了
                if signature != '':
                    await session.send(f"""✿博梦神社✿\n{name} 主人今日已经留下印记了呢~{checkin_data[user_id]["time_all"]}\n{signature}""")
                else:
                    await session.send(f"""✿博梦神社✿\n{name} 您今日已经完成打卡\n打卡总数{checkin_data[user_id]["time_all"]}""")

            if time_log < time_now_int:                                   # 今日未打卡，且有记录
                checkin_data[user_id]["time_all"] += 1  # 总数+1
                checkin_data[user_id]["last_time"] = time_now  # 年月日时分 更新下时间
                log.save(checkin_data)  # 保存下文件

                if signature != '':
                    await session.send(f"""✿博梦神社✿\n{name} 印记更新成功！{checkin_data[user_id]["time_all"]}\n{signature}""")
                else:
                    await session.send(f"""✿博梦神社✿\n{name} 今日打卡成功\n打卡总数{checkin_data[user_id]["time_all"]}""")


@checkin.args_parser  # qq机器人用命令解析器
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    session.state['signature'] = session.current_arg_text.strip()
    # print(session.state['signature'])


class check_in_log():                                            # log文件操作
    def __init__(self, file_path=None):
        # file_name = 'checkin_log.json'
        # file_dir1 = os.getcwd().replace('\\', '/') + f'/{file_name}' # nonebot目录
        # file_dir2 = os.getcwd().replace('\\', '/') + f'/awesome/plugins/{file_name}'
        if not file_path:
            print("忘了传入log文件目录了？")
            return
        self.file_path = file_path if os.path.isfile(file_path) else None
        if not self.file_path:
            raise FileNotFoundError('check in log文件丢失无法找到或未传入')
        else:
            print('log文件已存在', self.file_path)

    def read(self):                   # 读取
        try:
            with open(self.file_path, 'r', encoding='utf-8') as checkin_file:
                checkin_data = json.load(checkin_file)
        except Exception as e:
            print('chek in log读取失败', "目标位置:", self.file_path, e)
        return checkin_data

    def save(self, json_data=None):                   # 写入
        if json_data:
            checkin_data = json_data
        else:
            raise Exception('checkinlog.save方法需要传入json')
        try:
            with open(self.file_path, 'w', encoding='utf-8') as checkin_file:
                json.dump(checkin_data, checkin_file)
                print('checkinlog完成写入')
        except Exception as e:
            print('chekinlog写入失败', "目标位置:", self.file_path, e)
