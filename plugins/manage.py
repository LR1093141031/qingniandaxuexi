from nonebot import on_request, RequestSession, on_notice, NoticeSession, on_command, CommandSession, on_startup, \
    get_bot, get_loaded_plugins, default_config, permission
from nonebot.permission import SUPERUSER
import os
import json
import psutil
import re
import subprocess
import time

#  此部分全局量局与Group_Permission相同
plugins = ['Pixivtu', 'daxuexi', 'dailychat', 'SauceNaotu', 'TraceMoetu',
           'WebGuide', 'checkin', 'setu']
permission_file_dir = os.path.dirname(__file__) + '/premission.json'


@on_request('friend')  # 自动添加好友
async def _(session: RequestSession):
    try:
        await session.approve()
    except:
        await session.bot.set_friend_add_request(flag=session.event.flag, approve=True)
    # id = session.event.user_id
    # bot = nonebot.get_bot()
    # msg = f'欢迎11111111111111\n{id}'
    # print(msg)
    # await bot.send_private_msg(user_id=id, message=msg)


@on_notice('group_increase')  # 欢迎群新人
async def _(session: NoticeSession):
    welcome_file_path = os.path.split(os.path.realpath(__file__))[0] + '/data/day'
    path = welcome_file_path + '/welcome.jpg'
    if not os.path.isfile(path):
        print("welcome文件丢失？")
    welcome_message = f"""欢迎新朋友！~\n[CQ:image,file=file:///{path}]"""
    await session.send(welcome_message)


@on_command('list_all_group', permission=SUPERUSER)  # 返回机器人群列表
async def list_all_group(session: CommandSession):
    bot = get_bot()
    group_list = await bot.get_group_list()
    message = ''
    for i in group_list:
        message += f'{i}'
    await session.send(message)


@on_command('superuser')  # 返回机器人群列表
async def superuser(session: CommandSession):
    bot = get_bot()
    superuser_list = list(bot.config.SUPERUSERS)
    _message = ''
    for id in superuser_list:
        _message += f'{id}\n'
    await session.send(_message)


@on_command('update')  # 返回机器人群列表
async def update(session: CommandSession):
    bot = get_bot()
    if session.ctx['user_id'] in bot.config.SUPERUSERS:
        group_list = await bot.get_group_list()
        group_id_list = [str(group['group_id']) for group in group_list]
        group_count = len(group_id_list)
        print(type(group_id_list[0]), group_id_list)

        if not os.path.isfile(permission_file_dir):  # 权限文件不存在，原地创建个新的
            print('尝试原地创建/premission.json')
            permission_json_form = {}
            plugin_permission_form = {}
            for plugin in plugins:
                plugin_permission_form.update({plugin: 0})  # 因为要读取为bool类型，所以这里设置为int型的0和1
            for group_id in group_id_list:
                permission_json_form.update({group_id: plugin_permission_form})
            with open(permission_file_dir, 'w') as permission_file_new:
                json.dump(permission_json_form, permission_file_new)
            print(f'update:权限文件创建完成啦~ 一共发现{group_count}个群组')
            await session.send(f'update:权限文件创建完成啦~ 一共发现{group_count}个群组')

        else:  # 权限文件存在，尝试更新
            group_count_new = 0
            with open(permission_file_dir, 'r') as permission_file_new:
                permission_json_form = json.load(permission_file_new)
            plugin_permission_form = {}
            for group_id in group_id_list:
                if group_id not in permission_json_form:
                    group_count_new += 1
                    for plugin in plugins:
                        plugin_permission_form.update({plugin: 0})  # 因为要读取为bool类型，所以这里设置为int型的0和1
                    permission_json_form.update({group_id: plugin_permission_form})
            with open(permission_file_dir, 'w') as permission_file_new:
                json.dump(permission_json_form, permission_file_new)
            print(f'update:权限文件更新完成啦~ 一共更新{group_count_new}个群组')
            await session.send(f'update:权限文件更新完成啦~ 一共更新{group_count_new}个群组')
    else:
        await session.send('?')


@on_command('reboot')  # QQ客户端重启，进程名必须为rbq 或者RBQ
async def reboot(session: CommandSession):
    bot = get_bot()
    if session.ctx['user_id'] in bot.config.SUPERUSERS:
        print('管理员重启QQ客户端中......')
        pid_list = psutil.process_iter()
        print(pid_list)
        for process in pid_list:
            if process.name() in ['rbq.exe', 'RBQ.exe']:
                await session.send('成功获取QQ客户端进程，尝试重启')
                time.sleep(5)
                print('获取qq客户端进程:', process.name(), process.pid)
                # id = process.pid
                file_path = process.exe()
                process.kill()
                print('完成关闭', file_path)
                subprocess.Popen(args='', executable=file_path, cwd=os.path.dirname(file_path), startupinfo=None,
                                 creationflags=subprocess.CREATE_NEW_CONSOLE)
                # subprocess.Popen(args, bufsize=0, executable=None, \
                #                              stdin=None, stdout=None, stderr=None, \
                #                              preexec_fn=None, close_fds=False, shell=False, \
                #                              cwd=None, env=None, universal_newlines=False,\
                #                              startupinfo=None, creationflags=0)
                print('完成启动')
    else:
        await session.send('?')
