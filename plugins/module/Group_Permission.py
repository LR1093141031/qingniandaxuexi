import os
import json

plugins = ['Pixivtu', 'daxuexi', 'dailychat', 'SauceNaotu', 'TraceMoetu',
           'WebGuide', 'checkin', 'setu']                                # 需要检查的plugins
permission_file_dir = os.path.dirname(__file__) + '/premission.json'     # permission文件位置


class Permission:  # 机器人消息权限控制
    def __init__(self):
        try:                                                            # 尝试读取全局权限文件位置，否则就尝试读本文件目录下的
            self.permission_file_dir = permission_file_dir
        except NameError as e:
            self.permission_file_dir = os.path.dirname(__file__) + '/premission.json'
            print('未发现全局权限文件设置，尝试读取本地')

        if not os.path.isfile(self.permission_file_dir):  # 权限文件不存在，原地创建个新的
            # print('class Permission:权限文件找不到，用update命令更新')
            raise FileNotFoundError('class Permission:权限文件找不到，用update命令更新')

        try:                                               # 权限文件存在，尝试读取
            with open(self.permission_file_dir, 'r', encoding='utf-8') as self.permission_file:
                self.permission_dict = json.load(self.permission_file)
        except Exception as e:
            print('class Permission:权限log读取失败', e)

        self.plugins = plugins  # 这里因为插件做的混乱 所以先写死，后面再全写成类，然后用nonebot读取
        self.group_count = 0

    def permission_check(self, user_id_or_group_id: str, target_plugin: str) -> bool:
        user_id_or_group_id = str(user_id_or_group_id)
        if (user_id_or_group_id is None) or (target_plugin is None):
            raise ValueError('premission_check方法未获得传入群号和查询目标')
        else:
            try:
                return bool(self.permission_dict[user_id_or_group_id][target_plugin])
            except Exception as e:
                print('permission_check:权限读取目标群和插件无法找到', e)

    def permission_set(self, user_id_or_group_id: str, target_plugin: str, enable: bool) -> str:
        user_id_or_group_id = str(user_id_or_group_id)
        if (user_id_or_group_id in self.permission_dict) and (
                target_plugin in self.permission_dict[user_id_or_group_id]):
            _new_dict = {user_id_or_group_id: {target_plugin: 1 if enable else 0}}  # 这里的权限字典更新，传入True设为1，False为0

            self.permission_dict.update(_new_dict)
            self.permission_file_write()
            print(f'{user_id_or_group_id} {target_plugin} 设置为 {enable}')
            return f'{user_id_or_group_id} {target_plugin} 设置为 {enable}'
        else:
            print(f'无法搜索到该权限{user_id_or_group_id} {target_plugin}')
            return f'无法搜索到该权限{user_id_or_group_id} {target_plugin}'

    def permission_file_read(self) -> dict:  # 注意一下这里读的结果，全县部分是str的’bool‘
        # group_list = await self.bot.get_group_list()
        # print(group_list, type(group_list))
        # 这里不做处理，直接返回吧
        return self.permission_dict

    def permission_file_write(self) -> bool:  # 这里仅负责写入文件，不负责更新权限字典了，需要在调用部分更新
        try:
            with open(self.permission_file_dir, 'w') as _permission_file:
                json.dump(self.permission_dict, _permission_file)
        except Exception as e:
            print('permission_file_write:权限文件写入失败', e)
            return False
        return True

