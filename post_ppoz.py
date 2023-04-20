import myfunctions
from selenium import webdriver
from requestium import Session
from time import sleep
import configparser
import os.path
import sys
import datetime
from gui_login_form import return_id

settings = configparser.ConfigParser()
settings.read('settings.ini', encoding="utf-8")

err = ''

au = return_id()
login = au[0]
password = au[1]

options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
url = 'http://ppoz-service-bal-01.prod.egrn:9001/#/administration'
executable_path = settings['path']['executable_path']
browser = webdriver.Chrome(options=options, executable_path=executable_path)
print('start')
now = datetime.datetime.now().strftime("%d-%m-%Y %H_%M")
ext = 'txt'
d = myfunctions.make_dir('result_logs')
fname = f'{d}\\{now}.{ext}'
work_file = open(fname, "w+")
work_file.close()
s = Session(driver=browser)
s.driver.get(url)
sleep(1)
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
sleep(1)
s.transfer_driver_cookies_to_session()


def get_total_number(dateFrom, dateTo, region, role, department, user, n=50):
    i = 0
    num_on_page = 1
    total = 0
    while num_on_page != 0:
        data = {
          "pageNumber": i,
          "pageSize": n,
          "lastActionDate": {
            "dateFrom": dateFrom,
            "dateTo": dateTo
          },
          "objectRegions": [
            region
          ],
          "subjectRF": [
            region
          ],
          "executorRoles": [
            role
          ],
          "executorDepartments": [
            department
          ],
          "executors": [
            user
          ]
        }

        post = s.post('http://ppoz-service-bal-01.prod.egrn:9001/manager/requests', json=data)
        # print(post.text)
        # print(post.status_code)
        # print(post.json())
        if 200 <= post.status_code < 400:
            print('OK')
            num_on_page = len(post.json()['requests'])
            print(num_on_page)
        total += num_on_page
        i += 1
    return total


number = get_total_number(n=10, dateFrom="2023-03-01", dateTo="2023-03-01", region="72", role="PKURP_REG", department="72.044", user="ealiakhova")
print(number)
