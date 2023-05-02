from bot_pkurp_start import *
import orm
import re

url = 'http://pkurp-app-balancer-01.prod.egrn/requests?filter=mine'
logon(url)

count = len(open('numbers_unban.txt').readlines())
numbers = open('numbers_unban.txt')

cod_document = settings['words_to_entry']['cod_document']
name_title_ = settings['words_to_entry']['name_title_']
option_title = settings['words_to_entry']['option_title']


def writ_err(file, err_text):
    # записываем номер пакета в файл
    with open(fname, 'a+') as f:
        f.write(number + '\n')
        f.close()
        # и в ошибки
    dir_err = myfunctions.make_dir(file)
    err_file = f'{dir_err}/err_numbers.txt'
    if os.path.isfile(err_file):
        flag = 'a'
    else:
        flag = 'w'
    with open(err_file, flag) as f:
        f.write(err_text)


def wri_comm():
    if os.path.isfile(comm_file):
        flag = 'a'
    else:
        flag = 'w'
    with open(comm_file, flag) as f:
        f.write(f'{number} оставлен комментарий' + '\n')


dir_err = 'пропущенные пакеты снятий'
p = 0
err = 0
comm = 0
dir_comm = myfunctions.make_dir('пакеты с комментариями')
comm_file = f'{dir_comm}/comm_numbers.txt'
for number in numbers:
    number = number.strip()
    if number == '\n' or number == '':
        continue
    pre_link = 'http://pkurp-app-balancer-01.prod.egrn/72/requests/'
    post_link = '/registry_data_containers/statements'
    sved_page = f'{pre_link}{number}{post_link}'

    ext = 'json'
    path = settings['path']['uban']
    j_file = 'снятия.json'[:-5]
    file_j = f'{path}\\{j_file}.{ext}'
    with open(file_j, 'r') as file:
        num_data = json.load(file)

    ban_number = orm.get_number_of_ban(num_data[number]['№ постановления об аресте'],
                                       num_data[number]['дата постановления об аресте'], number)
    if not ban_number:
        print(f'[WARNING!] по снятию {number} не найдено обращение по наложению ареста')
        writ_err(dir_err, err_text=f'по снятию {number} не найдено обращение по наложению ареста' + '\n')
        err = err + 1
        continue
    ban_sved_page = f'{pre_link}{ban_number}{post_link}'

    first(ban_sved_page)
    print(f'[INFO] номер обращения с арестом: {ban_number}')
    print(f'[INFO] страница : {ban_sved_page}')
    try:
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.scroll-y .table'))
        )
    except:
        print("страници Сведения ограничений !!")
        if 'Записи, не сформированные автоматически' in browser.find_element(By.ID, 'empty_statement').text:
            print(f'[WARNING!] в обращении по наложению ареста {ban_number} нет записей')
            writ_err(dir_err,
                     err_text=f'по снятию {number} в обращении по наложению ареста {ban_number} нет записей' + '\n')
            err = err + 1
            continue
    ban = browser.find_element(By.ID, 'restrict').text
    pattern = r'(\d*\))'
    n = re.search(pattern, ban)
    # print(n)
    many_next = ((int(n[0][:-1]) - 1) // 10) + 1  # сколько раз нажимать Далее
    nums_ban = []
    while many_next > 0:
        tab = browser.find_element(By.CSS_SELECTOR, "#filtered_containers_table > div > div:nth-child(8) > div")
        while 'Загрузка' in tab.text:
            print('ждем загрузку ограничений-обременений')
            sleep(1)
        t = tab.find_elements(By.CSS_SELECTOR, ".scroll-y .table tbody tr")
        for i in t:
            if 'Запрещение регистрации' in i.text or 'ограничения' in i.text:
                nums_ban.append(i.find_element(By.CSS_SELECTOR, ':nth-child(5)').text)
        if many_next > 1:
            browser.find_element(By.CSS_SELECTOR, '.scroll-y  .next>.next').click()  # клик далее
            print('клик далее')
        many_next -= 1

    print(nums_ban)
    first(sved_page)

    print(f'[INFO] номер обращения : {number}')
    print(f'[INFO] страница : {sved_page}')

    kad_numbers = []


    def remove_ban(many):
        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "scroll-y"))
            )
        except:
            print("страници Сведения не загрузилась !!")
            if 'Записи не были сформированы автоматически' in browser.find_element(By.CLASS_NAME, 'js-dropable').text:
                print('актуальных записей нет')
                return False
        tab = browser.find_element(By.CSS_SELECTOR, "#filtered_containers_table > div > div:nth-child(8) > div")
        while 'Загрузка' in tab.text:
            print('ждем загрузку ограничений-обременений')
            sleep(1)
        t = tab.find_elements(By.CSS_SELECTOR, ".scroll-y .table tbody tr")
        for i in t:
            ############
            # Удаляем
            if 'Погашение' in i.text:
                k = i.find_element(By.CSS_SELECTOR, 'td:nth-child(4)')
                u = i.find_element(By.CSS_SELECTOR, 'td:nth-child(5)')
                kad_numbers.append(k.text)
                print(f'найдено погашение кадастрового номера {k.text} {u.text}')
                # continue
            # print('##')
            # print(i.text)
            i.find_element(By.LINK_TEXT, 'Удалить').click()
            alert_obj = browser.switch_to.alert
            alert_obj.accept()  # accept()dismiss()
            print(f'удалили {i}')
            # browser.refresh()
            sleep(1)
            many -= 1
            if many:
                remove_ban(many)


    try:
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.scroll-x .table'))
        )
    except:
        print("страници Сведения ограничений !!")
    try:
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#filtered_containers_table > div > div:nth-child(8) > div"))
        )
        ban = browser.find_element(By.ID, 'restrict').text
        pattern = r'(\d*\))'
        n = re.search(pattern, ban)
        many_ban = int(n[0][:-1])  # сколько записей удалить
        print(f'[INFO] найдено {many_ban} записей для удаления')
        remove_ban(many_ban)
    except:
        if browser.find_element(By.ID, 'empty_statement'):
            print('Записей для удаления нету')

    if check_manu_objects('Показать все'):
        browser.find_element(By.LINK_TEXT, 'Показать все').click()

    try:
        element = WebDriverWait(browser, 300).until(
            EC.presence_of_element_located((By.CLASS_NAME, "scroll-x"))
        )
    except:
        print("страници Сведения не загрузилась !!")
    try:
        element = WebDriverWait(browser, 150).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".js-table-filter-group-scope > tbody"))
        )
    except:
        print("таблица Сведения не загрузилась !!")

    num_kad = browser.find_elements(By.CSS_SELECTOR, ".js-table-filter-group-scope > tbody tr")
    len_num_kad = len(num_kad)


    def for_each_kad_number():
        if check_manu_objects('Показать все'):
            browser.find_element(By.LINK_TEXT, 'Показать все').click()
        global err, comm
        try:
            element = WebDriverWait(browser, 150).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".js-table-filter-group-scope > tbody"))
            )
        except:
            print("таблица Сведения не загрузилась !!")
        list_zayavleniy = browser.find_elements(By.CSS_SELECTOR, ".js-table-filter-group-scope > tbody tr")
        for z in list_zayavleniy:
            link = z.find_element(By.CLASS_NAME, 'samepage-link')
            kad_number = link.text
            if kad_number in kad_numbers:
                continue
            elif kad_number not in kad_numbers:
                kad_numbers.append(kad_number)
                link.click()
                print(f'открываем кадастровый номер: {kad_number}')
                try:
                    element = WebDriverWait(browser, 100).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR,
                                                        ".is-scroll-x > div > div > div:nth-child(2)"
                                                        " > div > div:nth-child(4) h4"))
                    )
                    while 'Ограничения/обременения' not in element.text:
                        print(element.text)
                        sleep(1)
                except:
                    print("Ограничения/обременения не загрузилась !!")
                fild = browser.find_element(By.CSS_SELECTOR,
                                            '.is-scroll-x > div > div > div:nth-child(2) > div > '
                                            'div:nth-child(4) [data-table = "restrict_record"]')

                div = browser.find_element(By.CSS_SELECTOR,
                                           '.is-scroll-x > div >div > div:nth-child(2) > div > div:nth-child(4)')
                for r in nums_ban:
                    if kad_number in r:
                        fild.send_keys(r)
                        print(f'ищем номер регистрации ограничения {r}')
                        sleep(1)
                        while 'Загрузка' in div.text:
                            print('загрузка')
                            sleep(1)
                        break
                else:
                    print(f'[WARNING !] для кадастрового номера {kad_number} номер регистрации запрещения не найден')
                    browser.find_element(By.CSS_SELECTOR, '.is-scroll-x .close').click()
                    myfunctions.comment(browser, number, f'для кадастрового номера {kad_number}'
                                                         f' номер регистрации запрещения не найден')
                    wri_comm()
                    comm = comm + 1
                    browser.get(sved_page)
                    break
                if 'Актуальные записи не найдены' in div.text:
                    print(f'[WARNING !] номер регистрации {r} не найден')
                    browser.find_element(By.CSS_SELECTOR, '.is-scroll-x .close').click()
                    window_before = browser.window_handles[0]
                    browser.switch_to.new_window()  # новая вкладка
                    pre_lnk = 'http://pkurp-app-balancer-01.prod.egrn/search/tabs/record?search%5Brecord.law_number%5D='
                    reg_n = r.replace(':', '%3A').replace('/', '%2F')
                    post_link = '&commit=Запросить'
                    link = f'{pre_lnk}{reg_n}{post_link}'
                    print(link)
                    browser.get(link)
                    try:
                        element = WebDriverWait(browser, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "*[class^='panel-group item']")))
                    except:
                        print("не вижу рег записи !!")
                        if 'Сведения, удовлетворяющие запросу, не найдены.' in browser.page_source:
                            print(f'[ERROR] рег. запись не найдена !!!')
                            writ_err(dir_err, err_text=f'в обращении {number} не найден номер записи {r}')
                            err = err + 1
                            break  # return 'error'
                    t_body = browser.find_element(By.CSS_SELECTOR, "*[class^='panel-group item']")
                    if 'Погашенная' in t_body.find_element(By.TAG_NAME, 'tr').text:
                        print(f'[INFO] найдена погашенная запись {r}')
                    else:
                        writ_err(dir_err, err_text=f'в обращении {number} что-то не так с номером записи {r}')
                        err = err + 1
                        return 'error'
                    browser.close()  # закрыть текущую вкладку
                    browser.switch_to.window(window_before)  # переключились обратно
                    myfunctions.comment(browser, number, f'номер регистрации {r} погашен')
                    wri_comm()
                    comm = comm + 1
                    browser.get(sved_page)
                    break
                tr = div.find_elements(By.TAG_NAME, 'tr')

                for t in tr:
                    # print(t.text)
                    if 'Просмотреть' in t.text and r in t.text:
                        t.find_element(By.CLASS_NAME, 'caret').click()
                        sleep(0.3)
                        t.find_element(By.CLASS_NAME, 'dropdown-menu').find_element(By.LINK_TEXT, 'Погасить')
                        # print('---')
                        lis = t.find_element(By.CLASS_NAME, 'dropdown-menu').find_elements(By.TAG_NAME, 'li')
                        for li in lis:
                            # print(li.get_attribute('value'))
                            # print(li.text)
                            if 'Погасить' in li.text:
                                print(li.find_element(By.TAG_NAME, 'ul').find_element(By.TAG_NAME, 'a').get_attribute(
                                    'href'))
                                element = li.find_element(By.TAG_NAME, 'ul').find_element(By.TAG_NAME, 'a')
                                browser.execute_script("arguments[0].click();",
                                                       element)  # выполняем скрипт JS из данного меню
                                break
                            else:
                                continue
                        # внутри записи

                        navi = browser.find_elements(By.CSS_SELECTOR, '.tabs-content  a')
                        for n in navi:
                            if 'Документы-основания' in n.text:
                                n.click()
                                break
                            else:
                                continue
                        btns = browser.find_elements(By.CSS_SELECTOR,
                                                     '#chooseBaseDocumentsForChangeRecord .btn-default')
                        for btn in btns:
                            if 'Выбрать из обращения' in btn.text:
                                btn.click()
                                break
                            else:
                                continue
                        try:
                            element = WebDriverWait(browser, 10).until(
                                EC.presence_of_element_located((By.CLASS_NAME, 'tree-scroll'))
                            )
                        except:
                            print("не вижу страницы редактирования документов !!")
                        check_l = browser.find_element(By.CLASS_NAME, 'tree-scroll') \
                            .find_elements(By.CSS_SELECTOR, "*[class^='docs-element js-docs-element']")

                        for ch in check_l:
                            # print(ch.text)
                            if 'pdf' in ch.text:
                                ch.find_element(By.CLASS_NAME, 'js-autofill-element').click()
                                browser.find_element(By.CSS_SELECTOR,
                                                     "*[class^='btn btn-primary js-autofill-submit']").click()
                                break

                        # заполняем форму документа-основания
                        try:
                            element = WebDriverWait(browser, 10).until(
                                EC.presence_of_element_located((By.CLASS_NAME, "form-group"))
                            )
                        except:
                            print("не вижу страницы редактирования общих сведений !!")
                        divs = browser.find_elements(By.CSS_SELECTOR, '#bs-tabs-react-underlying_documents .form-group')
                        for div in divs:
                            if div.text == "":
                                continue
                            elif 'Код документа' in div.text:
                                div.find_element(By.CLASS_NAME, 'glyphicon-pencil').click()
                                sleep(0.3)
                                print('ставим Код документа')
                                sel = div.find_element(By.CSS_SELECTOR,
                                                       "*[class^='select2-selection select2-selection--single']")
                                sel.click()
                                sleep(0.3)
                                while 'Совпадений не найдено' in browser.find_element(By.CLASS_NAME,
                                                                                      'select2-results__options').text:
                                    print('не загрузился список документов')
                                    sel.click()
                                    sleep(0.2)
                                    sel.click()
                                    sleep(1)
                                browser.find_element(By.CLASS_NAME, "select2-search__field").send_keys(cod_document)
                                # sleep(50)
                                options = browser.find_element(By.CLASS_NAME, 'select2-results__options') \
                                    .find_elements(By.CLASS_NAME, 'select2-results__option')
                                for option in options:
                                    if option.text == option_title:
                                        option.click()
                                        sleep(0.5)
                                        break
                            elif 'Наименование' in div.text:
                                print('вносим наименование')
                                fild = div.find_element(By.ID, 'registry_data_container'
                                                               '[underlying_documents_holder_attributes]'
                                                               '[underlying_documents_attributes][0][document_name]')
                                fild.clear()
                                fild.send_keys(name_title_)
                            elif 'Номер документа' in div.text:
                                print('ставим номер документа')
                                fild = div.find_element(By.ID, 'registry_data_container'
                                                               '[underlying_documents_holder_attributes]'
                                                               '[underlying_documents_attributes][0][document_number]')
                                fild.clear()
                                fild.send_keys(num_data[number]["идентификатор"])
                                break
                        browser.find_element(By.CSS_SELECTOR, '.page-footer > button').click()
                        print('сохраняем')
                        sleep(3)
                        print('возвращаемся в "сведения"')
                        while browser.current_url != sved_page:
                            browser.get(sved_page)
                            sleep(1)
                        # for_iach_kad_number()
                        break
                break

    while len_num_kad != 0:
        print(f'кадастровых номеров осталось {len_num_kad}')
        n = for_each_kad_number()
        if n == 'error':
            break
        len_num_kad -= 1
    # if n == 'error':
    #     continue

        # Запускаем проверки
    # sleep(1)
    # browser.refresh()
    pre_link = 'http://pkurp-app-balancer-01.prod.egrn/72/requests/'
    post_link = '/registry_data_containers/statements#bs-tabs-registry_data-manual_validation_results'
    check_list_link = f'{pre_link}{number}{post_link}'
    print(check_list_link)
    browser.get(check_list_link)
    browser.refresh()
    try:
        element = WebDriverWait(browser, 100).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "*[class^='btn btn-default btn-primary']"))
        )
    except:
        print("не вижу список проверок !!")


    def start_checks():
        browser.find_element(By.CSS_SELECTOR, "*[class^='btn btn-default btn-primary']").click()
        # try:
        #     browser.find_element(By.CSS_SELECTOR, "*[class^='btn btn-default btn-primary']").click()
        # except:
        #     print('не перешел на страницу')
        #     browser.refresh()


    start_checks()
    sleep(1)

    # Идём на стадию Проведение проверок
    pre_link = 'http://pkurp-app-balancer-01.prod.egrn/72/requests/'
    post_link = '/validations/statements'
    check_list_link = f'{pre_link}{number}{post_link}'
    print(check_list_link)
    browser.get(check_list_link)
    try:
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'table-container'))
        )
    except:
        print("не вижу КУВД !!")
    table = browser.find_element(By.CLASS_NAME, 'table-container')
    table.find_element(By.CSS_SELECTOR, "*[class^='js-iframe-trigger js-validations']").click()
    try:
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
    except:
        print("не вижу проверок !!")
    iframe = browser.find_elements(By.TAG_NAME, 'iframe')[1]
    # переключаемся в найденный фрейм
    print('in frame')
    browser.switch_to.frame(iframe)
    print('in ok')


    def take_checks(browser):
        # global done
        f_check = browser.find_element(By.CLASS_NAME, 'js-table-group-toggle-btn')
        element = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, 'js-table-group-toggle-btn')
            )
        )

        f_check.click()

        f_checks = browser.find_elements(By.CSS_SELECTOR,
                                         "*[class^='Check js-comment-check js-table-group "
                                         "js-status-done js-result-fail successCheck']")
        return f_checks


    f_checks = take_checks(browser)
    if f_checks:
        while not f_checks[0].text:
            sleep(0.5)
            f_checks = take_checks(browser)
        for f_c in f_checks:
            # print(f_c.text)
            sleep(0.3)
            if 'Проверка формата' in f_c.text or 'Проверка подписи' in f_c.text:
                f_c.find_element(By.CLASS_NAME, 'switch').click()
                sleep(0.3)
                try:
                    f_c.find_element(By.CSS_SELECTOR,
                                     # "*[class^='text optional  js-comment-check-textarea form-control']").clear()
                                     "*[class^='form-control text optional  js-comment-check-textarea']").clear()
                    f_c.find_element(By.ID, 'outer_validation_result_comment')
                    btn = f_c.find_element(By.CLASS_NAME, 'pull-left').find_element(By.TAG_NAME, 'button')
                    print(btn.text)  # Подтвердить
                    btn.click()
                except:
                    print('не удалось очистить комментарии')
                    sleep(3)
    else:
        try:
            # f_c.find_element(By.CSS_SELECTOR,
            #                  "*[class^='text optional  js-comment-check-textarea form-control']").clear()
            f_c.find_element(By.ID, 'outer_validation_result_comment')
            btn = f_c.find_element(By.CLASS_NAME, 'pull-left').find_element(By.TAG_NAME, 'button')
            print(btn.text)  # Подтвердить
            btn.click()
        except:
            print('не удалось очистить комментарии')
            sleep(3)

    # возвращяемся на основную страницу
    browser.switch_to.parent_frame()
    print('out frame ok')

    browser.find_element(By.LINK_TEXT, 'Далее').click()
    print('Далее')
    sleep(1)

    # записываем номер пакета в файл
    with open(fname, 'a+') as f:
        f.write(number + '\n')
        f.close()
    if settings['db']['delete_used'] == 'yes':
        # orm.update_ban(ban_number, number) сделано в get_number_of_bun
        orm.delete_ban(ban_number)
    p = p + 1

    print(f'[INFO] отработано {p + err} ({round((p + err) / count * 100, 2)} %) обращений из {count}'
          f' осталось {count - p - err}')
if err:
    with open(f'{dir_err}/err_numbers.txt', 'a') as f:
        f.write('-' * 10 + '\n')
    myfunctions.explore(dir_err)
    os.startfile(f'{dir_err}\err_numbers.txt', 'open')
if comm:
    with open(comm_file, 'a') as f:
        f.write('-' * 10 + '\n')
    myfunctions.explore(dir_comm)
    os.startfile(f'{dir_comm}\comm_numbers.txt', 'open')
browser.quit()
input('Всё завершено удачно, нажмите ENTER для выхода')  # чтоб не закрывалась консоль
