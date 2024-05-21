import myfunctions
from selenium import webdriver
from requestium import Session
from time import sleep
import configparser
import os.path
import sys
import datetime
from gui_reassing import return_id

settings = configparser.ConfigParser()
settings.read('settings.ini', encoding="utf-8")

err = ''
r_err = ''

data = return_id()
login = data[0]
password = data[1]
n = data[2]
t = data[3]
role = data[5]
user = data[4]

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
# response = s.get(url)
while True:
    if t < 1:
        t = 1
    if data[6]:
        numbers = data[6]
        count = len(numbers)
    else:
        count = len(open('numbers.txt').readlines())
        numbers = open('numbers.txt')

    multy_number = []
    for number in numbers:
        number = number.replace('\n', '')
        multy_number.append(number)
    numbers = myfunctions.num_list(multy_number, n)
    p = 0
    for number in numbers:
        data = {"requestNumbers": number, "role": role, "user": user}
        post = s.post('http://ppoz-service-bal-01.prod.egrn:9001/manager/assign/reassign', json=data)
        print(post.text)
        print(post.status_code)
        if 200 <= post.status_code < 400:
            print('OK')
            # записываем номер пакета в файл
            with open(fname, 'a+') as f:
                for n in number:
                    f.write(n + '\n')
                    p = p + 1
                f.close()
            # сравнение списков переназначенных номеров и отправленных
            if len(number) != len(post.json()['requestNumbers']):
                print('! в запросе ошибок нет, но не все пакеты переназначились !')
                print(f'из {len(number)} пакетов не назначилось {len(post.json()["requestNumbers"])}')
                print(post.json()['requestNumbers'])
                result_not = list(set(number) ^ set(post.json()['requestNumbers']))
                r_err = myfunctions.make_dir('errors')
                not_r_file = f'{r_err}/not_reassing_numbers.txt'
                if os.path.isfile(not_r_file):
                    flag = 'a'
                else:
                    flag = 'w'
                with open(not_r_file, flag) as f:
                    for n in result_not:
                        f.write(n + '\n')
        elif 400 <= post.status_code < 500:
            print('клиентская ошибка')
            err = myfunctions.make_dir('errors')
            err_file = f'{err}/err_numbers.txt'
            if os.path.isfile(err_file):
                flag = 'a'
            else:
                flag = 'w'
            with open(err_file, flag) as f:
                for n in number:
                    f.write(n + '\n')
        elif 500 <= post.status_code < 600:
            print('серверная ошибка')
            err = myfunctions.make_dir('errors')
            err_file = f'{err}/err_numbers.txt'
            if os.path.isfile(err_file):
                flag = 'a'
            else:
                flag = 'w'
            with open(err_file, flag) as f:
                for n in number:
                    f.write(n + '\n')

        print(f'отработано {p} обращений из {count}')
        sleep(t)  # чтоб не приняли за ddos
    print('всё завершено')
    if err:
        input(f'[ВНИМАНИЕ !!!] есть непереназначенные пакеты, проверьте папку {err}')
        myfunctions.explore(err)
        os.startfile(f'{err}\\err_numbers.txt', 'open')
        err = ''
    if r_err:
        input(f'[ВНИМАНИЕ !!!] есть непереназначенные пакеты, проверьте папку {r_err}')
        myfunctions.explore(r_err)
        os.startfile(f'{r_err}\\not_reassing_numbers.txt', 'open')
        r_err = ''
    data = return_id()
    if not data:
        break
    login = data[0]
    password = data[1]
    n = data[2]
    t = data[3]
    role = data[5]
    user = data[4]

browser.quit()
