import torch
import win32.win32gui as win32gui
import win32.win32api as win32api
import win32con
import numpy as np
import pickle as pk
import collections
import cv2
import time
import random

from PIL import Image, ImageGrab

from config import *


def get_position( title = TITLE):
    window =  win32gui.FindWindow( None, title)
    if window is None:
        print("Wrong!")
        raise Exception("Cannot get the position")

    win32gui.SetForegroundWindow( window)
    position = win32gui.GetWindowRect( window)
    print(f"Get the {title} positon at {position}")
    return position[0], position[1]

def get_screen( position):

    pic = ImageGrab.grab()
    screen = np.asarray( pic)

    # pic.save( '1.jpg')
    # with open('screen', 'wb') as fout:
    #     pk.dump( ( screen, position) , fout)

    return screen


def divide_image( screen, position):
    print( screen.shape)
    ans = [ [0] * CNT_W for _ in range( CNT_H)]

    x = position[1] + OFFSET_H
    for i in range( CNT_H):
        y = position[0] + OFFSET_W
        for j in range( CNT_W):
            ans[i][j] = screen[ x : x + SIZE_H , y : y + SIZE_W]
            y += STRIDE_W
        x += STRIDE_H
    return ans


def images_same( p1, p2, tail = 5):
    p1 = p1[tail:-tail, tail:-tail]
    p2 = p2[tail:-tail, tail:-tail]
    diff = cv2.subtract( p1, p2)
    return not diff.any()

def get_empty():
    fr = open('empty','rb')
    empty = pk.load( fr)
    fr.close()
    return empty


def get_types( images, empty):
    type_dict = collections.defaultdict( list)
    container = [empty]
    ans =[ [-1] * ( CNT_W) for _ in range( CNT_H) ]
    for i in range( CNT_H):
        for j in range( CNT_W):
            for k, image in enumerate( container):
                if images_same( images[i][j], image) == True:
                    ans[i][j] = k
                    break
            if ans[i][j] == -1:
                ans[i][j] = len( container)
                container.append( images[i][j])
            type_dict[ans[i][j]].append( (i,j))
    return ans, type_dict



def can_combine( p1, p2, kinds):
    x1, y1 = p1
    x2, y2 = p2


    sign = [ [ False] * CNT_W  for _ in range( CNT_H) ]
    sign[x1][y1] = True
    sign[x2][y2] = True

    def _foo( x, y):
        for i in range( x - 1, -1, -1):
            if kinds[i][y] != 0: break
            sign[i][y] = True
        for i in range( x + 1, CNT_H):
            if kinds[i][y] != 0: break
            sign[i][y] = True

        for j in range( y + 1, CNT_W):
            if kinds[x][j] != 0: break
            sign[x][j] = True
        for j in range( y - 1, -1, -1):
            if kinds[x][j] != 0: break
            sign[x][j] = True

    _foo( x1, y1)
    _foo( x2, y2)
    
    if x1 != x2:
        for j in range( CNT_W):
            if j == y1 or j == y2: continue
            if sign[x1][j] == True and sign[x2][j] == True:
                can = True
                for i in range( min(x1,x2) + 1, max( x1,x2) ):
                    if kinds[i][j] != 0:
                        can = False
                        break
                if can == True: 
                    # print(f"j = {j},纵向联通横向")
                    return True
    else:
        can = True
        if y1 < y2: it = range( y1 + 1, y2)
        else: it = range( y2 + 1, y1)
        for j in it:
            if kinds[x1][j] != 0:
                can = False
                break
        if can == True:
            # print("直接横向联通")
            return True
    

    if y1 != y2:
        for i in range( CNT_H):
            if i == x1 or i == x2: continue
            if sign[i][y1] == True and sign[i][y2] == True:
                can = True
                for j in range( min( y1, y2) + 1, max( y1, y2)):
                    if kinds[i][j] != 0:
                        can = False
                        break
                if can == True: 
                    # print(f"i = {i},横向联通总线")
                    return True
    else:
        can = True
        if x1 < x2: it = range( x1 + 1, x2)
        else: it = range( x2 + 1, x1)
        for i in it:
            if kinds[i][y1] != 0:
                can = False
                break
        if can == True:
            # print("直接纵向联通")
            return True   

    can = True
    if y1 < y2: it = range( y1 + 1, y2 + 1)
    else: it = range( y2, y1)
    for j in it:
        if kinds[x1][j] != 0:
            can = False
            break
    if x1 < x2: it = range( x1, x2)
    else: it = range( x2 + 1, x1 + 1)
    for i in it:
        if kinds[i][y2] != 0:
            can = False
            break
    if can == True:
        # print(f"通过{x1},{y1}->{x1},{y2}->{x2},{y2}")
        return True

    can = True
    if y1 < y2: it = range( y1 , y2 )
    else: it = range( y2 + 1, y1 + 1)
    for j in it:
        if kinds[x2][j] != 0:
            can = False
            break
    if x1 < x2: it = range( x1 + 1, x2 + 1)
    else: it = range( x2 , x1)
    for i in it:
        if kinds[i][y1] != 0:
            can = False
            break
    if can == True:
        # print(f"通过{x1},{y1}->{x2},{y1}->{x2},{y2}")
        return True

    
    return False

def get_total_cnt( kinds):
    ans = 0
    for item in kinds:
        for t in item:
            if t != 0:
                ans += 1
    return ans



def click( index, position):
    x, y = index
    new_x = ( x + 1 //2) * STRIDE_H + OFFSET_H + position[1]
    new_y = ( y + 1 //2) * STRIDE_W + OFFSET_W + position[0]

    win32api.SetCursorPos(( new_y, new_x))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, new_y, new_x, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, new_y, new_x, 0, 0)

def foo( temp_list, kinds, position):
    length = len( temp_list)
    for i in range( length):
        p1 = temp_list[i]
        for j in range( i + 1,length):
            p2 = temp_list[j]
            if can_combine( p1, p2, kinds):
                click( p1, position)
                click( p2, position)
                kinds[p1[0]][p1[1]] = 0
                kinds[p2[0]][p2[1]] = 0
                print(f"联通 {p1}\t{p2}")
                return [ item for k,item in enumerate( temp_list) if k != i and k != j]
    return temp_list