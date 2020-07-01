# 连连看游戏的窗口名称,可以从下方工具栏获取
# The name of the LinkGame window
TITLE = '' 

# 单张图片的窗口大小, ( 纵向， 横向)
# The shape of a single image, （ width, height）
SIZE_W, SIZE_H = 27, 31

# 两张图片间的步长 
# The offset between two images
STRIDE_W, STRIDE_H = 4 + SIZE_W, 4 + SIZE_H

# 第一张图距离左上角的像素距离
# The pixels distance from the first image to top-left corner of main window
OFFSET_W, OFFSET_H = 16, 183

# 整个游戏所涉及的图片规模
# The total size of all images, ( rows, columns)
CNT_W, CNT_H = 19, 11

DO_SLEEP = False
DO_SLEEP = True