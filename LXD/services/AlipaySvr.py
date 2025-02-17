import nonebot
from selenium import webdriver
from LXD.services.DBSvr import DB
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiocqhttp.exceptions import ActionFailed
from sqlite3 import IntegrityError
import time
import re
import random


class AlipaySvr:
    browser = None
    username = ""
    __db__ = None
    __scheduler__ = None
    __FirefoxProfile__ = "data/FirefoxProfile"
    __QQbot__ = nonebot.get_bot()
    __mainloop_job__ = None
    __errstatus__ = None

    def __init__(self):
        self.browser = webdriver.Firefox(firefox_profile=self.__FirefoxProfile__)
        # 初始化支付宝网页
        self.browser.get("https://personalweb.alipay.com/portal/i.htm")
        # self.login('18715707081', 'wjd1996')
        self.browser.implicitly_wait(500)
        self.username = self.browser.find_element_by_xpath("//a[@seed='account-zhangh-myalipay-v1']").text  # 检测登录
        print('支付宝 ' + self.username + ' 登录成功！')
        time.sleep(5)  # 别那么快
        entrance = self.browser.find_element_by_xpath("//a[@seed='global-record']")  # 模拟点击跳转记录页
        ActionChains(self.browser).move_to_element(entrance).click(entrance).perform()
        # self.browser.get("https://consumeprod.alipay.com/record/advanced.htm")  # 转到交易记录页
        # 打开数据库
        self.__db__ = DB()
        # 设置定时刷新
        self.__scheduler__ = AsyncIOScheduler()
        self.__mainloop_job__ = self.__scheduler__.add_job(self.mainloop_handler, 'interval', seconds=60)
        self.__scheduler__.start()

    def __del__(self):
        self.browser.quit()

    def login(self, username, password):
        entrance = self.browser.find_element_by_xpath("//li[@data-status='show_login']")
        time.sleep(random.random())
        ActionChains(self.browser).move_to_element_with_offset(entrance, xoffset=random.randint(3, 5),
                                                    yoffset=random.randint(15, 20)).click(entrance).perform()
        userinput = self.browser.find_element_by_xpath("//input[@id='J-input-user']")
        pwdinput = self.browser.find_element_by_xpath("//input[@id='password_rsainput']")
        smt = self.browser.find_element_by_xpath("//input[@id='J-login-btn']")
        time.sleep(random.random())
        ActionChains(self.browser).move_to_element_with_offset(userinput, xoffset=random.randint(3,5),
                                                    yoffset=random.randint(15, 20)).click(userinput).perform()
        time.sleep(random.random())
        userinput.clear()
        time.sleep(random.random())
        userinput.send_keys(username)
        time.sleep(random.random())
        ActionChains(self.browser).move_to_element_with_offset(pwdinput, xoffset=random.randint(3, 5),
                                                    yoffset=random.randint(15, 20)).click(pwdinput).perform()
        time.sleep(random.random())
        pwdinput.clear()
        time.sleep(random.random())
        pwdinput.send_keys(password)
        time.sleep(random.random())
        ActionChains(self.browser).move_to_element_with_offset(smt, xoffset=random.randint(3, 5),
                                                    yoffset=random.randint(15, 20)).click(smt).perform()
        return

    async def mainloop_handler(self):
        time.sleep(random.random())
        # 刷新页面
        if random.choice([True, False]):
            randomtradeno = self.__db__.getRandomAlipayTradeNo()
            self.checkoderid(randomtradeno, 0)
        time.sleep(random.random())
        try:
            entrance = self.browser.find_element_by_xpath("//a[@seed='global-record']")
            ActionChains(self.browser).move_to_element_with_offset(entrance, xoffset=random.randint(3, 5),
                                                        yoffset=random.randint(15, 20)).click(entrance).perform()
            self.__errstatus__ = None
        except NoSuchElementException:
            if not self.__errstatus__:
                try:
                    for uid in [916327225, 1158395892]:
                        await self.__QQbot__.send_private_msg_rate_limited(user_id=uid, message='支付宝出问题了，具体问题已进入排查。')
                except ActionFailed as e:
                    print('酷QHTTP插件错误，返回值：' + repr(e.retcode))
        # self.browser.refresh()
        self.browser.implicitly_wait(5)
        # 判断页面是否正常
        if self.browser.title == '登录 - 支付宝' and self.__errstatus__ != 'NeedLogin':  # 登录失效
            self.__mainloop_job__.pause()
            self.__errstatus__ = 'NeedLogin'
            scrshot = self.browser.get_screenshot_as_base64()
            msg = {
                'type': 'image',
                'data': {
                    'file': 'base64://' + scrshot
                }
            }
            try:
                for uid in [916327225, 1158395892]:
                    await self.__QQbot__.send_private_msg_rate_limited(user_id=uid, message='登录失效，请尽快修复！如果二维码过期，请回复“刷新支付宝页面”。')
                    await self.__QQbot__.send_private_msg_rate_limited(user_id=uid, message=msg)
            except ActionFailed as e:
                print('酷QHTTP插件错误，返回值：' + repr(e.retcode))
            self.__mainloop_job__.resume()
            return
        if self.browser.title == '安全校验 - 支付宝' and self.__errstatus__ != 'NeedConfirm':  # 被风控
            self.__mainloop_job__.pause()
            self.__errstatus__ = 'NeedConfirm'
            scrshot = self.browser.get_screenshot_as_base64()
            msg = {
                'type': 'image',
                'data': {
                    'file': 'base64://' + scrshot
                }
            }
            try:
                for uid in [916327225, 1158395892]:
                    await self.__QQbot__.send_private_msg_rate_limited(user_id=uid, message='需要安全校验，请尽快修复！如果二维码过期，请回复“刷新支付宝页面”。')
                    await self.__QQbot__.send_private_msg_rate_limited(user_id=uid, message=msg)
            except ActionFailed as e:
                print('酷QHTTP插件错误，返回值：' + repr(e.retcode))
            self.__mainloop_job__.resume()
            return
        # 进行review
        if not self.__errstatus__:
            self.review()
        else:
            print('程序依然处于错误状态，请尽快修复！')
            try:
                for uid in [916327225, 1158395892]:
                    await self.__QQbot__.send_private_msg_rate_limited(user_id=uid, message='程序依然处于错误状态，请尽快修复！如果二维码过期，请回复“刷新支付宝页面”。')
            except ActionFailed as e:
                print('酷QHTTP插件错误，返回值：' + repr(e.retcode))

    # 监测订单信息
    def review(self):
        time.sleep(1)
        self.browser.implicitly_wait(10)
        top_tradeNostr = self.browser.find_element_by_xpath("//tr[@id='J-item-1']/td[contains(@class,'tradeNo')]/p").text
        # top_orderno = self.browser.find_element_by_xpath("//a[@id='J-tradeNo-1']").get_attribute('title')
        last_seen_tradeNostr = self.__db__.getvar('Alipay_last_seen_orderno')
        if top_tradeNostr != last_seen_tradeNostr:  # 有新订单
            for item in self.browser.find_elements_by_xpath("//table[@id='tradeRecordsIndex']/tbody/tr"):
                try:
                    memo = item.find_element_by_xpath(".//p[@class='consume-title']/a").text
                except NoSuchElementException:
                    memo = item.find_element_by_xpath(".//p[@class='consume-title']").text
                print(memo)
                tradeNostr = item.find_element_by_xpath("./td[contains(@class,'tradeNo')]/p").text
                print(tradeNostr)
                if last_seen_tradeNostr:
                    if tradeNostr == last_seen_tradeNostr:
                        break
                restr = r"流水号:\d+"
                tradeNO = re.search(restr, tradeNostr)
                if tradeNO:
                    tradeNO = tradeNO.group().strip('流水号:')
                else:
                    continue
                print(tradeNO)
                amount = eval(item.find_element_by_xpath("./td[@class='amount']/span").text)  # 字符串转换
                print(amount)
                amount = int(amount * 100)  # 单位换算
                try:
                    self.__db__.saveAlipayTradeNo({
                        'tradeNo': tradeNO,
                        'memo': memo,
                        'amount': amount
                    })
                except IntegrityError:
                    pass
            print(last_seen_tradeNostr)
            self.__db__.setvar('Alipay_last_seen_orderno', top_tradeNostr)  # 订单检测完成
            return
        else:
            return

    def checkoderid(self, orderid, price):
        WebDriverWait(self.browser, 20, 0.5).until(expected_conditions.title_is, '我的账单 - 支付宝')
        # gotoadvanced = self.browser.find_element_by_xpath("//a[@seed='CR-AdvancedFilter']")
        # gotoadvanced.click()
        inpkwd = self.browser.find_element_by_xpath("//input[@id='J-keyword']")
        btnsubmit = self.browser.find_element_by_xpath("//input[@id='J-set-query-form']")
        ActionChains(self.browser).move_to_element_with_offset(inpkwd, xoffset=random.randint(3, 5),
                                                    yoffset=random.randint(15, 20)).click(inpkwd).perform()
        inpkwd.clear()
        time.sleep(random.random())
        inpkwd.send_keys(orderid)
        ActionChains(self.browser).move_to_element_with_offset(btnsubmit, xoffset=random.randint(3, 5),
                                                    yoffset=random.randint(15, 20)).click(btnsubmit).perform()
        self.browser.implicitly_wait(2)
        try:
            result = self.browser.find_element_by_xpath("//tr[@id='J-item-1']/td[@class='amount']/span").text
        except NoSuchElementException:
            return False
        print(result)
        amount = eval(result)
        if amount >= price:
            return amount
        else:
            return False

