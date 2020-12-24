from PIL import Image
import os
import random


def md5pic(full_path :str):
    a = random.randint(0, 254)
    b = random.randint(0, 254)
    c = random.randint(0, 254)
    if not os.path.isfile(full_path):
        print("md5未输入全路径")
        return False
    picture_name = os.path.basename(full_path)
    if os.path.getsize(full_path) <= 1000:
        print(f'{picture_name}未完成下载')
        return True
    else:
        try:
            img = Image.open(f'{full_path}')
            img = img.convert('RGB')
            img.putpixel((0, 0), (a, b, c))
            img.save(f'{full_path}')
            print(f'{picture_name}完成改图')
        except Exception as e:
            print("md5部分改图失败", e)
            return False
        return True


