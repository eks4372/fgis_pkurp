from bot_pkurp_start import *
import pandas as pd
from urllib.parse import unquote
from requestium import Session

file = settings['file']['check_file']
file_out = f'{now}_обращения проконтролированы.xlsx'
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
        reg_num = row['Рег. № пр./огран.']
        try:
            kad_number = row['Кадастровый №']
        except:
            kad_number = ''
        try:
            fio = row.ФИО
            if len(fio) <= 3:
                fio = ''
        except:
            fio = ''
        if fio and kad_number:
            if '  ' in fio:
                fio = fio.replace('  ', ' ')
                df.at[index, 'ФИО'] = fio
            link = f'{pre_lnk}{kad_number}&search[record.law_number]={reg_num}&search[individual.surname]={fio.split()[0]}' \
                   f'&search[individual.name]={fio.split()[1]}{post_link}'
        elif kad_number:
            link = f'{pre_lnk}{kad_number}&search[record.law_number]={reg_num}{post_link}'
        else:
            link = f'http://pkurp-app-balancer-01.prod.egrn/search/tabs/record?search[record.law_number]={reg_num}{post_link}'
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
        print(f'По номеру права {reg_num} найдено {int(len(reg) / 2)} записей')
        for index_, reg_f in enumerate(reg):
            if (index_ + 1) % 2 != 0:
                if 'Актуальная' in reg_f.text:
                    actual = True
                # if 'Актуальная' not in reg_f.text:
                #     continue
                # elif 'Актуальная' in reg_f.text:
                reg_f.find_element(By.CLASS_NAME, 'js-search-loadable').click()
                sleep(1)
                try:
                    element = WebDriverWait(browser, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "react-form"))
                    )
                except:
                    print("не вижу страницы сведений !!")
                    sys.exit()


                # # Выполняем JavaScript, чтобы получить XPath элемента
                # element_xpath = browser.execute_script(
                #     """
                #     var element = arguments[0];
                #     var xpath = '';
                #     while (element && element.nodeType === 1) {
                #         // XPath считается относительно родительского узла
                #         var siblingCount = 0;
                #         var sibling = element.previousSibling;
                #         while (sibling) {
                #             // Учитываем только элементы с тем же тегом
                #             if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                #                 siblingCount++;
                #             }
                #             sibling = sibling.previousSibling;
                #         }
                #         xpath = '/' + element.tagName.toLowerCase() + '[' + (siblingCount + 1) + ']' + xpath;
                #         element = element.parentNode;
                #     }
                #     return xpath;
                #     """,
                #     element
                # )
                # # Находим id родительского элемента
                # parent_xpath = '/'.join(element_xpath.split('/')[:-4])  # Удаляем последний сегмент
                # parent_element = browser.find_element(By.XPATH, parent_xpath)
                # parent_id = parent_element.get_attribute('id')
                # print(parent_id)
                # break
            # history = browser.find_element(By.CSS_SELECTOR, f'#{parent_id} .pointer')
            history = browser.find_element(By.LINK_TEXT , 'Исторические сведения')
            history.click()
            try:
                element = WebDriverWait(browser, 100).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "panel-heading"))
                )
            except:
                print("не вижу истории !!")
            items = browser.find_elements(By.CSS_SELECTOR, '.history .item')
            # for i in items:
            #     print(i.text)
            print(f'базовая запись: {items[-1].text}')
            try:
                kuvd = items[-1].find_element(By.PARTIAL_LINK_TEXT, 'КУВД').text
                print(f"КУВД: {kuvd}")
            except:
                print('похоже базовая запись была еще при царе горохе')
                kuvd = ''
                number = 'номер из ЕГРП'

            if kuvd:
                try:
                    items[-1].find_element(By.LINK_TEXT, kuvd).click()
                    browser.switch_to.window(browser.window_handles[1])
                except:
                    kuvd = input(f'похоже я не нашёл базовую запись, ввудите № КУВД и нажмите enter: ')
                    if not kuvd:
                        number = 'КУВД не найдена'
                    else:
                        browser.find_element(By.LINK_TEXT, kuvd).click()
                        sleep(1)
            if kuvd:
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
                        "72"
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

                break
            else:
                df.at[index, 'номер обращения'] = number
        obr = obr + 1
        print(f'[INFO] отработано {obr} ({round(obr / len(df) * 100, 2)} %) обращений из {len(df)},'
              f' осталось {len(df) - obr}')
        # записываем номер пакета в файл
        with open(fname, 'a+') as f:
            f.write(number + '\n')
except:
    # df['Номер док. уд. личность'] = df['Номер док. уд. личность'].apply(lambda x: str(x).zfill(6))  # 6 значный номер
    df.to_excel(f'{now}часть номеров проконтролированы.xlsx', index=False)
    print('аварийное завершение !')
    sys.exit()
# df['Номер док. уд. личность'] = df['Номер док. уд. личность'].apply(lambda x: str(x).zfill(6))
df.to_excel(file_out, index=False)
browser.quit()
input('Всё завершено удачно, нажмите ENTER для выхода')  # чтоб не закрывалась консоль
