from bot_pkurp_start import *
import pandas as pd
from urllib.parse import unquote
from requestium import Session
import re
from date_select import selected_dates
from datetime import datetime


def check_date_in_range(end, start, string, n = 2):
    pattern = r"\d{2}\.\d{2}\.\d{4}"
    matches = re.findall(pattern, string)

    if n == 2:
        if len(matches) >= n:
            second_date = matches[1]
            year = int(second_date[-4:])
    elif n == 1:
        year = matches[0]
    else:
        year = input('не найдена дата погашения, введите год вручную: ')

    if datetime.strptime(end, "%d.%m.%Y") <= datetime.strptime(year, "%d.%m.%Y") <= datetime.strptime(start, "%d.%m.%Y"):
        return True
    return False


def extract_number(string):
    pattern = r"\[НомРегПрава=(.*?)\]"

    match = re.search(pattern, string)
    if match:
        return match.group(1)

    return None


file = settings['file']['check_file_']
file_out = f'{now}_обращения по датам проконтролированы.xlsx'
# selected_dates = date_select.select_dates()
if selected_dates:
    start_date, end_date = selected_dates
    print(f"Выбранные даты: {start_date} - {end_date}")
url = 'http://pkurp-app-balancer-01.prod.egrn/requests?filter=mine'
logon(url)
print(f'чтение файла "{file}"')
df = pd.read_excel(file)
pre_lnk = 'http://pkurp-app-balancer-01.prod.egrn/search/tabs/record?search[record.property_number]='
post_link = '&commit=Запросить'
obr = 0
try:
    for index, row in df.iterrows():
        print(f'{index + 1} из {len(df)}')
        kad_number = row['Кадастровый №']
        er = row['Ошибка в данных']
        if 'Право' in er:
            serch_reg_num = row['Путь']
            reg_num = extract_number(serch_reg_num)
            print(f'у объекта {kad_number} ошибка в праве {reg_num}')
            link = f'{pre_lnk}{kad_number}&search[record.law_number]={reg_num}{post_link}'
        else:
            print(f'у объекта {kad_number} ошибка в объекте')
            link = f'{pre_lnk}{kad_number}{post_link}'
        print(link)

        browser.get(unquote(link))
        if "Возникла ошибка на сервере" in browser.page_source:
            print('ошибка сервера, пробую обновить страницу')
            browser.refresh()
        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "*[class^='panel-group item']")))
        except:
            print("не вижу рег записи !!")
            try:
                link = f'{pre_lnk}{kad_number}&search[record.law_number]={reg_num}{post_link}'
                print(link)
                browser.get(unquote(link))
            except:
                print("всёравно не вижу рег записи !!")
        t_body = browser.find_element(By.CSS_SELECTOR, "*[class^='panel-group item']")
        reg = t_body.find_elements(By.TAG_NAME, 'tr')
        m = 0
        find = False
        actual = False
        if 'Право' in er:
            print(f'По номеру права {reg_num} найдено {int(len(reg) / 2)} записей')
            for index_, reg_f in enumerate(reg):
                if (index_ + 1) % 2 != 0:
                    if reg_num in reg_f.text:
                        if 'Актуальная' in reg_f.text:
                            actual =True
                        reg_f.find_element(By.CLASS_NAME, 'js-search-loadable').click()
                        sleep(1)
                        try:
                            element = WebDriverWait(browser, 10).until(
                                EC.presence_of_element_located((By.CLASS_NAME, "react-form"))
                            )
                        except:
                            print("не вижу страницы сведений !!")
                            sys.exit()
                        break
        else:
            print(f'По кадастровому номеру {kad_number} найдено {int(len(reg) / 2)} записей')
            for index_, reg_f in enumerate(reg):
                if (index_ + 1) % 2 != 0:
                    if kad_number in reg_f.text:
                        if 'Актуальная' in reg_f.text:
                            actual =True
                        reg_f.find_element(By.CLASS_NAME, 'js-search-loadable').click()
                        sleep(1)
                        try:
                            element = WebDriverWait(browser, 10).until(
                                EC.presence_of_element_located((By.CLASS_NAME, "react-form"))
                            )
                        except:
                            print("не вижу страницы сведений !!")
                            sys.exit()
                        break

        # Открываем историю
        history = browser.find_element(By.LINK_TEXT, 'Исторические сведения')
        history.click()
        try:
            element = WebDriverWait(browser, 100).until(
                EC.presence_of_element_located((By.CLASS_NAME, "panel-heading"))
            )
        except:
            print("не вижу истории !!")
        items = browser.find_elements(By.CSS_SELECTOR, '.history .item')
        for i in items:
            # print(i.text)
            if check_date_in_range(start_date, end_date, i.text, 1):

                # print(f'базовая запись: {items[-1].text}')
                kuvd = i.find_element(By.PARTIAL_LINK_TEXT, 'КУВД').text
                print(f"КУВД: {kuvd}")
                try:
                    i.find_element(By.LINK_TEXT, kuvd).click()
                    browser.switch_to.window(browser.window_handles[1])
                except:
                    kuvd = input(f'похоже я не нашёл базовую запись, ввудите № КУВД и нажмите enter: ')
                    browser.find_element(By.LINK_TEXT, kuvd).click()
                    sleep(1)
                    browser.switch_to.window(browser.window_handles[1])
                try:
                    element = WebDriverWait(browser, 100).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "kuvd-page"))
                    )
                except:
                    print("не открылось ППОЗ !!")
                data = {
                    "pageNumber": 0,
                    "pageSize": 10,
                    "idKUVD": kuvd,
                    "objectRegions": [
                        "72", "00"
                    ],
                    "byActiveExecutor": True
                }

                s = Session(driver=browser)
                s.transfer_driver_cookies_to_session()
                post = s.post('http://ppoz-service-bal-01.prod.egrn:9001/manager/requests', json=data)
                # print(post.text)
                # print(post.status_code)
                print(post.json())
                # print(post.json()['requests'])
                if 200 <= post.status_code < 400:
                    print(f'[INFO] статус запроса : OK')
                    break
                else:
                    print(f'[ERROR] что-то пошло не так код ответа {post.status_code}')
                    print(post.text)
                    sys.exit()
        browser.close()
        browser.switch_to.window(browser.window_handles[0])

        number = post.json()['requests'][0]['appealNumber']
        print(f'номер обращения: {number}')
        for i in post.json()['requests']:
            for u in i['responsibleUsers']:
                if u['roleTitle'] == 'Специалист кадастровой палаты':
                    # fio = u['firstName'] + u['lastName'] + u['secondName']
                    fio_kad = f"{u['lastName']} {u['firstName']} {u['secondName']}"
                    date_kad = u['completionDate']
                elif u['roleTitle'] == 'Регистратор, принимающий решение':
                    fio_reg = f"{u['lastName']} {u['firstName']} {u['secondName']}"
                    date_reg = u['completionDate']
        print(f'специалист кадастровой палаты: {fio_kad}, дата: {date_kad}')
        print(f'регистратор, принимающий решение: {fio_reg}, дата: {date_reg}')

        df.at[index, 'номер обращения'] = number
        df.at[index, 'номер КУВД'] = kuvd
        df.at[index, 'специалист кад. палаты'] = fio_kad
        df.at[index, 'дата завершения кад'] = date_kad
        df.at[index, 'рег., принимающий решение'] = fio_reg
        df.at[index, 'дата завершения рег'] = date_reg
        df.at[index, 'актуальное'] = actual
        # print(df)

        # break
        obr = obr + 1
        print(f'[INFO] отработано {obr} ({round(obr / len(df) * 100, 2)} %) обращений из {len(df)},'
              f' осталось {len(df) - obr}')
        # записываем номер пакета в файл
        with open(fname, 'a+') as f:
            f.write(number + '\n')
except:

    df.to_excel(f'{now}часть номеров по дате проконтролированы.xlsx', index=False)
    print('аварийное завершение !')
    sys.exit()

df.to_excel(file_out, index=False)
browser.quit()
input('Всё завершено удачно, нажмите ENTER для выхода')  # чтоб не закрывалась консоль
