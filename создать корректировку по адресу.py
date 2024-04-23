from bot_pkurp_start import *
import pandas as pd
import re
from urllib.parse import unquote
from urllib.parse import quote

file = settings['file']['start_file']
# dir_ = myfunctions.make_dir('корректировка создана')
file_out = f'{now}_обращения корректировки.xlsx'
url = 'http://pkurp-app-balancer-01.prod.egrn/requests?filter=mine'
logon(url)

print(f'чтение файла "{file}"')
df = pd.read_excel(file)
# pre_lnk = 'http://pkurp-app-balancer-01.prod.egrn/search/tabs/record?utf8=%E2%9C%93&search%5Brecord.law_number%5D='
pre_lnk = 'http://pkurp-app-balancer-01.prod.egrn/search/tabs/record?search'
# post_link = '&search%5Bfilter%5D=&commit=Запросить'
post_link = '&commit=Запросить'
obr = 0
df['номер обращения корректировки'] = ''
try:
    for index, row in df.iterrows():
        print(f'{index + 1} из {len(df)}')
        kad_number = row['Кадастровый №']
        link = f'{pre_lnk}[record.property_number]={kad_number}'
        f = False
        fk = False
        print(link)
        # browser.get(unquote(link))
        browser.get(unquote(quote(link)))
        if "Возникла ошибка на сервере" in browser.page_source:
            print('ошибка сервера, пробую обновить страницу')
            browser.refresh()
        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "*[class^='panel-group item']")))
        except:
            print("не вижу рег записи !!")
        t_body = browser.find_element(By.CSS_SELECTOR, "*[class^='panel-group item']")
        rec = t_body.find_elements(By.TAG_NAME, 'tr')
        m = 0
        find = False
        actual = False
        adj = False
        adj_k = False
        print(f'По кадастровому № {kad_number} найдено {int(len(rec) / 2)} записей')
        for index_, reg_f in enumerate(rec):
            if (index_ + 1) % 2 != 0:
                # print(f'По номеру права {reg_num} найдено {int(len(reg) / 2)} записей')
                # if 'Актуальная' not in reg_f.text:
                #     continue
                if 'Запись о помещении' in reg_f.text or 'Запись о машин' in reg_f.text or 'Запись о помещении' in reg_f.text:
                    reg_f.find_element(By.CLASS_NAME, 'js-search-loadable').click()
                    sleep(1)
                    try:
                        element = WebDriverWait(browser, 10).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "react-form"))
                        )
                    except:
                        print("не вижу страницы сведений !!")
                        sys.exit()
                # break

                try:
                    element = WebDriverWait(browser, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "react-form"))
                    )
                except:
                    print("не вижу страницы сведений !!")
                    sys.exit()

                t_gropups = browser.find_elements(By.CLASS_NAME, 'tab-group')
                for t in t_gropups:
                    l_menus = t.find_elements(By.CSS_SELECTOR, "*[class^='nav nav-tabs js-fixed']")
                    if find:
                        break
                    for l_menu in l_menus:
                        # print(len(l_menus))

                        l_menu.find_element(By.PARTIAL_LINK_TEXT, 'Адрес').click()

                        sleep(1)
                        m = m + 1
                        try:
                            element = WebDriverWait(browser, 10).until(
                                EC.presence_of_element_located((By.CLASS_NAME, "form-group"))
                            )
                        except:
                            print("не вижу страницы сведений !!")
                        f_groups = browser.find_elements(By.CSS_SELECTOR, '.scope .scope .scope .scope .scope  .scope')
                        for group in f_groups:
                            if group.text == '':
                                continue
                            elif 'Район' in group.text:
                                find = True
                                f = group.find_elements(By.CLASS_NAME, 'form-group')
                            elif 'Корпус' in group.text:
                                find = True
                                fk = group.find_elements(By.CLASS_NAME, 'form-group')
                                break


            else:
                if find:
                    if f:
                        for i in f:
                            if i.find_element(By.CLASS_NAME, 'form-control'):
                                print(f'есть заполненное поле {i.text}')
                                adj = True
                                break
                            else:
                                print('поля пусты - корректировка не нужна')
                                adj = False
                    if fk:
                        for i in fk:
                            if i.find_element(By.CLASS_NAME, 'form-control'):
                                print(f'есть заполненное поле {i.text}')
                                # print((i.text).split('\n')[1])
                                if 'корп' != (i.text).split('\n')[1]:
                                    adj_k = True
                                    break
                                else:
                                    print('поля заполнено корректно, корректировка не нужна')
                                    adj_k = False
                                    break
                    if adj or adj_k:
                        if reg_f.find_element(By.CLASS_NAME, 'pull-right'):

                            x = browser.find_elements(By.CSS_SELECTOR, '.pull-right:not([class*=" "])')
                            reg_f_ = x[m]
                            print('btn')
                            reg_f_.find_element(By.LINK_TEXT, 'Корректировка сведений').click()
                            browser.switch_to.window(browser.window_handles[1])
                            try:
                                element = WebDriverWait(browser, 10).until(
                                    EC.presence_of_element_located((By.CLASS_NAME, "tab-group"))
                                )
                            except:
                                print('не загрузилась запись об изменении')
                                if "Возникла ошибка на сервере" in browser.page_source:
                                    print('ошибка сервера, пробую обновить страницу')
                                    browser.refresh()

                            browser.find_element(By.PARTIAL_LINK_TEXT, 'Адрес').click()

                            forms = browser.find_elements(By.CSS_SELECTOR,
                                                          '#bs-tabs-react-right_holders .scope .form-group')
                            if not forms:
                                forms = browser.find_elements(By.CSS_SELECTOR, '.scope .scope .scope .scope .scope  .scope')

                            if adj:
                                for form in forms:
                                    if 'Район' in form.text:
                                        f = form.find_elements(By.CLASS_NAME, 'fa-check-square-o')
                                        for i in f:
                                            i.click()
                                        break
                                        # if 'Тип' in form.text:
                                        #     i.find_element(By.CLASS_NAME, 'fa-check-square-o').click()
                                        # elif 'Наименование' in i.text:
                                        #     i.find_element(By.CLASS_NAME, 'fa-check-square-o').click()
                            if adj_k:
                                for form in forms:
                                    if 'Корпус' in form.text:
                                        f = form.find_elements(By.CLASS_NAME, 'fa-check-square-o')
                                        f[0].click()
                                        break

                            btns = browser.find_elements(By.CLASS_NAME, 'btn-primary')
                            for b in btns:
                                if b.text == 'Далее':
                                    b.click()
                                    print('далее')
                            # browser.find_element(By.CSS_SELECTOR,
                            #                "#tech-error-react input[name='edited_attrs[0][new]'][type='string']") \
                            #     .send_keys(snils)
                            # browser.find_element(By.CLASS_NAME, 'fa-plus').click()

                            # browser.find_element(By.CSS_SELECTOR, '#tech-error-react textarea').\
                            #         send_keys(f'удаление района в городе')
                            if adj_k:
                                n = len(browser.find_elements(By.CSS_SELECTOR, '.table tr'))
                                browser.find_element(By.CSS_SELECTOR,
                                                     f"#tech-error-react input[name='edited_attrs[{n-2}][new]'][type='string']").send_keys('корп')
                            browser.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
                            while not browser.find_element(By.ID, 'CertListBox').get_attribute("value"):
                                wait = WebDriverWait(browser, 30)
                                cert_value_present = wait.until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, "#CertListBox option[value]")))
                                print('нет сертификата')
                            browser.find_element(By.CLASS_NAME, 'btn-next').click()
                            print("подписать и отправить")
                            wait = WebDriverWait(browser, 100)
                            wait_number = wait.until(
                                EC.presence_of_element_located((By.CLASS_NAME, 'alert-success')))

                            res = re.search(r'Other-\d{4}-\d{2}-\d{2}-\d+',
                                            browser.find_element(By.CLASS_NAME, 'alert-success').text)
                            if res:
                                number = res.group()
                                print(number)
                            else:
                                print("Не удалось найти строку с номером обращения")
                                sys.exit()
                            browser.close()
                            browser.switch_to.window(browser.window_handles[0])
                            break
                        else:
                            continue
                    else:
                        find = False
                        number = f'{kad_number} обращение не создано'
                        break
                else:
                    find = False
                    number = f'{kad_number} обращение не создано'
                    break

        if not df['номер обращения корректировки'].isin([number]).any():
            df.at[index, 'номер обращения корректировки'] = number
        else:
            print(f'значение {number} уже существует')
            sys.exit()
        # break
        obr = obr + 1
        print(f'[INFO] отработано {obr} ({round(obr / len(df) * 100, 2)} %) обращений из {len(df)},'
              f' осталось {len(df) - obr}')
        # записываем номер пакета в файл
        with open(fname, 'a+') as f:
            f.write(number + '\n')
except:
    df.to_excel(f'{now}часть номеров корректировки.xlsx', index=False)
    print('аварийное завершение !')
    sys.exit()
df.to_excel(file_out, index=False)
browser.quit()
input('Всё завершено удачно, нажмите ENTER для выхода')  # чтоб не закрывалась консоль
