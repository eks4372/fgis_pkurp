from bot_pkurp_start import *
import pandas as pd
from urllib.parse import unquote
from requestium import Session

w = ['Запрещение регистрации', 'Арест', 'Прочие ограничения прав и обременения объекта недвижимости']
# file = settings['file']['check_file']
file = 'numbers.xlsx'
file_out = f'{now}_обращения для фильтра.xlsx'
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
        reg_num = row['enc_reg_num']
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
        if 'Сведения, удовлетворяющие запросу, не найдены.' in browser.page_source:
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
        # for index_, reg_f in enumerate(reg):
        #     if (index_ + 1) % 2 != 0:
        for i in w:
            if i in reg[0].text:
                print(f'вид: {i}')
                df.at[index, 'Вид'] = i
                find = True
                break
        if not find:
            print('не найдено')
            df.at[index, 'Вид'] = 'не найдено'
        obr = obr + 1
        print(f'[INFO] отработано {obr} ({round(obr / len(df) * 100, 2)} %) обращений из {len(df)},'
              f' осталось {len(df) - obr}')
        # записываем номер пакета в файл
        with open(fname, 'a+') as f:
            f.write(reg_num + '\n')
except:
    # df['Номер док. уд. личность'] = df['Номер док. уд. личность'].apply(lambda x: str(x).zfill(6))  # 6 значный номер
    df.to_excel(f'{now}часть номеров для фильтра.xlsx', index=False)
    print('аварийное завершение !')
    sys.exit()
df.to_excel(file_out, index=False)
browser.quit()
input('Всё завершено удачно, нажмите ENTER для выхода')  # чтоб не закрывалась консоль
