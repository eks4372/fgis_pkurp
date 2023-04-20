import sys
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import myfunctions
import configparser
import os.path
import datetime
import shutil
from gui_login_form import return_id
from xml_reader import xml_parser
from orm import add_ban

settings = configparser.ConfigParser()
settings.read('settings.ini', encoding="utf-8")
merge = settings['sort']['merge']
serch = settings['sort']['serch']
y = ['y', 'yes', 'д', 'да', 'ага']

au = return_id()
login = au[0]
password = au[1]
#########
path_ban = myfunctions.make_dir(settings['path']['ban'])
path_unban = myfunctions.make_dir(settings['path']['uban'])
if os.listdir(path_ban):
    a = input(f'[ВНИМАНИЕ !] папка {path_ban} не пуста, очистить ?: ')
    if a.lower() in y:
        shutil.rmtree(path_ban)
        path_ban = myfunctions.make_dir(settings['path']['ban'])
if os.listdir(path_unban):
    a = input(f'[ВНИМАНИЕ !] папка {path_unban} не пуста, очистить ?: ')
    if a.lower() in y:
        shutil.rmtree(path_unban)
        path_unban = myfunctions.make_dir(settings['path']['uban'])

now = datetime.datetime.now().strftime("%d-%m-%Y %H_%M")
ext = 'json'
fname_j = f'{now}.{ext}'

url = 'http://ppoz-service-bal-01.prod.egrn:9001/#/administration'

options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

executable_path = settings['path']['executable_path']
browser = webdriver.Chrome(options=options, executable_path=executable_path)

count = len(open('numbers.txt').readlines())
numbers = open('numbers.txt')
p = 0
errors = ''
browser.get(url)
try:
    element = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "/html/body/div/main/div/section/article/div/form/div/div[3]/div[3]/button"))
    )
except:
    print("не вижу кнопки ВОЙТИ !!")
if "ВОЙТИ" in browser.page_source:
    print("страница логина")
    myfunctions.logon(url, browser, login, password)
    sleep(1)

if browser.current_url != url:
    print(browser.current_url)
    print("Что-то пошло не так ((")
    sleep(5)
    if browser.current_url != url:
        print(browser.current_url)
        print("Походу не работает сайт ((")
        sys.exit()
    elif "ВОЙТИ" in browser.page_source:
        print("страница логина")
        myfunctions.logon(url, browser, login, password)
for number in numbers:
    number = number.replace('\n', '')
    number = number.replace(' ', '')
    preurl = 'http://ppoz-service-bal-01.prod.egrn:9001/#/administration/details/'
    posturl = '/docs'
    url = f'{preurl}{number}{posturl}'
    print(url)
    browser.get(url)
    browser.refresh()

    try:
        element = WebDriverWait(browser, 120).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "*[class^='link selected-item']"))
        )
    except:
        print("не вижу номера обращения на странице !!")
        if '502 Bad Gateway' in browser.page_source:
            browser.refresh()
    obr = (browser.find_element(By.CSS_SELECTOR, "*[class^='link selected-item']").text).rsplit('№', 2)
    obr = obr[1]
    print(obr)
    #   проверка загрузки нужной страницы текущего обращения
    if obr != number:
        print('не та страница !!')
        browser.quit()
    row = browser.find_elements(By.CLASS_NAME, 'row-data')
    for r in row:
        if r.text == 'Постановление (выписка) из ФССП.xml':
            link_xml = r.find_element(By.CLASS_NAME, 'col-icon').find_element(By.TAG_NAME, 'a').get_attribute('href')

    print(link_xml)


    def take_data_from_xml(i=1):
        try:
            d = xml_parser(link_xml)
            return d
        except :
            i += 1
            print(f'не удалось загрузить xml, попытка {i}')
            if i < 4:
                return take_data_from_xml(i)


    data = take_data_from_xml()
    print(data)
    # записываем в файл
    ext = 'json'
    if data[0] == 'O_IP_ACT_BAN_REG':
        path = path_ban
    elif data[0] == 'O_IP_ACT_ENDBAN_REG':
        path = path_unban
    # path = "n_obr"
    fname = f'{path}\\{number}.{ext}'

    to_json = {
        number: {'Вид постановления': data[0], 'ФИО': data[1], 'идентификатор': data[2], '№ постановления': data[3],
                 'код подразделения': data[4], 'уникальный ид': data[5], 'кадастровый номер': data[6]
            , 'номер регистрации': data[7], 'вид права': data[9], 'ИНН': data[8], 'дата документа': data[10],
                 '№ постановления об аресте': data[11], 'дата постановления об аресте': data[12], 'xml_link': link_xml}}
    values = to_json[number].values()
    if '' in values or [] in values:  # num_data[number]["номер регистрации"]:
        print(f'[WARNING !] {number}, косячный, не все ключи заполнены')
        errors = myfunctions.make_dir(f'{path}/косяки')
        error = f'{errors}\\{number}.{ext}'
        with open(error, 'w') as f:
            f.write(json.dumps(to_json, indent=2, ensure_ascii=False))
    else:
        with open(fname, 'w') as f:
            f.write(json.dumps(to_json, indent=2, ensure_ascii=False))

    p = p + 1
    print(f'[INFO] отработано {p} ({round(p / count * 100, 2)} %) обращений из {count}, осталось {count - p}')
