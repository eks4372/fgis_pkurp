from bot_pkurp_start import *
import pandas as pd
import re

file = settings['file']['start_file']
dir_ = myfunctions.make_dir('корректировка создана')
file_out = f'{dir_}\\{now}_обращения.xlsx'
url = 'http://pkurp-app-balancer-01.prod.egrn/requests?filter=mine'
logon(url)

print(f'чтение файла "{file}"')
df = pd.read_excel(file)
pre_lnk = 'http://pkurp-app-balancer-01.prod.egrn/search/tabs/record?utf8=%E2%9C%93&search%5Brecord.law_number%5D='
post_link = '&search%5Bfilter%5D=&commit=Запросить'
obr = 0
try:
    for index, row in df.iterrows():
        print(f'{index + 1} из {len(df)}')
        reg_num = row['Рег. № пр./огран.']
        fio = row.ФИО
        snils = row.СНИЛС
        gender = row.пол
        m_i = row.message_id
        reg_n = reg_num.replace(':', '%3A').replace('/', '%2F')
        link = f'{pre_lnk}{reg_n}{post_link}'
        print(link)
        browser.get(link)
        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "*[class^='panel-group item']")))
        except:
            print("не вижу рег записи !!")
        t_body = browser.find_element(By.CSS_SELECTOR, "*[class^='panel-group item']")
        reg = t_body.find_elements(By.TAG_NAME, 'tr')
        m = 0
        find = False
        for index_, reg_f in enumerate(reg):
            if (index_ + 1) % 2 != 0:
                print(f'По номеру права {reg_num} найдено {int(len(reg) / 2)} записей')
                if 'Актуальная' not in reg_f.text:
                    continue
                elif 'Актуальная' in reg_f.text:
                    print(f"Номер права {reg_num} {reg_f.find_element(By.CLASS_NAME, 'text-success').text}")
                    reg_f.find_element(By.CLASS_NAME, 'js-search-loadable').click()
                    try:
                        element = WebDriverWait(browser, 10).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "react-form"))
                        )
                    except:
                        print("не вижу страницы сведений !!")
                        sys.exit()

                    l_menus = browser.find_element(By.CSS_SELECTOR, "*[class^='panel-group item']") \
                        .find_elements(By.CSS_SELECTOR, "*[class^='nav nav-tabs js-fixed']")

                    for l_menu in l_menus:
                        # print(len(l_menus))
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
                        for group in f_groups:
                            if group.text == '':
                                continue
                            elif 'Фамилия' in group.text:
                                f = group.find_element(By.CLASS_NAME, 'form-control').text
                            elif 'Имя' in group.text:
                                n = group.find_element(By.CLASS_NAME, 'form-control').text
                            elif 'Отчество' in group.text:
                                p = group.find_element(By.CLASS_NAME, 'form-control').text
                                break
                        f_n_p = f'{f} {n} {p}'
                        print(f_n_p)
                        if f_n_p == fio:
                            if gender == 'Male':
                                x = ''
                            else:
                                x = 'а'
                            print(f'{fio} найден{x}')
                            find = True
                            break
                        else:
                            print(f'{f_n_p} не равно {fio}')
            else:
                if find:
                    if reg_f.find_element(By.CLASS_NAME, 'pull-right'):
                        print('btn')
                        reg_f.find_element(By.LINK_TEXT, 'Корректировка сведений').click()
                        browser.switch_to.window(browser.window_handles[1])
                        try:
                            element = WebDriverWait(browser, 10).until(
                                EC.presence_of_element_located((By.CLASS_NAME, "tab-group"))
                            )
                        except:
                            print('не загрузилась запись об изменении')
                        browser.find_element(By.LINK_TEXT, 'Сведения о правообладателе').click()
                        forms = browser.find_elements(By.CSS_SELECTOR,
                                                      '#bs-tabs-react-right_holders .scope .form-group')
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
                        browser.find_element(By.CSS_SELECTOR, '#tech-error-react textarea').send_keys(m_i)
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
        df.at[index, 'номер обращения корректировки'] = number
        print(df)
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
