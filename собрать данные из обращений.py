from bot_pkurp_start import *
import pandas as pd
import re

file = settings['file']['numbers_file']
file_out = f'{now}_данные по арестам без СНИЛСа.xlsx'
url = 'http://pkurp-app-balancer-01.prod.egrn/requests?filter=mine'
logon(url)
print(f'чтение файла "{file}"')
df = pd.read_excel(file)
df_ = pd.DataFrame()
obr = 0
try:
    for index, row in df.iterrows():
        print(f'{index + 1} из {len(df)}')
        number = row['номер обращения']
        fio = row['ФИО']
        pre_link = 'http://pkurp-app-balancer-01.prod.egrn/72/requests/'
        post_link = '/registry_data_containers/statements'
        sved_page = f'{pre_link}{number}{post_link}'
        print(number)
        print(sved_page)


        def first():
            browser.get(sved_page)
            try:
                element = WebDriverWait(browser, 300).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "scroll-x"))
                )
            except:
                print("страници Сведения не загрузилась !!")
                if 'Сервис проверки прав доступа недоступен. Обратитесь к администратору' in browser.page_source:
                    first()


        first()

        # print(re.findall(r'\((\d+)\)', browser.find_element(By.ID, 'restrict').text)[0])
        try:
            many_next = ((int(re.findall(r'\((\d+)\)', browser.find_element(By.ID, 'restrict').text)[
                                  0]) - 1) // 10) + 1  # сколько раз нажимать Далее
        except:
            # many_next = int(re.findall(r'\((\d+)\)', browser.find_element(By.ID, 'empty_statement').text)[0])
            if 'Записи, не сформированные автоматически' in browser.find_element(By.ID, 'empty_statement').text:
                print('записей нет !!!')
                dir_err = myfunctions.make_dir('пропущенные пакеты по контролю СНИЛС')
                err_file = f'{dir_err}/err_numbers.txt'
                if os.path.isfile(err_file):
                    flag = 'a'
                else:
                    flag = 'w'
                with open(err_file, flag) as f:
                    f.write(f"пропущен номер обращения,  нет записей {number}" + '\n')
                # sys.exit()
                obr = obr + 1
                continue

        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "scroll-y"))
            )
        except:
            print("страници Сведения не загрузилась !!")
        kad_numbers = []
        reg_numbers = []
        while many_next > 0:
            tab = browser.find_element(By.CSS_SELECTOR, "#filtered_containers_table > div > div:nth-child(8) > div")
            while 'Загрузка' in tab.text:
                print('ждем загрузку ограничений-обременений')
                sleep(1)
            t = tab.find_elements(By.CSS_SELECTOR, ".scroll-y .table tbody tr")
            edit_link = t[0].find_element(By.LINK_TEXT, 'Внесение сведений').get_attribute("href")
            for i in t:
                if 'Запрещение регистрации' in i.text:
                    tds = i.find_elements(By.TAG_NAME, 'td')
                    print(f'обр: {number}, кад№: {tds[3].text}, №ареста: {tds[4].text}, ФИО: {tds[7].text}')
                    kad_numbers.append(tds[3].text)
                    reg_numbers.append(tds[4].text)
            if many_next > 1:
                browser.find_element(By.CSS_SELECTOR, '.scroll-y  .next>.next').click()  # клик далее
                print('клик далее')
            many_next -= 1

        browser.get(edit_link)
        print(edit_link)
        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "react-form"))
            )
        except:
            print("не вижу страницы сведений !!")
            sys.exit()
        l_menu = browser.find_element(By.CLASS_NAME, 'react-form').find_element(By.CSS_SELECTOR,
                                                                                "*[class^='nav nav-tabs js-fixed']")
        l_menu.find_element(By.LINK_TEXT, 'Сведения о лицах').click()

        fgs = browser.find_elements(By.CSS_SELECTOR, '.scope .fieldset .fieldset .fieldset .form-group')
        for fg in fgs:
            if 'Фамилия' in fg.text:
                f = fg.find_element(By.CLASS_NAME, 'form-control').text
            elif 'Имя' in fg.text:
                n = fg.find_element(By.CLASS_NAME, 'form-control').text
            elif 'Отчество' in fg.text:
                p = fg.find_element(By.CLASS_NAME, 'form-control').text
            elif 'Дата рождения' in fg.text:
                bd = fg.find_element(By.CLASS_NAME, 'form-control').text
                # bd = f'{bd[-4:]}-{bd[3:5]}-{bd[:2]}'
            elif 'СНИЛС' in fg.text:
                snils = fg.find_element(By.CLASS_NAME, 'form-control').text
            elif 'Код документа' in fg.text:
                cod_d = fg.find_element(By.CLASS_NAME, 'form-control').text
            elif 'Серия документа' in fg.text:
                sn = fg.find_element(By.CLASS_NAME, 'form-control').text
            elif 'Номер документа' in fg.text:
                num = fg.find_element(By.CLASS_NAME, 'form-control').text
            elif 'Дата документа' in fg.text:
                doc_date = fg.find_element(By.CLASS_NAME, 'form-control').text
                doc_date = f'{doc_date[-4:]}-{doc_date[3:5]}-{doc_date[:2]}'
            elif 'Место рождения' in fg.text:
                bda = fg.find_element(By.CLASS_NAME, 'form-control').text
        fio_ = f'{f} {n} {p}'
        if fio_.lower().strip().replace('ё', 'е') == fio.lower().strip().replace('ё', 'е') and not snils:
            print(f'{fio_} не имеет СНИЛСа')
        elif fio_.lower().strip().replace('ё', 'е') == fio.lower().strip().replace('ё', 'е') and snils:
            print(f'{fio_} имеет СНИЛС, всё ок')
            obr = obr + 1
            continue
        else:
            print('что-то пошло не так !!!')
            dir_err = myfunctions.make_dir('пропущенные пакеты по контролю СНИЛС')
            err_file = f'{dir_err}/err_numbers.txt'
            if os.path.isfile(err_file):
                flag = 'a'
            else:
                flag = 'w'
            with open(err_file, flag) as f:
                f.write(f"пропущен номер обращения {number}" + '\n')
            # sys.exit()
            obr = obr + 1
            continue
        for k_value, r_value in zip(kad_numbers, reg_numbers):
            df_ = df_._append(
                {'номер обращения': number, 'Кадастровый №': k_value, 'Рег. № пр./огран.': r_value, 'ФИО': fio_,
                 'ДР': bd, 'СНИЛС': snils, 'Код документа': cod_d, 'Серия док. уд. личность': sn,
                 'Номер док. уд. личность': num,'Дата  док. уд. личность': doc_date, 'Место рождения': bda},
                ignore_index=True)
        # инфа по прогрессу
        obr = obr + 1
        print(f'[INFO] отработано {obr} ({round(obr / len(df) * 100, 2)} %) обращений из {len(df)},'
              f' осталось {len(df) - obr}')
        # записываем номер пакета в файл
        with open(fname, 'a+') as f:
            f.write(number + '\n')
except:
    if not df_.empty:
        df_.to_excel(f'{now}часть номеров без СНИЛСа.xlsx', index=False)
    print(f'аварийное завершение ! номер {number} не отработан')
    sys.exit()
df_.to_excel(file_out, index=False)
browser.quit()
input('Всё завершено удачно, нажмите ENTER для выхода')  # чтоб не закрывалась консоль
