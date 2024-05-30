import sys
from bot_pkurp_start import *
import pandas as pd
from urllib.parse import unquote
from urllib.parse import quote
import re

file = settings['file']['start_file']
file_out = f'{now}_обращения корректировки.xlsx'
url = 'http://pkurp-app-balancer-01.prod.egrn/requests?filter=mine'
logon(url)

print(f'чтение файла "{file}"')
df = pd.read_excel(file)
pre_lnk = 'http://pkurp-app-balancer-01.prod.egrn/search/tabs/record?search'
post_link = '&commit=Запросить'
obr = 0
df['номер обращения корректировки'] = ''
try:
    for index, row in df.iterrows():
        print(f'{index + 1} из {len(df)}')
        kad_number = row['Кадастровый №']
        name = row['наименование']
        link = f'{pre_lnk}[record.property_number]={kad_number}'
        print(link)
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
        print(f'По кадастровому № {kad_number} найдено {int(len(rec) / 2)} записей')
        for index_, reg_f in enumerate(rec):
            if (index_ + 1) % 2 != 0:
                if 'Запись о помещении' in reg_f.text or 'Запись о машин' in reg_f.text or 'Запись о помещении' in reg_f.text or 'Запись о здании' in reg_f.text:
                    reg_f.find_element(By.CLASS_NAME, 'js-search-loadable').click()
                    m = m + 1
                    find = True
                    sleep(1)
                    try:
                        element = WebDriverWait(browser, 10).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "react-form"))
                        )
                    except:
                        print("не вижу страницы сведений !!")
                        sys.exit()
                    continue

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
                browser.find_element(By.PARTIAL_LINK_TEXT, 'Характеристики').click()

                forms = browser.find_elements(By.CSS_SELECTOR,
                                              '#bs-tabs-react-params .scope .form-group')
                if not forms:
                    forms = browser.find_elements(By.CSS_SELECTOR, '.scope .scope .scope .scope .scope .scope')
                if not forms:
                    forms = browser.find_elements(By.CSS_SELECTOR, '.scope .scope .scope .scope .scope')
                for form in forms:
                    if 'Наименование' in form.text:
                        f = form.find_element(By.CLASS_NAME, 'fa-check-square-o').click()
                        break
                btns = browser.find_elements(By.CLASS_NAME, 'btn-primary')
                for b in btns:
                    if b.text == 'Далее':
                        b.click()
                        print('далее')
                browser.find_element(By.CSS_SELECTOR,
                                     "#tech-error-react input[name='edited_attrs[0][new]'][type='string']").send_keys(name)
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

        if not find:
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