browser.quit()


def do_merge(path_in, path_out, outfile, db=False):
    merged = {}
    if not os.path.exists(path_in):
        print('папки ', path_in, ' не существует')
        print('Введите название path_in')
        path_in = str(input())
    for infile in os.listdir(path_in):
        if '.json' in infile:
            print(infile)
            with open(f'{path_in}\\{infile}', 'r') as f:
                datas = json.load(f)
                datas[infile[:-5]]['комментарий'] = []
                merged.update(datas)

    if not os.path.exists(path_out):
        print('папки ', path_out, ' не существует')
        print('Введите название path_out')
        path_out = str(input())
    print(path_out)
    with open(f'{path_out}\\{outfile}', 'w') as meg_file:
        json.dump(merged, meg_file, indent=2, ensure_ascii=False)
    if db:
        add_ban(merged)


if settings['db']['use_db'] == 'yes':
    do_merge(path_ban, path_ban, fname_j, db=True)  # объединяем в один файл
else:
    do_merge(path_ban, path_ban, fname_j)
do_merge(path_unban, path_unban, fname_j)


def take_num(path, j_file, t_file='номера_обращений.txt'):
    file = f'{path}\\{j_file}'
    print(file)
    if os.path.isfile(file):
        t_name = f'{path}\\{t_file}'
        print(t_name)
        text = open(t_name, 'w')
        with open(file, 'r') as f:
            d = json.load(f)
        for each in d:
            text.write(each + '\n')
        text.close()


if merge == 'yes':
    take_num(path_ban, fname_j, 'номера_обращений_арестов.txt')  # забираем номера обращений в txt
    take_num(path_unban, fname_j, 'номера_обращений_снятий.txt')
    if serch != 'yes':
        shutil.copyfile(f'{path_ban}/{fname_j}', f'{path_ban}/вводчик.json')
        shutil.copyfile(f'{path_unban}/{fname_j}', f'{path_unban}/снятия.json')


def search_kad_number(path_b, j_file_b, path_u, j_file_u):
    j_file_b = j_file_b[:-5]
    j_file_u = j_file_u[:-5]
    ext = 'json'
    file_b = f'{path_b}\\{j_file_b}.{ext}'
    file_u = f'{path_u}\\{j_file_u}.{ext}'
    print(file_b)
    print(file_u)
    with open(file_b, 'r') as f_b:
        d_b = json.load(f_b)
    with open(file_u, 'r') as f_u:
        d_u = json.load(f_u)
    for each_u in d_u:
        kad_u = d_u[each_u]['кадастровый номер']
        for kad_number in kad_u:
            print('ищу ', kad_number)
            for each_b in d_b:
                print('среди ', d_b[each_b]['кадастровый номер'])
                if kad_number in d_b[each_b]['кадастровый номер']:
                    print('find it')
                    print(d_b[each_b])  # содержание пакета
                    print(each_b)  # номер пакета
                    l_b = d_b[each_b]['комментарий']
                    l_u = d_u[each_u]['комментарий']
                    up_data_b = kad_number + ' есть снятие в пакете ' + each_u
                    up_data_u = kad_number + ' есть арест в пакете ' + each_b
                    l_b.append(up_data_b)
                    l_u.append(up_data_u)
                    d_b[each_b]['комментарий'] = l_b
                    d_u[each_u]['комментарий'] = l_u
                else:
                    print('его нет')
                    print('__________')
    file_b = f'{path_b}\\{j_file_b + "_s"}.{ext}'
    file_u = f'{path_u}\\{j_file_u + "_s"}.{ext}'
    with open(file_b, 'w') as f:
        f.write(json.dumps(d_b, indent=2, ensure_ascii=False))
        f.close()
    with open(file_u, 'w') as f:
        f.write(json.dumps(d_u, indent=2, ensure_ascii=False))
        f.close()


if serch == 'yes':
    search_kad_number(path_ban, fname_j, path_unban, fname_j)  # ищем дубли кад номеров снятий в арестах
a = input("скопировать номера арестов в numbers.txt ? :")
if a in y:
    shutil.copyfile(f'{path_ban}\\номера_обращений_арестов.txt', 'numbers.txt')
a = input("скопировать номера снятий в numbers_unban.txt ? :")
if a in y:
    shutil.copyfile(f'{path_unban}\\номера_обращений_снятий.txt', 'numbers_unban.txt')
if errors:
    input(f'[ВНИМАНИЕ !!!] есть неверно заполненные пакеты, проверьте папку {errors}')
    myfunctions.explore(errors)
else:
    input('Всё завершено удачно, нажмите ENTER для выхода')  # чтоб не закрывалась консоль
myfunctions.explore(path_ban)
myfunctions.explore(path_unban)
