#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
#pyinstaller -F --icon=lesson.ico  newLesson.py --upx-dir
pyinstaller newLesson.spec --upx-dir
'''
import json
import os
import random
import sys
import time
import urllib.request

import cv2
from selenium.common import exceptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class NewLesson(object):
    urlList = []

    def __init__(self):
        if getattr(sys, 'frozen', False):
            BASE_DIR = os.path.dirname(os.path.realpath(sys.executable))
        else:
            BASE_DIR = os.path.dirname(os.path.realpath(__file__))
        # 调试开启
        # BASE_DIR=r'D:\python_code\autoLearning\dist'

        with open(os.path.join(BASE_DIR, "config.json"), 'r') as json_file:
            config = json.load(json_file)
        account = config['account']
        password = config['password']
        lessonUrl = config['lessonUrl']
        self.version = config.get('version', 1)
        self.max_retry_count = config.get('max_retry_count', 30)
        self.chromedriver_port = config.get('chromedriver_port', 9515)

        if account == "" or password == "" or len(lessonUrl) == 0:
            print("配置信息不全，请补充后重新启动")
            time.sleep(3)
            sys.exit(0)

        self.account = account
        self.password = password
        self.lessonUrl = lessonUrl
        chrome_opt = Options()  # 创建参数设置对象.
        chromeDriverPath = os.path.join(BASE_DIR, 'chromedriver.exe')
        chrome_opt.add_argument('--headless')  # 无界面化.
        chrome_opt.add_argument('--disable-gpu')  # 配合上面的无界面化.
        chrome_opt.binary_location = os.path.join(BASE_DIR, 'Application', 'chrome.exe')
        chrome_opt.add_argument('--window-size=1920,1080')  # 设置窗口大小, 窗口大小会有影响.
        chrome_opt.add_argument("--mute-audio")  # 静音
        chrome_opt.add_experimental_option("excludeSwitches", ["enable-logging"])  # 禁止日志打印
        driver = ChromeDriver(
            service=Service(chromeDriverPath, port=self.chromedriver_port),
            options=chrome_opt
        )
        self.driver = driver

        # self.driver.get("https://xuexi.yunxuetang.cn/kng/#/course/play?kngId=3ebfc6b5-9271-4e45-a190-1184013c7f39&projectId=&btid=&gwnlUrl=&locateshare=5d7b4f2c-7f70-4f44-8541-6234e759cb99")

    def login(self):
        self.driver.get("https://xuexi.yunxuetang.cn/login.html")
        print(f"--------------当前软件版本：{self.version}")
        print("--------------打开登录页面")

        wait = WebDriverWait(self.driver, 20)

        # 先等待并点击“账号登录”按钮的 button 节点（避免点到不可点击的 span）
        try:
            tab_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[1]/div[1]/div/div/div[3]/button[1]")))
            self.driver.execute_script("arguments[0].scrollIntoView(true);", tab_btn)
            self.driver.execute_script("arguments[0].click();", tab_btn)
        except exceptions.TimeoutException:
            pass

        time.sleep(1)

        # 等待两个输入框渲染（你的页面两个都叫 username 时）
        inputs = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//*[@name='username']")))
        if len(inputs) < 2:
            try:
                u = wait.until(EC.presence_of_element_located((By.NAME, "username")))
                p = wait.until(EC.presence_of_element_located((By.NAME, "password")))
                inputs = [u, p]
            except exceptions.TimeoutException:
                print("--------------登录输入框未渲染，无法定位到用户名和密码输入框")
                print("--------------程序即将退出，请检查网络连接或稍后重试")
                self.driver.quit()
                time.sleep(3)
                sys.exit(1)

        try:
            inputs[0].clear()
            inputs[0].send_keys(self.account)
            inputs[1].clear()
            inputs[1].send_keys(self.password)
        except Exception as e:
            print(f"--------------输入用户名密码失败：{str(e)}")
            print("--------------程序即将退出，请检查配置文件中的账号密码")
            self.driver.quit()
            time.sleep(3)
            sys.exit(1)

        # 勾选协议（保持原 XPath，做等待与 JS 点击）
        try:
            agree = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "/html/body/div[2]/div[1]/div[1]/div/div/div[2]/div[3]/label/span[1]/span/span")))
            self.driver.execute_script("arguments[0].click();", agree)
        except exceptions.TimeoutException:
            print("--------------未找到协议勾选框，跳过此步骤")

        # 点击登录按钮（保持原 XPath，失败时兜底到 submit 或"登录"文本）
        try:
            login_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[1]/div[1]/div/div/div[2]/button")))
            self.driver.execute_script("arguments[0].click();", login_btn)
        except exceptions.TimeoutException:
            try:
                login_btn = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' or normalize-space()='登录']")))
                self.driver.execute_script("arguments[0].click();", login_btn)
            except exceptions.TimeoutException:
                print("--------------未找到登录按钮，页面结构可能已变更")
                print("--------------程序即将退出，请联系开发者更新")
                self.driver.quit()
                time.sleep(3)
                sys.exit(1)

        print("--------------开始登录")
        self.driver.implicitly_wait(5)
        if self.iselement('tcaptcha-iframe'):
            print('切换滑动验证进行识别')
            # 此时需要切换到弹出的滑块区域，需要切换frame窗口
            self.driver.switch_to.frame("tcaptcha_iframe")

            WebDriverWait(self.driver, 8).until(EC.visibility_of_element_located((By.ID, 'slideBg')))
            # 获取滑块验证图片下载路径，并下载到本地
            bigImage = self.driver.find_element(By.ID, "slideBg")
            bigImageSrc = bigImage.get_attribute("src")  # 获取图片的style属性
            # 下载图片至本地
            urllib.request.urlretrieve(bigImageSrc, 'bigImage.png')

            # 计算缺口图像的x轴位置
            dis = self.get_pos('bigImage.png')
            # 获取小滑块元素，并移动它到上面的位置
            smallImage = self.driver.find_element(By.XPATH, '//*[@id="tcaptcha_drag_thumb"]')
            # 小滑块到目标区域的移动距离（缺口坐标的水平坐标距离小滑块的水平坐标相减的差）
            # 新缺口坐标=原缺口坐标*新画布宽度/原画布宽度
            newDis = int(dis * 340 / 672 - smallImage.location['x'])
            self.driver.implicitly_wait(5)  # 使用浏览器隐式等待5秒
            # 按下小滑块按钮不动
            ActionChains(self.driver).click_and_hold(smallImage).perform()
            # 移动小滑块，模拟人的操作，一次次移动一点点
            i = 0
            moved = 0
            while moved < newDis:
                x = random.randint(3, 10)  # 每次移动3到10像素
                moved += x
                ActionChains(self.driver).move_by_offset(xoffset=x, yoffset=0).perform()
                print("第{}次移动后，位置为{}".format(i, smallImage.location['x']))
                i += 1
            # 移动完之后，松开鼠标
            ActionChains(self.driver).release().perform()
            # 整体等待5秒看结果
            time.sleep(3)

    def get_pos(self, imageSrc):
        # 读取图像文件并返回一个image数组表示的图像对象
        image = cv2.imread(imageSrc)
        # GaussianBlur方法进行图像模糊化/降噪操作。
        # 它基于高斯函数（也称为正态分布）创建一个卷积核（或称为滤波器），该卷积核应用于图像上的每个像素点。
        blurred = cv2.GaussianBlur(image, (5, 5), 0, 0)
        # Canny方法进行图像边缘检测
        # image: 输入的单通道灰度图像。
        # threshold1: 第一个阈值，用于边缘链接。一般设置为较小的值。
        # threshold2: 第二个阈值，用于边缘链接和强边缘的筛选。一般设置为较大的值
        canny = cv2.Canny(blurred, 0, 100)  # 轮廓
        # findContours方法用于检测图像中的轮廓,并返回一个包含所有检测到轮廓的列表。
        # contours(可选): 输出的轮廓列表。每个轮廓都表示为一个点集。
        # hierarchy(可选): 输出的轮廓层次结构信息。它描述了轮廓之间的关系，例如父子关系等。
        contours, hierarchy = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # 遍历检测到的所有轮廓的列表
        for contour in contours:
            # contourArea方法用于计算轮廓的面积
            area = cv2.contourArea(contour)
            # arcLength方法用于计算轮廓的周长或弧长
            length = cv2.arcLength(contour, True)
            # 如果检测区域面积在5025-7225之间，周长在300-380之间，则是目标区域
            if 5025 < area < 7225 and 300 < length < 380:
                # 计算轮廓的边界矩形，得到坐标和宽高
                # x, y: 边界矩形左上角点的坐标。
                # w, h: 边界矩形的宽度和高度。
                x, y, w, h = cv2.boundingRect(contour)
                print("计算出目标区域的坐标及宽高：", x, y, w, h)
                # 在目标区域上画一个红框看看效果
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.imwrite("111.jpg", image)
                return x
        return 0

    def read2(self):
        if self.iselement('yxtf-image__inner'):
            print('-------------------登录成功')
        else:
            print('-------------------登录失败')
            self.driver.quit()
            return

        # 手工更换地址
        for lession in self.lessonUrl:
            cnt = 0
            print(lession)
            # 获取所有课程列表
            self.driver.get(lession)
            time.sleep(3)
            # 如果为多课程
            if self.iselement('flex-space-between'):
                # 读取课程开始遍历
                # self.driver.find_elements_by_class_name("flex-space-between")[0].click()
                if self.iselement('yxtf-button--larger'):
                    if len(self.find_elements_by_class("yxtf-button--larger")) == 2:
                        self.click_class_element("yxtf-button--larger", 1)
                    else:
                        self.click_class_element("yxtf-button--larger", 0)
                    time.sleep(3)
                time.sleep(3)
                # 获取进程，如果没有进程则要开始跳到下一课程
                process = ''
                while process == '':
                    if self.iselement('yxt-color-warning'):
                        process = self.driver.find_element(By.CLASS_NAME, "yxt-color-warning").text
                        break
                    if self.iselement('yxtf-button--default'):
                        moved = self.try_next_lesson()
                        if not moved:
                            print("当前链接疑似已全部完成，停止继续跳转")
                            break
                        print("已学完，跳到下一个")
                        cnt += 1
                    else:
                        break
                    # self.driver.find_elements_by_class_name("yxtf-icon-arrow-right")[0].click()
                    # print(process)
                # 课程数量
                # ml8=self.driver.find_element_by_class_name("ml8").text
                if self.iselement('yxt-color-warning') is False:
                    if self.iselement('yxtf-button--larger'):
                        if len(self.find_elements_by_class("yxtf-button--larger")) == 2:
                            self.click_class_element("yxtf-button--larger", 1)
                        else:
                            self.click_class_element("yxtf-button--larger", 0)
                        time.sleep(2)
                # process=eval(self.driver.find_element_by_class_name("opacity8").text.replace('已完成 ',''))
                # 到第几页
                while process != '':
                    # if process*cnt
                    time.sleep(10)
                    # if self.iselement('is-plain'):
                    #     break
                    if self.iselement('yxt-color-warning'):
                        process = self.driver.find_element(By.CLASS_NAME, "yxt-color-warning").text
                    if self.iselement('yxtf-button--large'):
                        # print("跳过超时限制")
                        # self.driver.find_elements_by_class_name("yxtf-button--large")[0].click()
                        element = self.driver.find_element(By.CLASS_NAME, "yxtf-button--large")
                        action = ActionChains(self.driver)
                        action.move_to_element(element)
                        action.send_keys("Enter")
                    if self.iselement("yxt-color-warning"):
                        print("当前课程剩余时间:" + self.driver.find_element(By.CLASS_NAME, "yxt-color-warning").text)
                    else:
                        moved = self.try_next_lesson()
                        if not moved:
                            print("当前链接疑似已全部完成，停止继续跳转")
                            break
                        print("已学完，跳到下一个")
                        cnt += 1
                        # 超过30次则跳过
                        if cnt > self.max_retry_count:
                            break
            else:
                ml8 = self.driver.find_element(By.CLASS_NAME, "ml8").text
                if ml8 == "已完成学习":
                    continue
                process = eval(
                    self.driver.find_element(By.CLASS_NAME, "opacity8").text.replace('已完成 ', '').replace('%', ''))
                while process < 100:
                    # if process*cnt
                    time.sleep(5)
                    # if self.iselement('is-plain'):
                    #     break
                    process = eval(
                        self.driver.find_element(By.CLASS_NAME, "opacity8").text.replace('已完成 ', '').replace('%',
                                                                                                                ''))
                    if self.iselement('yxtf-button--larger'):
                        print("执行播放")
                        self.click_class_element("yxtf-button--larger", 0)
                        time.sleep(2)
                    if self.iselement('yxtf-button--large'):
                        print("跳过超时限制")
                        element = self.driver.find_element(By.CLASS_NAME, "yxtf-button--large")
                        action = ActionChains(self.driver)
                        action.move_to_element(element)
                        action.send_keys("Enter")
                        time.sleep(2)
                    if self.iselement("yxt-color-warning"):
                        print("课程进度:" + str(
                            round(process * 100, 2)) + "%,当前课程剩余时间:" + self.driver.find_element(By.CLASS_NAME,
                                                                                                        "yxt-color-warning").text)
                    else:
                        break
                        # for item in self.driver.find_elements_by_class_name("ulcdsdk-break-word"):
                        #     if item.text=='下一个':
                        #         print("跳转下一个视频")
                        #         item.click()
                        #         break
        print("课程结束")
        self.driver.quit()

    def iselement(self, classname):
        try:
            self.driver.find_element(By.CLASS_NAME, classname)
            return True
        except exceptions.NoSuchElementException:
            return False

    def find_elements_by_class(self, classname):
        return self.driver.find_elements(By.CLASS_NAME, classname)

    def get_page_signature(self):
        parts = [self.driver.current_url]
        for classname in ("ml8", "opacity8", "yxt-color-warning"):
            elements = self.find_elements_by_class(classname)
            if elements:
                parts.append(f"{classname}:{elements[0].text.strip()}")
        return "|".join(parts)

    def click_class_element(self, classname, index=0):
        elements = self.find_elements_by_class(classname)
        if len(elements) <= index:
            raise exceptions.NoSuchElementException(
                f"class={classname} 的元素数量不足，无法点击索引 {index}"
            )

        element = elements[index]
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        try:
            element.click()
        except exceptions.ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", element)

    def try_next_lesson(self):
        if len(self.find_elements_by_class("yxtf-button--default")) <= 1:
            return False

        before = self.get_page_signature()
        self.click_class_element("yxtf-button--default", 1)
        time.sleep(5)
        after = self.get_page_signature()
        return before != after


if __name__ == '__main__':
    n = NewLesson()
    n.login()
    n.read2()
