import sys
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import shutil
import time
import subprocess
import re
import json
FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')


def logon(url, browser, login, password):
    try:
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div/main/div/section/article/div/form/div/div[3]/div[3]/button"))
        )
    except:
        print("не вижу кнопки ВОЙТИ !!")

    login_block = '/html/body/div/main/div/section/article/div/form/div/div[3]/input[1]'
    password_block = '/html/body/div/main/div/section/article/div/form/div/div[3]/input[2]'

    browser.find_element(By.XPATH, login_block).send_keys(login)
    browser.find_element(By.XPATH, password_block).send_keys(password)
    browser.find_element(By.XPATH, '/html/body/div/main/div/section/article/div/form/div/div[3]/div[3]/button').click()
    sleep(1)
    page_source = browser.page_source
    if "Пароль неверный" in page_source:
        print('неверные пароль ! !')
        while browser.current_url != url:
            print("ЗАЛОГИНЬТЕСЬ УЖЕ !")
            sleep(5)
    if "Учетная запись не найдена" in page_source:
        print('неверный логин ! !')
        while browser.current_url != url:
            print("ЗАЛОГИНЬТЕСЬ УЖЕ !")
            sleep(15)
    if "Превышено количество одновременных сессий" in page_source:
        browser.find_element(By.XPATH,'/html/body/div/main/div/section/article/div/form/div/div[3]/div[1]/button').click()
        sleep(1)
        page_source = browser.page_source
    if "Выберите вашу часовую зону" in page_source:
        browser.find_element(By.XPATH,'/html/body/div[3]/div/div/div[2]/div/div[2]/button').click()
        sleep(1)
        alert_obj = browser.switch_to.alert
        alert_obj.accept()


def take_face(browser, link):
    browser.get(link)
    try:
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "react-form"))
        )
    except:
        print("не вижу страницы сведений !!")
    l_menu = browser.find_element(By.CLASS_NAME, 'react-form').find_element(By.CSS_SELECTOR,
                                                                            "*[class^='nav nav-tabs js-fixed']")
    # Входим в Сведения о правообладателе
    l_menu.find_element(By.LINK_TEXT, 'Сведения о правообладателе').click()
    try:
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "form-group"))
        )
    except:
        print("не вижу страницы сведений !!")
    f_groups = browser.find_elements(By.CLASS_NAME, 'form-group')
    for group in f_groups:
        if '*Наименование' in group.text:
            f = "Юридическое лицо"
            f_ = group.find_element(By.CLASS_NAME, 'form-control').text
            return (f, f_)
        elif '*Фамилия' in group.text:
            f = "Физическое лицо"
            f_ = 'фио'
            return (f, f_)


def make_dir(dir: str, remove: bool = False, append: bool = True):
    """remove — пересоздавать ли папку, если она есть
    append — только если remove = False, оставлять ли папку без изменений, если она есть
    почти как os.makedirs('F:\\torrents\\bun', exist_ok=True) ,
    но может создавать копии папок если append  = False, возвращает path
    и / можно писать как угодно"""
    d = dir.replace(':\\', '://')
    d = d.replace('\\', '/')
    d = d.split('/')
    path = ''
    n = 0
    for p in d:
        if p == '':
            n = n + 1
            continue
        elif ':' in p:
            n = n + 1
            path = path + p + '//'
        else:
            name = d[n]
            path = path + name
            n = n + 1
            if n == len(d):
                if os.path.exists(path) and remove:
                    print('папка пересоздана ', path)
                    shutil.rmtree(path)
                    os.mkdir(path)
                elif os.path.exists(path) and remove == False:
                    if append:
                        print('папка ', path, ' существует')
                        return (path)
                    else:
                        i = 1
                        while os.path.exists(path):
                            path = dir + str(i)
                            i = i + 1
                        print('папка есть, выбрано имя ', path)
                        os.mkdir(path)
                else:
                    print('папки нет, создаем ', path)
                    os.mkdir(path)
            else:
                if not os.path.exists(path):
                    os.mkdir(path)
            if n < len(d):
                path = path + '//'
    return (path)


