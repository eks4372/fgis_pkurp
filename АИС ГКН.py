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
import pandas as pd
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
# from gui_login_form import return_id

settings = configparser.ConfigParser()
settings.read('settings.ini', encoding="utf-8")

now = datetime.datetime.now().strftime("%d-%m-%Y %H_%M")
ext = 'txt'
d = myfunctions.make_dir('result_logs')
fname = f'{d}\\{now}.{ext}'
work_file = open(fname, "w")
work_file.close()
file = settings['file']['ais']
file_out = f'{now}_наименования из АИС ГКН.xlsx'
print(f'чтение файла "{file}"')
df = pd.read_excel(file)
a = 0
correct = [1, 2, 3]
while a not in correct:
    a = input('искать ОКС в 1 - актуальных, 2- архивных, 3 - анулированных (по умолчанию 1): ')
    if not a:
        a = 1
    else:
        a = int(a)

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

url_OKS_actual = 'http://10.72.141.10/wrapper/wrapperform.aspx?listname=OKS_DATA_NEW&name=OKS_ACT&current=OKS_ACT'
url_OKS_arch = 'http://10.72.141.10/wrapper/wrapperform.aspx?listname=OKS_DATA_NEW&name=OKS_ARC&current=OKS_ARC'
url_OKS_null = 'http://10.72.141.10/wrapper/wrapperform.aspx?listname=OKS_DATA_NEW&name=OKS_NULL&current=OKS_NULL'
if a == 1:
    browser.get(url_OKS_actual)
elif a == 2:
    browser.get(url_OKS_arch)
else:
    browser.get(url_OKS_null)
input('авторизуйтесь и нажмите тут enter')
sleep(1)
print('залогонились')
obr = 0
browser.refresh()
sleep(1)
# iframe = browser.find_elements(By.TAG_NAME, 'frame')
iframe = browser.find_elements(By.TAG_NAME, 'frame')[1]
browser.switch_to.frame(iframe)
try:
    for index, row in df.iterrows():
        print(f'{index + 1} из {len(df)}')
        kad_number = row['CADASTRALNUMBER']

        browser.find_element(By.ID, 'ctl00_tb0').clear()
        browser.find_element(By.ID, 'ctl00_tb0').send_keys(kad_number)
        browser.find_element(By.ID, 'ctl00_b1').click()
        print(f'жмём найти {kad_number}')
        try:
            element = WebDriverWait(browser, 10).until(
                EC.text_to_be_present_in_element((By.ID, 'ErrLabel2'), '')  # Проверяем наличие любого текста в элементе
            )
            # print("Текст появился в элементе с ID ErrLabel2!")
        except:
            print("Текст не появился в элементе с ID ErrLabel2 или время истекло")

        f = int(browser.find_element(By.ID, 'ErrLabel2').text.split(':')[1].strip())
        print(f'найдено {f}')
        name = 'error'
        if f == 0:
            name = 'не найдено'
        else:
            table = browser.find_element(By.CSS_SELECTOR, '#DataGrid1 .odd')
            td = table.find_elements(By.TAG_NAME, 'td')
            i = 0
            for t in td:
                i += 1
                if i == 6:
                    print(t.text)
                    name = t.text
                    break
        df.at[index, 'наименование'] = name
        obr = obr + 1
        print(f'[INFO] отработано {obr} ({round(obr / len(df) * 100, 2)} %) обращений из {len(df)},'
              f' осталось {len(df) - obr}')
except:
    df.to_excel(f'{now}часть наименований из АИС ГКН.xlsx', index=False)
    print('аварийное завершение !')
    sys.exit()
df.to_excel(file_out, index=False)
browser.quit()
input('Всё завершено удачно, нажмите ENTER для выхода')  # чтоб не закрывалась консоль
