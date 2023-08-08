import json
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from time import sleep
import myfunctions
import configparser
import os.path
import datetime
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from gui_login_form import return_id

settings = configparser.ConfigParser()
settings.read('settings.ini', encoding="utf-8")

au = return_id()
login = au[0]
password = au[1]
#########
now = datetime.datetime.now().strftime("%d-%m-%Y %H_%M")
ext = 'txt'
d = myfunctions.make_dir('result_logs')
fname = f'{d}\\{now}.{ext}'
work_file = open(fname, "w")
work_file.close()

options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
try:
    options.add_extension('extension_1_2_8_0.crx')
except:
    print('не установлены расширения браузера')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

executable_path = settings['path']['executable_path']
browser = webdriver.Chrome(options=options, executable_path=executable_path)


def check_login(url):
    if "ВОЙТИ" in browser.page_source:
        print("страница логина")
        myfunctions.logon(url, browser, login, password)
        sleep(1)

    if browser.current_url != url:
        print(browser.current_url)
        print("Что-то пошло не так ((")
        # browser.get(url)
        sleep(5)
        if browser.current_url != url:
            print(browser.current_url)
            print("Походу не работает сайт ((")
            sys.exit()
        elif "ВОЙТИ" in browser.page_source:
            print("страница логина")
            myfunctions.logon(url, browser, login, password)


# url = 'http://pkurp-app-balancer-01.prod.egrn/requests?filter=mine'
def logon(url):
    browser.get(url)
    try:
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/div/main/div/section/article/div/form/div/div[3]/div[3]/button"))
        )
    except:
        print("не вижу кнопки ВОЙТИ !!")
    check_login(url)

    try:
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "table"))
        )
    except:
        print("не загрузилась страница !!")


def first(sved_page):
    browser.get(sved_page)
    try:
        element = WebDriverWait(browser, 300).until(
            EC.presence_of_element_located((By.CLASS_NAME, "scroll-x"))
        )
    except:
        print("страници Сведения не загрузилась !!")
        if 'Сервис проверки прав доступа недоступен. Обратитесь к администратору' in browser.page_source:
            first(sved_page)


def check_manu_objects(txt):
    try:
        browser.find_element(By.LINK_TEXT, txt)
    except NoSuchElementException:
        return False
    return True


if __name__ == '__main__':
    logon('http://pkurp-app-balancer-01.prod.egrn/requests?filter=mine')