def comment(browser, number, com):
    """в ПКУРП добавляет комментарий"""
    pre_link = 'http://pkurp-app-balancer-01.prod.egrn/72/requests/'
    midl_link = '/comments?_id='
    post_link = '#bs-tabs-messages-comments'
    commemt_page = f'{pre_link}{number}{midl_link}{number}{post_link}'
    browser.get(commemt_page)
    try:
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, 'comment_text'))
        )
    except:
        print("не вижу страницы комментариев !!")
        sleep(1)
        comment(browser, number, com)
    if com not in browser.find_element(By.ID, 'bs-tabs-messages-comments').text:
        browser.find_element(By.ID, 'comment_text').send_keys(com)
        btns = browser.find_elements(By.CSS_SELECTOR, "*[class^='btn btn-default btn btn-primary js-form-timeout']")
        for b in btns:
            if 'Добавить комментарий' in b.text:
                b.click()
    sleep(3)


def explore(path):
    """открывает папку"""
    path = os.path.normpath(path)

    if os.path.isdir(path):
        subprocess.run([FILEBROWSER_PATH, path])
    elif os.path.isfile(path):
        subprocess.run([FILEBROWSER_PATH, '/select,', os.path.normpath(path)])


def num_list(list: list, n: int = 0):
    """принимает список и делит его на списки нужной длины"""
    l = []
    i = 0
    w = 0
    o = len(list) // n
    while w < o:
        l.append(list[:n])
        # print('l= ', l)
        while i < n:
            if len(list) > 0:
                list.pop(0)
                i = i + 1
                # print('list= ', list)
            else:
                break
        i = 0
        w = w +1
        # print('w= ', w)
    if list:
        l.append(list)
    return l


