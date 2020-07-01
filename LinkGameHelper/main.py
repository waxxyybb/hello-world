# import torch
import win32.win32gui as win32gui
import win32.win32api as win32api
import win32con
import numpy as np
import cv2

from PIL import Image, ImageGrab

from config import *
from utils import *

if __name__=='__main__':
    if TITLE == '':
        print("请在config中设置连连看游戏窗口名称，eg'此电脑'、'Chrome'")
        raise Exception('游戏窗口名称未设置')

    position = get_position( TITLE)

    screen = get_screen( position)

    images = divide_image( screen, position)

    empty = get_empty( )

    kinds, kinds_dict = get_types( images, empty)

    cnts = get_total_cnt( kinds)

    print( f"总计{cnts}张图片")


    to_stop = 0
    temp = random.randint( 1, 3)

    while cnts > 0:
        for k in kinds_dict:
            if k == 0: continue
            temp_list = kinds_dict[k]
            if not temp_list: continue
            new_list = foo( temp_list, kinds, position)
            if len( temp_list) != len( new_list):
                to_stop += 1
                cnts -= len( temp_list) - len( new_list)
                if DO_SLEEP and to_stop % int( temp * 2) == 0:
                    temp = random.randint( 1, 5)
                    time.sleep( temp)
                time.sleep(1.3)
            kinds_dict[k] = new_list