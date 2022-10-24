from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
import random
import time
from selenium.webdriver import ActionChains
from captcha import RotateCaptcha
from urllib.parse import quote


import requests

base_url = 'https://wappass.baidu.com/static/captcha/tuxing.html?ak=2ef521ec36290baed33d66de9b16f625&backurl=http%3A%2F%2Ftieba.baidu.com%2F&timestamp=1655176222&signature=7166d8dcec4ed272e5d84314de53e574'
headers = {
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
}


class my_web():
    def __init__(self):
        self.base_url = 'https://aiqicha.baidu.com/'
        # 初始化slenium
        options = Options()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        self.driver = webdriver.Chrome(executable_path= "D:/AppData/ccr_project/chromedriver.exe", options=options)

    def __ease_out_expo(self,sep):
        if sep == 1:
            return 1
        else:
            return 1 - pow(2, -10 * sep)

    def generate_tracks(self, distance):
        """
        根据滑动距离生成滑动轨迹
        :param distance: 需要滑动的距离
        :return: 滑动轨迹<type 'list'>: [[x,y,t], ...]
            x: 已滑动的横向距离
            y: 已滑动的纵向距离, 除起点外, 均为0
            t: 滑动过程消耗的时间, 单位: 毫秒
        """
        distance = int(distance)
        if not isinstance(distance, int) or distance < 0:
            raise ValueError(f"distance类型必须是大于等于0的整数: distance: {distance}, type: {type(distance)}")
        # 初始化轨迹列表
        slide_track = [
            # [random.randint(-50, -10), random.randint(-50, -10), 0],
            [0, 0, 0],
        ]
        # 共记录count次滑块位置信息
        count = 30 + int(distance / 2)
        # 初始化滑动时间
        t = random.randint(50, 100)
        # 记录上一次滑动的距离
        _x = 0
        _y = 0
        for i in range(count):
            # 已滑动的横向距离
            x = round(self.__ease_out_expo(i / count) * distance)
            # 滑动过程消耗的时间
            t += random.randint(10, 20)
            if x == _x:
                continue
            slide_track.append([x, _y, t])
            _x = x
        slide_track.append(slide_track[-1])
        return slide_track

    def download_img(self):
        img_url = self.driver.find_elements(By.XPATH, '//*[@class="vcode-spin-img"]')[0].get_attribute("src")
        r = requests.get(img_url)
        time.sleep(random.randint(70,100)/100)
        with open('img.jpg', 'wb') as f:
            f.write(r.content)
        rotateCaptcha = RotateCaptcha()
        rotated_image = rotateCaptcha.getImgFromDisk('./img.jpg')
        return rotateCaptcha,rotated_image

    def main(self):
        #1.发起请求
        while 1:
            # key_word = random.choice(COMPANY)
            # #企业信息cookies
            # url = self.base_url + 's?q=' + quote(key_word)
            url = base_url
            #商标信息cookie接口
            # url = 'https://aiqicha.baidu.com/mark/s?q={}'.format(quote(key_word))
            self.driver.get(url)
            time.sleep(1)
            #2.判断是否出现滑块(进入while循环中，直到滑块过了才出来)
            flag = self.driver.find_elements(By.XPATH,'//*[contains(text(),"请完成下方验证后继续操作")]')
            while flag:
                # global rotateCaptcha,rotated_image
                success_download_img = True
                while success_download_img:
                    try:
                        rotateCaptcha, rotated_image = self.download_img()
                        break
                    except:
                        self.driver.refresh()

                result = rotateCaptcha.predictAngle(rotated_image)
                displacement_distance = 212 / 360 * int(result)
                print('预测旋转角度为：', result, '滑动距离为：', displacement_distance)
                source = self.driver.find_element(By.XPATH, r'//*[@class="vcode-spin-button"]/p')
                action = ActionChains(self.driver, duration=10)
                action.click_and_hold(source).perform()
                a = 0
                for x in self.generate_tracks(displacement_distance):
                    action.move_by_offset(xoffset=x[0] - a, yoffset=x[1])
                    a = x[0]

                action.release(source).perform()
                time.sleep(2)
                # if key_word in self.driver.page_source:
                #     break
                break
            #3.返回cookies
            cookie_list = self.driver.get_cookies()
            return cookie_list

if __name__ == '__main__':
    cookie_list = my_web().main()
    cookies_dict = {cookie['name']: cookie['value'] for cookie in cookie_list}
    print(cookies_dict)