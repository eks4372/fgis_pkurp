from bot_pkurp_start import *
import pandas as pd
from urllib.parse import unquote
from requestium import Session
import re
from datetime import datetime

date_start = settings['file']['date_st']
file = settings['file']['check_file_a']
file_out = f'{now}_архивные номера проконтролированы.xlsx'
url = 'http://pkurp-app-balancer-01.prod.egrn/requests?filter=mine'
logon(url)
print(f'чтение файла "{file}"')
df = pd.read_excel(file)
pre_lnk = 'http://pkurp-app-balancer-01.prod.egrn/search/tabs/record?search[record.property_number]='
post_link = '&commit=Запросить'
obr = 0
err = 0
try:
    for index, row in df.iterrows():
        find = False
        print(f'{index + 1} из {len(df)}')
        kad_number = row['Кадастровый №']
        link = f'{pre_lnk}{kad_number}{post_link}'
        browser.get(unquote(link))
        if "Возникла ошибка на сервере" in browser.page_source:
            print('ошибка сервера, пробую обновить страницу')
            browser.refresh()
        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "*[class^='panel-group item']")))
        except:
            print("не вижу рег записи !!")
            # try:
            #     link = f'{pre_lnk}{kad_number}&search[record.law_number]={reg_num}{post_link}'
            #     print(link)
            #     browser.get(unquote(link))
            # except:
            #     print("всёравно не вижу рег записи !!")
        t_body = browser.find_element(By.CSS_SELECTOR, "*[class^='panel-group item']")
        reg = t_body.find_elements(By.TAG_NAME, 'tr')
        m = 0
        find = False
        actual = False
        print(f'По кадастровому номеру {kad_number} найдено {int(len(reg) / 2)} записей')
        if 'Архивная' in reg[0].text:
            print(f'кад номер {kad_number} архивный')
        else:
            print(f'!!! кад номер {kad_number} не архивный !!!')
            err +=1
            dir_err = myfunctions.make_dir('пропущенные номера')
            err_file = f'{dir_err}/err_numbers.txt'
            if os.path.isfile(err_file):
                flag = 'a'
            else:
                flag = 'w'
            with open(err_file, flag) as f:
                f.write(f'[ERROR] !!! кад номер {kad_number} не архивный !!!')
            continue
        # проверяем наличие актуальных прав
        for index_, reg_f in enumerate(reg):
            if (index_ + 1) % 2 != 0:
                if 'Актуальная' in reg_f.text:
                    actual = True
                    print(f'у кадастрогово номера {kad_number} найдена актуальная запись о правах')
                    break
        if actual:
            pattern = r"\d{2}\.\d{2}\.\d{4}"
            matches = re.findall(pattern, reg[0].text)
            second_date = matches[1]
            print(f'дата погашения {second_date}')
            if datetime.strptime(second_date, "%d.%m.%Y") <= datetime.strptime(date_start, "%d.%m.%Y"):
                print(f'кадастровый №{kad_number} снят {second_date}, т.е. раньше {date_start}')
                df.at[index, 'дата снятия а учета'] = second_date
                df.at[index, 'номер обращения'] = 'снято в АИС ГКН'
                df.at[index, 'актуальное'] = actual
                continue
            reg[0].find_element(By.CLASS_NAME, 'js-search-loadable').click()
            sleep(1)
            try:
                element = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "react-form"))
                )
            except:
                print("не вижу страницы сведений !!")
                sys.exit()

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
                if second_date in i.text:
                    find = True

                    try:
                        kuvd = i.find_element(By.PARTIAL_LINK_TEXT, 'КУВД').text
                        print(f"КУВД: {kuvd}")
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
                    print(post.json())
                    # print(post.json()['requests'])
                    if 200 <= post.status_code < 400:
                        print(f'[INFO] статус запроса : OK')
                        break
                    else:
                        print(f'[ERROR] что-то пошло не так код ответа {post.status_code}')
                        print(post.text)
                        sys.exit()
            if not find:
                print(f'[ERROR] у записи с кадастровым номером {kad_number} не нашел в истории нужную запись')
                # записываем номер пакета в файл
                with open(fname, 'a+') as f:
                    f.write(kad_number + '\n')
                    f.close()
                    # и в ошибки
                dir_err = myfunctions.make_dir('пропущенные пакеты')
                err_file = f'{dir_err}/err_numbers.txt'
                if os.path.isfile(err_file):
                    flag = 'a'
                else:
                    flag = 'w'
                with open(err_file, flag) as f:
                    err += 1
                    f.write(f'[ERROR] у записи с кадастровым номером {kad_number} не нашел в истории нужную запись' + '\n')
                continue
            browser.close()
            browser.switch_to.window(browser.window_handles[0])

            if not post.json()['requests']:
                print(f'по номеру книги {kuvd} ответ из ППОЗ не получен')
                number = f'по номеру книги {kuvd} ответ из ППОЗ не получен'
                # print(i.text)
                lines = i.text.split('\n')
                first_line = lines[0]
                parts = first_line.split()
                fio_reg = ' '.join(parts[-3:])
                df.at[index, 'рег., принимающий решение'] = fio_reg
                df.at[index, 'актуальное'] = actual
            else:
                number = post.json()['requests'][0]['appealNumber']
                print(f'номер обращения: {number}')
                for i in post.json()['requests']:
                    for u in i['responsibleUsers']:
                        if 'Специалист кадастровой палаты' in u['roleTitle']:
                            # fio = u['firstName'] + u['lastName'] + u['secondName']
                            fio_kad = f"{u['lastName']} {u['firstName']} {u['secondName']}"
                            date_kad = u['completionDate']
                        elif u['roleTitle'] == 'Регистратор, принимающий решение':
                            fio_reg = f"{u['lastName']} {u['firstName']} {u['secondName']}"
                            date_reg = u['completionDate']
                print(f'специалист кадастровой палаты: {fio_kad}, дата: {date_kad}')
                print(f'регистратор, принимающий решение: {fio_reg}, дата: {date_reg}')

                df.at[index, 'дата снятия а учета'] = second_date
                df.at[index, 'номер обращения'] = number
                df.at[index, 'номер КУВД'] = kuvd
                df.at[index, 'специалист кад. палаты'] = fio_kad
                df.at[index, 'дата завершения кад'] = date_kad
                df.at[index, 'рег., принимающий решение'] = fio_reg
                df.at[index, 'дата завершения рег'] = date_reg
                df.at[index, 'актуальное'] = actual
                # print(df)
        else:
            df.at[index, 'актуальное'] = actual

        # break
        obr = obr + 1
        print(f'[INFO] отработано {obr} ({round(obr / len(df) * 100, 2)} %) обращений из {len(df)},'
              f' осталось {len(df) - obr}')
        # записываем номер пакета в файл
        with open(fname, 'a+') as f:
            f.write(kad_number + '\n')
except:
    df.to_excel(f'{now}часть архивных номеров проконтролированых.xlsx', index=False)
    print('аварийное завершение !')
    sys.exit()

df.to_excel(file_out, index=False)
if err:
    with open(err_file, 'a') as f:
        f.write('-' * 10 + '\n')
    myfunctions.explore(dir_err)
    os.startfile(f'{dir_err}\err_numbers.txt', 'open')
browser.quit()
input('Всё завершено удачно, нажмите ENTER для выхода')  # чтоб не закрывалась консоль
