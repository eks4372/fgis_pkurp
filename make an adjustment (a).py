from bot_pkurp_start import *
import pandas as pd
import re
from urllib.parse import unquote

file = settings['file']['start_file']
# dir_ = myfunctions.make_dir('корректировка создана')
file_out = f'{now}_обращения корректировки.xlsx'
url = 'http://pkurp-app-balancer-01.prod.egrn/requests?filter=mine'
logon(url)

print(f'чтение файла "{file}"')
df = pd.read_excel(file)
# pre_lnk = 'http://pkurp-app-balancer-01.prod.egrn/search/tabs/record?utf8=%E2%9C%93&search%5Brecord.law_number%5D='
pre_lnk = 'http://pkurp-app-balancer-01.prod.egrn/search/tabs/record?search[record.property_number]='
# post_link = '&search%5Bfilter%5D=&commit=Запросить'
post_link = '&commit=Запросить'
obr = 0
df['номер обращения корректировки'] = ''
try:
    for index, row in df.iterrows():
        print(f'{index + 1} из {len(df)}')
        reg_num = row['Рег. № пр./огран.']
        kad_number = row['Кадастровый №']
        fio = row.ФИО
        if '  ' in fio:
            fio = fio.replace('  ', ' ')
            df.at[index, 'ФИО'] = fio
        snils = row.СНИЛС
        gender = row.пол
        m_i = row.message_id
        # reg_n = reg_num.replace(':', '%3A').replace('/', '%2F')
        # kad_number = kad_number.replace(':', '%3A')
        # link = f'{pre_lnk}{reg_n}{post_link}'
        # link = f'{pre_lnk}{kad_number}&search[record.law_number]={reg_num}&search[individual.surname]={fio.split()[0]}'\
        #        f'&search[individual.name]={fio.split()[1]}{post_link}'
        link = f'{pre_lnk}{kad_number}&search[record.law_number]={reg_num}{post_link}'
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
        t_body = browser.find_element(By.CSS_SELECTOR, "*[class^='panel-group item']")
        reg = t_body.find_elements(By.TAG_NAME, 'tr')
        m = 0
        find = False
        actual = False
        print(f'По номеру права {reg_num} найдено {int(len(reg) / 2)} записей')
        for index_, reg_f in enumerate(reg):
            if (index_ + 1) % 2 != 0:
                # print(f'По номеру права {reg_num} найдено {int(len(reg) / 2)} записей')
                if 'Актуальная' not in reg_f.text:
                    continue
                elif 'Актуальная' in reg_f.text:
                    reg_f.find_element(By.CLASS_NAME, 'js-search-loadable').click()
                    sleep(1)
                    try:
                        element = WebDriverWait(browser, 10).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "react-form"))
                        )
                    except:
                        print("не вижу страницы сведений !!")
                        sys.exit()
        for index_, reg_f in enumerate(reg):
            if (index_ + 1) % 2 != 0:
                # print(f'По номеру права {reg_num} найдено {int(len(reg) / 2)} записей')
                if 'Актуальная' not in reg_f.text:
                    continue
                elif 'Актуальная' in reg_f.text:
                    print(f"Номер права {reg_num} {reg_f.find_element(By.CLASS_NAME, 'text-success').text}")
                    # reg_f.find_element(By.CLASS_NAME, 'js-search-loadable').click()
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
                            try:
                                l_menu.find_element(By.LINK_TEXT, 'Сведения о правообладателе').click()
                            except:
                                l_menu.find_element(By.PARTIAL_LINK_TEXT, 'Сведения о лицах').click()
                                # print('вместо "Сведения о правообладателе" найдено "Сведения о лицах..."')
                                # m = m + 1
                                # continue
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
                            for group in f_groups:
                                if group.text == '':
                                    continue
                                elif 'Фамилия' in group.text:
                                    f = group.find_element(By.CLASS_NAME, 'form-control').text
                                elif 'Имя' in group.text:
                                    n = group.find_element(By.CLASS_NAME, 'form-control').text
                                elif 'Отчество' in group.text:
                                    p = group.find_element(By.CLASS_NAME, 'form-control').text
                                    # break
                                    f_n_p = f'{f} {n} {p}'
                                    f_n_p =f_n_p.strip()
                                    print(f_n_p)
                                    if f_n_p == fio:
                                        if gender == 'Male':
                                            x = ''
                                        else:
                                            x = 'а'
                                        print(f'{fio} найден{x}')
                                        find = True
                                        actual = True
                                        break
                                    else:
                                        print(f'{f_n_p} не равно {fio}')
                            else:
                                if m == int(len(reg) / 2):
                                    print(f'{fio} не найден в {reg_num}')
                                    sys.exit()
            else:
                if find:
                    if reg_f.find_element(By.CLASS_NAME, 'pull-right'):
                        # ищем точное совпадение
                        x = browser.find_elements(By.CSS_SELECTOR, '.panel-group .pull-right:not([class*=" "])')
                        reg_f_ = x[m - 1]
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
                        try:
                            browser.find_element(By.LINK_TEXT, 'Сведения о правообладателе').click()
                            forms = browser.find_elements(By.CSS_SELECTOR,
                                                          '#bs-tabs-react-right_holders .scope .form-group')
                        except:
                            browser.find_element(By.LINK_TEXT, 'Сведения о лицах').click()
                            forms = browser.find_elements(By.CSS_SELECTOR,
                                                          '.fieldset .scope .form-group')
                        f_n_p = ''
                        for form in forms:
                            # print(form.text)
                            if form.text == '':
                                continue
                            elif 'Фамилия' in form.text:
                                f = form.find_element(By.CLASS_NAME, 'form-control').text
                            elif 'Имя' in form.text:
                                n = form.find_element(By.CLASS_NAME, 'form-control').text
                            elif 'Отчество' in form.text:
                                p = form.find_element(By.CLASS_NAME, 'form-control').text
                                f_n_p = f'{f} {n} {p}'
                                f_n_p = f_n_p.strip()
                                print(f_n_p)
                            if f_n_p == fio:
                                if 'СНИЛС' in form.text:
                                    form.find_element(By.CLASS_NAME, 'fa-check-square-o').click()
                                    break
                        btns = browser.find_elements(By.CLASS_NAME, 'btn-primary')
                        for b in btns:
                            if b.text == 'Далее':
                                b.click()
                                print('далее')
                        browser.find_element(By.CSS_SELECTOR,
                                             "#tech-error-react input[name='edited_attrs[0][new]'][type='string']") \
                            .send_keys(snils)
                        browser.find_element(By.CLASS_NAME, 'fa-plus').click()
                        browser.find_element(By.CSS_SELECTOR, '#tech-error-react textarea').send_keys(
                            f'ид запроса в СМЭВ {fio}: {m_i}')
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
        if not actual:
            print(f'по рег номеру {reg_num} нет актуальных записей')
            dir_err = myfunctions.make_dir('ошибки')
            err_file = f'{dir_err}/err_numbers.txt'
            if os.path.isfile(err_file):
                flag = 'a'
            else:
                flag = 'w'
            with open(err_file, flag) as f:
                f.write(f'по рег номеру {reg_num} нет актуальных записей' + '\n')
            df.at[index, 'номер обращения корректировки'] = 'обращение не создано'
            obr = obr + 1
            continue
        else:
            if not df['номер обращения корректировки'].isin([number]).any():
                df.at[index, 'номер обращения корректировки'] = number
            else:
                print(f'значение {number} уже существует')
                sys.exit()
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