def take_face_(browser, reg_num, subject, inn, reg_name):

    def are_you_sure():
        answer = input(f'ответте утвердительно для продолжения, отрицательно для завершения программы \n'
                       f'или введите искомую фамилию (наименование) и тип лица: 1 - физ лицо, 2 - юр лицо \n'
                       f'через запятую (например: Иванов, 1) для возврата из функции поиска: ')
        if answer.lower() in ['yes', 'y', 'да', 'д', 'ага', ]:
            print('ok')
        elif answer.lower() in ['no', 'n', 'нет', 'н', 'стоп', ]:
            print('выход')
            sys.exit()
        elif ',' in answer:
            f_ = answer.split(',')[0].strip()
            f = answer.split(',')[1].strip()
            if f == '1':
                type = "Физическое лицо"
            elif f == '2':
                type = "Юридическое лицо"
                return ('Актуальная', type, f_)
            else:
                print('не верные данные введены')
                are_you_sure()
        else:
            print('не верные данные введены')
            are_you_sure()

    reg_name = reg_name.split(',')[0]
    print(reg_num, reg_name)
    pre_lnk = 'http://pkurp-app-balancer-01.prod.egrn/search/tabs/record?utf8=%E2%9C%93&search%5Brecord.law_number%5D='
    reg_n = reg_num.replace(':', '%3A').replace('/', '%2F')
    post_link = '&search%5Bfilter%5D=&commit=Запросить'
    link = f'{pre_lnk}{reg_n}{post_link}'
    print(link)
    browser.get(link)
    status = '-'
    i = 0
    try:
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "*[class^='panel-group item']")))
    except:
        print("не вижу рег записи !!")
    t_body = browser.find_element(By.CSS_SELECTOR, "*[class^='panel-group item']")
    reg = t_body.find_elements(By.TAG_NAME, 'tr')
    st = []
    for reg_f in reg:
        if len(reg) > 10:
            print(f'По номеру права {reg_num} найдено {len(reg)} записей, уверены что хотите продолжить поиск?')
            print(f'Это может занят много времени или вылету программы, поэтому предлагаю следующте варианты:')
            are_you_sure()
        if 'Погашенная' in reg_f.text and reg_name.lower() in reg_f.text.lower():
            print(f'Номер права {reg_num} архивный')
            st.append('Погашенная')
            reg_f.find_element(By.CLASS_NAME, 'js-search-loadable').click()
            try:
                element = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "react-form"))
                )
            except:
                print("не вижу страницы сведений !!")
        elif 'Актуальная' in reg_f.text and reg_name.lower() in reg_f.text.lower():
            st.append('Актуальная')
            print(reg_f.find_element(By.CLASS_NAME, 'text-success').text)
            reg_f.find_element(By.CLASS_NAME, 'js-search-loadable').click()
            try:
                element = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "react-form"))
                )
            except:
                print("не вижу страницы сведений !!")

    sleep(1)
    l_menus = browser.find_element(By.CSS_SELECTOR, "*[class^='panel-group item']")\
        .find_elements(By.CSS_SELECTOR, "*[class^='nav nav-tabs js-fixed']")
    m = 0
    for l_menu in l_menus:
        print(len(l_menus))

        l_menu.find_element(By.LINK_TEXT, 'Сведения о правообладателе').click()
        sleep(1)
        m = m + 1
        print(f'вошли в запись запись m= {m}')
        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "form-group"))
            )
        except:
            print("не вижу страницы сведений !!")
        f_groups = browser.find_elements(By.CLASS_NAME, 'form-group')
        f = ''
        i = 0
        for group in f_groups:
            if group.text == '':
                continue
            elif '*Наименование' in group.text:
                f = "Юридическое лицо"
                if 'Российская Федерация' not in group.find_element(By.CLASS_NAME, 'form-control').text:
                    f_ = group.find_element(By.CLASS_NAME, 'form-control').text
                else:
                    print('Российская Федерация!!!')
                    f_ = '-'

            elif '*ИНН' in group.text:
                if group.find_element(By.CLASS_NAME, 'form-control').text == inn:
                    status = st[m - 1]
                    while m != 1:
                        m = m - 1
                        browser.back()
                    return (status, f, f_)
            elif '*Фамилия' in group.text:
                f = "Физическое лицо"
                sur = group.find_element(By.CLASS_NAME, 'form-control').text
                # f_ = 'фио'
            elif '*Имя' in group.text:
                n = group.find_element(By.CLASS_NAME, 'form-control').text
                if n.lower().replace('ё', 'е') in subject.lower().replace('ё', 'е'):
                    i = i + 1
            elif 'Отчество' in group.text:
                l = group.find_element(By.CLASS_NAME, 'form-control').text
                if l.lower().replace('ё', 'е') in subject.lower().replace('ё', 'е'):
                    i = i + 1

                print(f'i= {i}')
                print(f'm= {m}')
                if i >= 2:
                    status = st[m - 1]
                    while m != 1:
                        m = m - 1
                        browser.back()
                    f_ = f'{sur} {n} {l}'
                    return (status, f, f_,)
        print(f'прошли запись')
        if i < 2:
            continue
    return status


def surname_for_serch(surname):
    if 'е' in surname.lower() or 'ё' in surname.lower():
        if 'ё' == surname.lower()[0] or 'е' == surname.lower()[0]:
            surname = surname[1:]
        if 'ё' in surname.lower():
            surname = surname.lower().rsplit('ё')[0]
        else:
            if 'е' in surname.lower():
                surname = surname.lower().rsplit('е')[0]
    return surname


def serch_fio(f, f_):
    f = f.split()
    n = 0
    for i in f:
        if i.lower().replace('ё','е') in f_.lower().replace('ё','е'):
            n = n + 1
    return n


def serch_snils(s:str):
    """ищет и возвращает СНИЛС в строке"""
    result = re.search(r'\d{3}-\d{3}-\d{3} \d{2}', s)
    if result:
        return result[0]
    else:
        return False


def serch_ogrn(s:str):
    """ищет и возвращает СНИЛС в строке"""
    result = re.search(r'\d{13}', s)
    if result:
        return result[0]
    else:
        return False


def distr_json(file, write = False, d = None):
    """возвращает словарь из файла json
    или записывает словарь в файл json"""
    if not write:
        with open(file, 'r') as f:
            data = json.load(f)
        return data
    if write:
        with open(file, 'w') as f:
            f.write(json.dumps(d, ensure_ascii=False, indent=2))
        return True
