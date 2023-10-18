from bot_pkurp_start import *
import pandas as pd

# dir_ = myfunctions.make_dir('корректировка СНИЛС')
file = settings['file']['sig_file']
file_out = f'{now}_подписанные.xlsx'
url = 'http://pkurp-app-balancer-01.prod.egrn/requests?filter=mine'
logon(url)

print(f'чтение файла "{file}"')
df = pd.read_excel(file)
pre_lnk = 'http://pkurp-app-balancer-01.prod.egrn/00/requests/'
post_link = '/registry_record_signatures/statements'
obr = 0
try:

    for index, row in df.iterrows():
        print(f'{index + 1} из {len(df)}')
        number = row['номер обращения корректировки']
        page = f'{pre_lnk}{number}{post_link}'
        print(page)
        browser.get(page)
        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "mainContent"))
            )
        except:
            print("не вижу страницы подписания !!")
            try:
                browser.find_element(By.CLASS_NAME, 'btn-next').click()
                sleep(1)
                df.at[index, 'подписано'] = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
                obr = obr + 1
                print(f'[INFO] отработано {obr} ({round(obr / len(df) * 100, 2)} %) обращений из {len(df)},'
                      f' осталось {len(df) - obr}')
                # записываем номер пакета в файл
                with open(fname, 'a+') as f:
                    f.write(number + '\n')
                sleep(1)
                continue
            except:
                print("что -то не то !!")
        while not browser.find_element(By.ID, 'CertListBox').get_attribute("value"):
            wait = WebDriverWait(browser, 30)
            cert_value_present = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#CertListBox option[value]")))
            print('нет сертификата')
        browser.find_element(By.CSS_SELECTOR, '.page-footer  .btn-primary').click()
        print('подписать и внести')
        sleep(1)
        while 'Подписание' in browser.page_source:
            print('подписание')
            sleep(0.5)
        df.at[index, 'подписано'] = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        obr = obr + 1
        print(f'[INFO] отработано {obr} ({round(obr / len(df) * 100, 2)} %) обращений из {len(df)},'
              f' осталось {len(df) - obr}')
        # записываем номер пакета в файл
        with open(fname, 'a+') as f:
            f.write(number + '\n')
        sleep(1)
except:
    df.to_excel(f'{now}часть номеров подписанные.xlsx', index=False)
    print('аварийное завершение !')
    sys.exit()
df.to_excel(file_out, index=False)
browser.quit()
input('Всё завершено удачно, нажмите ENTER для выхода')  # чтоб не закрывалась консоль
