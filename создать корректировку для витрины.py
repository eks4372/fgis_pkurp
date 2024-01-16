from bot_pkurp_start import *
import pandas as pd
import re


def check_date_in_range(string):
    pattern = r"\d{2}\.\d{2}\.\d{4}"

    matches = re.findall(pattern, string)

    if len(matches) >= 2:
        second_date = matches[1]
        year = int(second_date[-4:])


    else:
        year = int(input('не найдена дата погашения, введите год вручную: '))

    if 2015 <= year <= 2016:
        return True

    return False


dir_res = myfunctions.make_dir('result')
fname_obr = f'{dir_res}\\обращения_{now}.{ext}'
count = len(open('reestr_numbers.txt').readlines())
numbers = open('reestr_numbers.txt')
url = 'http://pkurp-app-balancer-01.prod.egrn/requests?filter=mine'
logon(url)

pre_lnk = 'http://pkurp-app-balancer-01.prod.egrn/search/tabs/number?search%5Bsection%5D='
post_link = '&search%5Bonly_today%5D=0&search%5Bonly_today%5D=1&search%5Bfilter%5D=&commit=Запросить'
obr = 0

for number in numbers:
    print(f'{obr + 1} из {count}')
    number = number.strip()
    if number == '\n' or number == '':
        continue
    kad_n = number.replace(':', '%3A').replace('/', '%2F')
    link = f'{pre_lnk}{kad_n}{post_link}'
    print(link)
    browser.get(link)
    if "Возникла ошибка на сервере" in browser.page_source:
        print('ошибка сервера, пробую обновить страницу')
        browser.refresh()
    try:
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "*[class^='panel-group item']")))
    except:
        print("не вижу рег записи !!")
    t_body = browser.find_element(By.CSS_SELECTOR, ".tab-3 .panel-group")
    nav = browser.find_elements(By.CSS_SELECTOR, '.scroll-x > .nav-tabs > .li-tab-nav')
    for n in nav:
        if 'Записей о правах, ограничениях и сделках' in n.text:
            n.click()
            reg_count = re.findall(r'\d+', n.text)
            print(f'найдено {reg_count[0]} записей о регистрации')
            break
    reg = t_body.find_elements(By.TAG_NAME, 'tr')
    m = 0
    find = False
    not_actual = False
    print(f'По кадастровому номеру {number} найдено {int(len(reg) / 2)} записей')
    for index_, reg_f in enumerate(reg):
        if (index_ + 1) % 2 != 0:
            # print(f'По номеру права {reg_num} найдено {int(len(reg) / 2)} записей')
            # if 'Актуальная' not in reg_f.text:
            #     continue
            if 'Погашенная' in reg_f.text or 'Архивная' in reg_f.text and 'Запись о вещных правах' in reg_f.text:
                # if check_date_in_range(reg_f.text):
                #     find = True
                #     not_actual = True
                # else:
                #     continue
                find = True
                not_actual = True
                m += 1
                r_r = reg_f.find_element(By.CLASS_NAME, 'js-search-loadable').text
                reg_f.find_element(By.CLASS_NAME, 'js-search-loadable').click()
                sleep(1)
                try:
                    element = WebDriverWait(browser, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "react-form"))
                    )
                except:
                    print("не вижу страницы сведений !!")
                    sys.exit()

        else:
            if find:
                if reg_f.find_element(By.CLASS_NAME, 'pull-right'):
                    # ищем точное совпадение
                    x = browser.find_elements(By.CSS_SELECTOR, '.pull-right:not([class*=" "])')
                    reg_f_ = x[m]
                    print(f'создать корректировку {m} погашенной записи {r_r}')
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
                    forms = browser.find_elements(By.CSS_SELECTOR,
                                                  '.scope .fieldset .form-group')
                    for form in forms:
                        if 'Дата снятия с учета/регистрации' in form.text:
                            date_ = form.find_element(By.CLASS_NAME, 'relative').text
                            form.find_element(By.CLASS_NAME, 'fa-check-square-o').click()
                            break
                    btns = browser.find_elements(By.CLASS_NAME, 'btn-primary')
                    for b in btns:
                        if b.text == 'Далее':
                            b.click()
                            print('далее')
                    browser.find_element(By.CSS_SELECTOR,
                                         "#tech-error-react input[name='edited_attrs[0][new]'][type='string']") \
                        .send_keys(date_)
                    # browser.find_element(By.CSS_SELECTOR,
                    #                      "#tech-error-react input[name='edited_attrs[1][new]'][type='string']") \
                    #     .send_keys(inn)
                    # browser.find_element(By.CSS_SELECTOR,
                    #                      "#tech-error-react input[name='edited_attrs[2][new]'][type='string']") \
                    #     .send_keys(ogrn)

                    # browser.find_element(By.CLASS_NAME, 'fa-plus').click()
                    # browser.find_element(By.CSS_SELECTOR, '#tech-error-react textarea').send_keys(
                    #     f'ид запроса в СМЭВ {name_u}: {m_i}')

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
                        number_obr = res.group()
                        print(number_obr)
                        # записываем номер пакета в файл
                        with open(fname_obr, 'a+') as f:
                            f.write(number + ';' + number_obr + ';' + r_r + '\n')
                    else:
                        print("Не удалось найти строку с номером обращения")
                        sys.exit()
                    browser.close()
                    browser.switch_to.window(browser.window_handles[0])
                    find = False
                    continue
    if not not_actual:
        print(f'По кадастровому номеру {number} нет погашенных записей')
        dir_err = myfunctions.make_dir('ошибки')
        err_file = f'{dir_err}/err_numbers.txt'
        if os.path.isfile(err_file):
            flag = 'a'
        else:
            flag = 'w'
        with open(err_file, flag) as f:
            f.write(f'По кадастровому номеру {number} нет погашенных записей' + '\n')
        # df.at[index, 'номер обращения корректировки'] = 'обращение не создано'
        obr = obr + 1
        continue

    obr = obr + 1
    print(f'[INFO] отработано {obr} ({round(obr / count * 100, 2)} %) обращений из {count},'
          f' осталось {count - obr}')
    # записываем номер пакета в файл
    with open(fname, 'a+') as f:
        f.write(number + '\n')

browser.quit()
input('Всё завершено удачно, нажмите ENTER для выхода')  # чтоб не закрывалась консоль
