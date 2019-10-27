# -*- coding:utf-8 -*-

import sys
import os
import cv2 as cv
import numpy as np
import subprocess
import time
import math

base_dir = "E:/codeLearn/adbController/"
recognize_dir = "E:/codeLearn/adbController/recognizeTemplate/"
tmpSnapshot_dir = "E:/codeLearn/adbController/tmpSnapshot/"
cv_recognize_method = cv.TM_SQDIFF_NORMED
def init():
    # 删除临时文件（删除本目录下所有缓存的截图文件）
    for root, dirs, files in os.walk(tmpSnapshot_dir):
        for file in files:
            deleteFile = root+"/"+file
            print("wait delete temp file is "+deleteFile)
            if os.path.exists(deleteFile):
                os.remove(deleteFile)

# 保存截图
def saveSnaphot(filename):
    snapshotFile = tmpSnapshot_dir+str(filename)+".png"
    process = subprocess.Popen('adb shell screencap -p', shell=True, stdout=subprocess.PIPE)
    screenshot = process.stdout.read()
    binary_screenshot = screenshot.replace(b'\r\n', b'\n')
    f = open(snapshotFile, 'wb')
    f.write(binary_screenshot)
    f.close()



# 检测可点击的按键像素点列表
def checkButtonPixListToClick(target):
    ret = []
    targetFile = tmpSnapshot_dir+str(target)+".png"
    target = cv.imread(targetFile)
    for root, dirs, files in os.walk(recognize_dir):
        for file in files:
            tpfile = root + file
            tpl = cv.imread(tpfile)
            # 模板图片1，2 tw x轴 ，th y轴
            th, tw = tpl.shape[:2]
            result = cv.matchTemplate(target, tpl, cv_recognize_method)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
            print(min_val, max_val, min_loc, max_loc )
            # min_loc 是cv.TM_SQDIFF_NORMED 左上角的点
            # 添加中心点坐标
            if(min_val < 0.000001):
                ret.append((min_loc[0] + tw/2, min_loc[1] + th/2))
    return ret


# 主流程
if __name__ == '__main__':
    # 初始化
    init()

    # 打开手机淘宝
    process = subprocess.Popen('adb shell am start -n com.taobao.taobao/com.taobao.tao.TBMainActivity activity', shell=True)
    time.sleep(5.0)
    saveSnaphot("home")
    pixList = checkButtonPixListToClick("home")
    if len(pixList)<=0:
        print("主页未匹配")
    # do someting 进行我们的操作
    # 点击像素点（1249，247） 打开猫币活动
    process = subprocess.Popen('adb shell input tap %f %f' % (pixList[0][0], pixList[0][1]), shell=True)
    time.sleep(5.0)
    # 点击像素点（1221，2319） 打开猫币活动
    saveSnaphot("active")
    pixList = checkButtonPixListToClick("active")
    if len(pixList)<=0:
        print("活动页未匹配")
    process = subprocess.Popen('adb shell input tap %f %f' % (pixList[0][0], pixList[0][1]), shell=True)
    time.sleep(5.0)

    # 看广告起始像素点位置 （1210，2460） 从下向上递减250
    count = 0
    while 1:
        saveSnaphot(count)
        time.sleep(1.0)
        pixList = checkButtonPixListToClick(count)
        if (len(pixList)<=0):
            print("无可点击活动按钮 退出~~~")
            break
        # 当是最后一个广告的时候
        process = subprocess.Popen('adb shell input tap %f %f' % (pixList[0][0], pixList[0][1]), shell=True)
        # 等待观看广告完成
        time.sleep(35.0)
        # 返回
        process = subprocess.Popen('adb shell input keyevent KEYCODE_BACK', shell=True)
        time.sleep(3.0)
        print('have seen ' + str(count+1) + ' advertise')
        count += 1

    print(sys.stdout, "ALL AD HAVE SEEN!!")
    sys.exit(1)






