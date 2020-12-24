from PIL import Image
import os
import numpy as np
import json
#from nonebot import on_command, CommandSession
import time
import requests


def pixel_rgb_change(pixel : int, add : int, white : bool):
    if white:
        pixel = pixel + add
        if pixel > 255:
            pixel = 255
            return pixel
        else:
            return pixel
    else:
        pixel = pixel - add
        if pixel < 0:
            pixel = 0
            return pixel
        else:
            return pixel





def anti_yellow_md5pic(path :str , picture :str ): #反tx鉴黄改图模块函数
    div_num = [6, 10] #图像分割线条数
    sub_div_num = 4 #图像分割线条粗细比例
    white_enable = False #是否启用白色线条
    color_div = 170 #色差设置

    if os.path.getsize(f'{path}/{picture}') <= 1000:
        print(f'{picture}未完成下载')
        return False
    else:
        try:
            img = Image.open(f'{path}/{picture}')
            img = img.convert('RGB')
            (width, height) = img.size[0] , img.size[1]

            if width > height:
                main_div_num = div_num[0]
            else:
                main_div_num = div_num[1]

            main_div_height = int(height/main_div_num)
            sub_div_height = int(main_div_height/sub_div_num)
            h = 0
            for i in range(main_div_num): #线条数量
                h = h + sub_div_height * (sub_div_num - 1) #高度初始值
                if 0 <= h <= (height - sub_div_height): #判断图像边界，防止超出
                    for j in range(sub_div_height): #循环改该宽度像素
                        for w in range(width): #循环改高度内像素
                            pixel = img.getpixel((w, h+j))

                            pixel_new = [0, 0, 0]

                            pixel_new[0] = pixel_rgb_change(pixel[0], color_div, white_enable)
                            pixel_new[1] = pixel_rgb_change(pixel[1], color_div, white_enable)
                            pixel_new[2] = pixel_rgb_change(pixel[2], color_div, white_enable)

                            img.putpixel((w, h+j), (pixel_new[0], pixel_new[1], pixel_new[2]))

                h = h + sub_div_height

            img.save(f'{path}/{picture}')
        except:
            print(f"反tx改图失败,{picture}改图失败")
            return False


        print(f"完成反tx改图,{picture}完成改图")
        return True


#anti_yellow_md5pic(r'C:\Users\MSI-PC\Desktop\qq机器人', 'img.jpg')

