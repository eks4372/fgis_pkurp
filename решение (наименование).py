from bot_pkurp_start import *
import pandas as pd
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

file = settings['file']['snils_file']
file_out = f'{now}_результат решений.xlsx'
url = 'http://pkurp-app-balancer-01.prod.egrn/requests?filter=mine'
logon(url)

print(f'чтение файла "{file}"')
df = pd.read_excel(file)
pre_lnk = 'http://pkurp-app-balancer-01.prod.egrn/00/requests/'
obr = 0
try:
    for index, row in df.iterrows():
        print(f'{index + 1} из {len(df)}')
        kad_number = row['Кадастровый №']
        number = row['номер обращения корректировки']
        post_link = '/registry_data_containers/statements'
        sved_page = f'{pre_lnk}{number}{post_link}'
        print(sved_page)


        def first():
            browser.get(sved_page)
            try:
                element = WebDriverWait(browser, 300).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "scroll-y"))
                )
            except:
                print("страници Сведения не загрузилась !!")
                if 'Сервис проверки прав доступа недоступен. Обратитесь к администратору' in browser.page_source:
                    first()


        first()

        try:
            element = WebDriverWait(browser, 3).until(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, '.scroll-y .table tbody tr'), 'Изменение сведений'))
        except TimeoutException:
            print("не вижу прав !!!")
        except StaleElementReferenceException:
            print("Элемент стал устаревшим, повторяем попытку...")
            try:
                element = WebDriverWait(browser, 3).until(
                    EC.text_to_be_present_in_element((By.CSS_SELECTOR, '.scroll-y .table tbody tr'),
                                                     'Изменение сведений'))
            except TimeoutException:
                print("не вижу прав !!!")
        t = browser.find_elements(By.CSS_SELECTOR, '.scroll-y .table tbody tr')
        for tr in t:
            if kad_number in tr.text:
                tr.find_element(By.LINK_TEXT, 'Изменение сведений').click()
                sleep(1)
                break
        try:
            element = WebDriverWait(browser, 300).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "*[class^='nav nav-tabs js-fixed']"))
            )
        except:
            print("не вижу меню")
        l_menu = browser.find_elements(By.CSS_SELECTOR, "*[class^='nav nav-tabs js-fixed']")
        for l_menu in l_menu:
            l_menu.find_element(By.PARTIAL_LINK_TEXT, 'Характеристики').click()

            sleep(1)
            break
        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "form-group"))
            )
        except:
            print("не вижу страницы сведений !!")
        f_groups = browser.find_elements(By.CSS_SELECTOR, '#bs-tabs-react-params .scope .form-group')
        # if not f_groups:
        #     f_groups = browser.find_elements(By.CSS_SELECTOR, '.scope .scope .scope .scope .scope')
        for group in f_groups:
            if group.text == '':
                continue
            elif 'Наименование' in group.text:
                wait = WebDriverWait(browser, 10)
                element = wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'fa-check')))
                group.find_element(By.CLASS_NAME, 'fa-check').click()
                break

        nav_tab = browser.find_element(By.CLASS_NAME, 'nav-tabs')
        nav_tab.find_element(By.LINK_TEXT, 'Документы-основания').click()
        print('переходим в документы-основания')
        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "*[class^='icon glyphicon glyphicon-remove-circle']"))
            )
        except:
            print("не крестик !!")


        def check_delete():
            try:
                x = browser.find_elements(By.CSS_SELECTOR,
                                          '#bs-tabs-registry_record_nav-underlying_documents .glyphicon-remove-circle')
            except NoSuchElementException:
                return False
            if len(x) >= 1:
                return True
            return False


        i = 0
        if check_delete():
            print('есть уже документ')
            i = 1
            browser.find_element(By.XPATH,
                                 '/html/body/div[7]/div/form/div[1]/div/div/div[2]/div/div/div/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div').click()
            print('удалили документ-основание')
        btns = browser.find_elements(By.CSS_SELECTOR, '#chooseBaseDocumentsForChangeRecord .btn-default')
        for b in btns:
            if 'Выбрать из обращения' in b.text:
                b.click()
        print('Выбрать из обращения')
        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'in'))
            )
        except:
            print("не вижу страницы с выбором документов-щснований !!")
        check_l = browser.find_element(By.CLASS_NAME, 'tree-scroll') \
            .find_elements(By.CSS_SELECTOR, "*[class^='docs-element js-docs-element']")
        for ch in check_l:
            # print(ch.text)
            if 'Заявление' in ch.text:
                ch.find_element(By.CLASS_NAME, 'js-autofill-element').click()
        browser.find_element(By.CSS_SELECTOR, "*[class^='btn btn-primary js-autofill-submit']").click()
        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "toggle-node"))
            )
        except:
            print("не вижу страницы с заполненными документами-основаниями !!")

        browser.find_element(By.CLASS_NAME, 'js-spinner-transform').click()
        print('сохранить запись')

        # Запускаем проверки
        sleep(1)
        browser.refresh()
        pre_link = 'http://pkurp-app-balancer-01.prod.egrn/72/requests/'
        post_link = '/registry_data_containers/statements#bs-tabs-registry_data-manual_validation_results'
        check_list_link = f'{pre_link}{number}{post_link}'
        print(check_list_link)
        browser.get(check_list_link)
        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "*[class^='btn btn-default btn-primary']"))
            )
        except:
            print("не вижу список проверок !!")


        def start_checks():
            try:
                browser.find_element(By.CSS_SELECTOR, "*[class^='btn btn-default btn-primary']").click()
            except:
                print('не перешел на страницу')
                browser.refresh()
            # проверяем выполнение проверок
            # success = int(browser.find_element(By.CLASS_NAME, 'is-result-success').text)
            # print(f'число успешных проверок: {success}')
            tab = browser.find_element(By.CLASS_NAME, "validation-results")
            while 'Загрузка' in tab.text:
                print('ждем загрузку проверок')
                sleep(1)
            while 'Выполняются проверки' in browser.page_source:
                print('ждем выполнение проверок')
                sleep(1)
            fail = int(browser.find_element(By.CLASS_NAME, 'is-result-fail').text)
            print(f'число непройденных проверок: {fail}')
            if fail > 3:  # число непройденных проверок
                sleep(3)
                start_checks()


        start_checks()
        sleep(1)
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
            try:
                element = WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable(
                        (By.CLASS_NAME, 'js-table-group-toggle-btn')
                    )
                )
            except:
                print("не вижу первичных проверок !!")
            f_cl = browser.find_element(By.CLASS_NAME, 'iframe-padding')
            checks = browser.find_elements(By.CLASS_NAME, 'js-table-group-toggle-btn')
            f_check = checks[0]
            s_check = checks[1]
            f_check.click()
            sleep(0.5)
            s_check.click()

            fchecks = browser \
                .find_elements(By.CSS_SELECTOR,
                               "*[class^='Check js-comment-check js-table-group js-status-done js-result-fail successCheck']")
            schecks = browser \
                .find_elements(By.CSS_SELECTOR,
                               "*[class^='Check js-comment-check js-table-group js-status-scheduled js-result-fail']")
            fchecks += schecks
            return fchecks


        f_checks = take_checks(browser)
        if f_checks:
            while not f_checks[0].text:
                sleep(0.5)
                f_checks = take_checks(browser)
            for f_c in f_checks:
                # print(f_c.text)
                sleep(0.3)
                if 'Проверка формата' in f_c.text or 'Проверка подписи' in f_c.text \
                        or 'Проверка полномочий заявителя' in f_c.text or 'Проверка формы и содержания' in f_c.text:
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
        skips = browser.find_elements(By.CLASS_NAME, 'glyphicon-eye-close')
        for s in skips:
            s.click()  # колоколим

        # возвращяемся на основную страницу
        browser.switch_to.parent_frame()
        print('out frame ok')

        while True:
            try:
                button = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn-next')))
                print('кнопка далее активна')
                break
            except:
                print('ожидание активности кнопки далее')

        sleep(0.5)
        button.click()
        sleep(0.5)
        try:
            browser.find_element(By.LINK_TEXT, 'Далее').click()
        except:
            print('#')
        print('далее')
        sleep(0.5)

        while True:
            try:
                button = WebDriverWait(browser, 10).until_not(EC.element_to_be_clickable((By.CLASS_NAME, 'btn-next')))
                print('кнопка далее неактивна')
                break
            except:
                print('ожидание неактивности кнопки далее...')
                try:
                    browser.find_element(By.LINK_TEXT, 'Далее').click()
                except:
                    print('###')
        sleep(1)

        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, 'registrar_decision_result_approve'))
            )
        except:
            print('не могу выбрать решение')
            try:
                browser.find_element(By.LINK_TEXT, 'Назад').click()
                print('пробую вернуть ся назад')
                sleep(3)
                browser.find_element(By.LINK_TEXT, 'Далее').click()
                print('и снова далее')
            except:
                print('всеравно не могу выбрать решение')
        browser.find_element(By.ID, 'registrar_decision_result_approve').click()
        print('внести сведения в ЕГРН')
        sleep(0.3)
        while not browser.find_element(By.CLASS_NAME, 'btn-next').is_enabled():
            print('кнопка далее не активна')
            sleep(0.3)
        browser.find_element(By.CLASS_NAME, 'btn-next').click()
        print('далее')
        # Alert
        alert_obj = browser.switch_to.alert
        alert_obj.accept()

        while 'service_task' not in browser.current_url:
            print('ждем завершения')
            sleep(0.3)
        df.at[index, 'выполнено'] = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        obr = obr + 1
        print(f'[INFO] отработано {obr} ({round(obr / len(df) * 100, 2)} %) обращений из {len(df)},'
              f' осталось {len(df) - obr}')
        # записываем номер пакета в файл
        with open(fname, 'a+') as f:
            f.write(number + '\n')
except:
    df.to_excel(f'{now}часть номеров решений.xlsx', index=False)
    print('аварийное завершение !')
    sys.exit()
df.to_excel(file_out, index=False)
browser.quit()
input('Всё завершено удачно, нажмите ENTER для выхода')  # чтоб не закрывалась консоль
