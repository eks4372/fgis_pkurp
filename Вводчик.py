from bot_pkurp_start import *


def check_exist(identity):
    try:
        browser.find_element(By.ID, identity).find_element(By.CSS_SELECTOR,
                                                           "*[class^='btn btn-default react-add']")
    except NoSuchElementException:
        return False
    return True


url = 'http://pkurp-app-balancer-01.prod.egrn/requests?filter=mine'
logon(url)

encumbrance = settings['words_to_entry']['encumbrance']
content = settings['words_to_entry']['content']
undetermined = settings['words_to_entry']['undetermined']
undefined = settings['words_to_entry']['undefined']
cod_document = settings['words_to_entry']['cod_document']
name_title = settings['words_to_entry']['name_title']

count = len(open('numbers.txt').readlines())
numbers = open('numbers.txt')
p = 0
err = 0
comm = 0
for number in numbers:
    type_face = ''
    skip = False
    people = 0
    reg_num_ = []
    number = number.strip()
    if number == '\n' or number == '':
        continue
    pre_link = 'http://pkurp-app-balancer-01.prod.egrn/72/requests/'
    post_link = '/registry_data_containers/statements'
    sved_page = f'{pre_link}{number}{post_link}'
    print(number)
    # print(people)
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


    def check_manu_objects(txt):
        try:
            browser.find_element(By.LINK_TEXT, txt)
        except NoSuchElementException:
            return False
        return True


    if check_manu_objects('Показать все'):
        browser.find_element(By.LINK_TEXT, 'Показать все').click()
    #####################
    try:
        element = WebDriverWait(browser, 300).until(
            EC.presence_of_element_located((By.CLASS_NAME, "scroll-x"))
        )
    except:
        print("страници Сведения не загрузилась !!")
    try:
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "tbody"))
        )
    except:
        print("таблица Сведения не загрузилась !!")
    try:
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "caret"))
        )
    except:
        print("не вижу кнопки Посмотреть !!")
    tab = browser.find_element(By.CLASS_NAME, "scroll-x")
    t = tab.find_elements(By.TAG_NAME, 'tbody')
    try:
        refresh_ = settings['extra']['refresh']
        if refresh_ == 'no':
            refresh = False
        else:
            refresh = True
    except:
        refresh = True

    refr_links = []
    for btn in t:
        btn.find_element(By.CLASS_NAME, 'caret').click()
        refr_links.append(
            btn.find_element(By.CLASS_NAME, 'dropdown-menu').find_element(By.LINK_TEXT, 'Обновить').get_attribute(
                "href"))
        btn.find_element(By.CLASS_NAME, 'caret').click()
    # собрали список ссылок для обновления
    print(refr_links)

    # обновляем сведения по каждому объекту
    if refresh:
        q = 0
        for lnk in refr_links:
            q = q + 1
            browser.get(lnk)
            print(f'обновляем сведения {q} из {len(refr_links)}')
    ######################
    # проверяем нет ли архивных записей
    try:
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "scroll-x"))
        )
    except:
        print("страници Сведения не загрузилась !!")


    ################

    def check_manu_objects(txt):
        try:
            browser.find_element(By.LINK_TEXT, txt)
        except NoSuchElementException:
            return False
        return True


    if check_manu_objects('Показать все'):
        browser.find_element(By.LINK_TEXT, 'Показать все').click()
    #####################
    try:
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "scroll-x"))
        )
    except:
        print("страници Сведения не загрузилась !!")
    sleep(2)
    tab = browser.find_element(By.CLASS_NAME, "scroll-x")
    t = tab.find_elements(By.TAG_NAME, 'tbody')
    arch_kad_number = []
    for status in t:
        if 'Архив' in status.text:
            # print('text =', status.text)
            print('архивный кадастровый номер = ', status.find_element(By.CLASS_NAME, 'samepage-link').text)
            arch_kad_number.append(status.find_element(By.CLASS_NAME, 'samepage-link').text)
    arch_kad_number_ = list(arch_kad_number)


# проверяем и собираем ссылки для внесения сведений


    def remove_arch(arch_kad_number, browser, many_next):
        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "scroll-y"))
            )
        except:
            print("страници Сведения не загрузилась !!")
            if 'Записи не были сформированы автоматически' in browser.find_element(By.CLASS_NAME,
                                                                                   'js-dropable').text and not arch_kad_number:
                print('актуальных записей нет')
                return False
        while many_next > 0:
            tab = browser.find_element(By.CSS_SELECTOR, "#filtered_containers_table > div > div:nth-child(8) > div")
            while 'Загрузка' in tab.text:
                print('ждем загрузку ограничений-обременений')
                sleep(1)
            t = tab.find_elements(By.CSS_SELECTOR, ".scroll-y .table tbody tr")
            for int in t:
                ############
                # # Удаляем архивные
                for arch_kad_num in arch_kad_number:
                    if arch_kad_num in int.text:
                        print(arch_kad_number)
                        print('##')
                        print(int.text)
                        int.find_element(By.LINK_TEXT, 'Удалить').click()
                        alert_obj = browser.switch_to.alert
                        alert_obj.accept()  # accept()dismiss()
                        print('удалили ', arch_kad_num)
                        # browser.refresh()
                        sleep(1)
                        arch_kad_number.remove(arch_kad_num)
                        if arch_kad_number:
                            remove_arch(arch_kad_number, browser, many_next - 1)
            if many_next > 1:
                browser.find_element(By.CSS_SELECTOR, '.scroll-y  .next>.next').click()  # клик далее
                print('клик далее')
            many_next -= 1


    many_next = ((len(refr_links) - 1) // 10) + 1  # сколько раз нажимать Далее
    if arch_kad_number:
        remove_arch(arch_kad_number, browser, many_next)
        if many_next > 0:
            # .scroll-y  .pagination  li:nth-child(2)> .pagination-link
            browser.find_element(By.CSS_SELECTOR, '.scroll-y  .pagination-link').click()  # на 1 страницу

    # собираем оставшиеся ссылки
    try:
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "scroll-y"))
        )
    except:
        print("страници Сведения не загрузилась !!")
        if 'Записи не были сформированы автоматически' in browser.find_element(By.CLASS_NAME,
                                                                               'js-dropable').text and not arch_kad_number:
            print('актуальных записей нет')
            print('arch_kad_number_', arch_kad_number_)
            if arch_kad_number_:
                for kad_n in arch_kad_number_:
                    myfunctions.comment(browser, number, f'ОН с кадастровым номером {kad_n} архивный')
            p = p + 1
            continue

    ext = 'json'
    path = settings['path']['entering']
    j_file = 'вводчик.json'[:-5]
    file_j = f'{path}\\{j_file}.{ext}'
    with open(file_j, 'r') as file:
        num_data = json.load(file)
        file.close()

    reg_num_list = num_data[number]['номер регистрации']
    reg_num_list_ = list(reg_num_list)
    surname_ = num_data[number]['ФИО'].rsplit(' ')[0]
    surname = myfunctions.surname_for_serch(surname_)
    edit_links = []
    while many_next > 0:
        tab = browser.find_element(By.CSS_SELECTOR, "#filtered_containers_table > div > div:nth-child(8) > div")
        while 'Загрузка' in tab.text:
            print('ждем загрузку ограничений-обременений')
            sleep(1)
        t = tab.find_elements(By.CSS_SELECTOR, ".scroll-y .table tbody tr")
        for i in t:
            if 'Запрещение регистрации' in i.text:
                skip = True
                continue
            edit_links.append(i.find_element(By.LINK_TEXT, 'Внесение сведений').get_attribute("href"))
        if many_next > 1:
            browser.find_element(By.CSS_SELECTOR, '.scroll-y  .next>.next').click()  # клик далее
            print('клик далее')
        many_next -= 1
    # собрали список ссылок для внесения сведений
    print(edit_links)

    #################
    # Вносим сведения
    o = 0
    kad_num_list = []
    if settings['extra']['next'] == 'no':
        next_flag = True
    for link in edit_links:
        break_out_flag = False
        print('осталось ', len(edit_links) - o, " объектов")


        def start():
            global kad_num
            browser.get(link)
            print(link)
            l_menu = browser.find_element(By.CLASS_NAME, 'react-form').find_element(By.CSS_SELECTOR,
                                                                                    "*[class^='nav nav-tabs js-fixed']")

            # Входим в Общие сведения об ограничениях и обременениях
            l_menu.find_element(By.LINK_TEXT, 'Общие сведения об ограничениях и обременениях').click()
            print('Входим в Общие сведения об ограничениях и обременениях')
            # sleep(1)
            try:
                element = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "form-group"))
                )
            except:
                print("не вижу страницы редактирования общих сведений !!")
            f_groups = browser.find_elements(By.CLASS_NAME, 'form-group')
            for group in f_groups:
                # print('w' ,group.text)
                if not group.text:
                    continue
                elif '*Кадастровый номер ОН' in group.text:
                    # print(group.text)
                    # print('___')
                    kad_num = group.find_element(By.CLASS_NAME, 'form-control')
                    if kad_num.text in kad_num_list:
                        print('как так-то ???')
                        print(f'номер {kad_num.text} уже был')
                        start()
                        break
                    else:
                        kad_num_list.append(kad_num.text)

                    print('кад номер ', kad_num.text)  # взяли кадастровый номер
                elif '*Порядковый номер части' in group.text:
                    print("Удаляем порядковый номер части")
                    # sleep(3)
                    browser.find_element(By.XPATH,
                                         '//*[@id="bs-tabs-react-restrictions_encumbrances_data"]'
                                         '/div/div/div/div/div[1]/div/div[3]/div/div[2]/div/div/div/div[1]/div/div[2]').click()
                elif '*Вид зарегистрированного ограничения права или обременения ОН' in group.text:
                    group.find_element(By.ID,
                                       "select2-registry_data_containerdata_attributesrestrictions_encumbrances_data_attributesrestriction_encumbrance_type-container").click()
                    options = browser.find_element(By.CLASS_NAME, 'select2-results__options').find_elements(
                        By.CLASS_NAME,
                        'select2-results__option')
                    # Вносим вид постановления
                    for option in options:
                        if option.text == 'Запрещение регистрации':
                            option.click()
                            break
                elif '*Предмет ограничения/обременения' in group.text:
                    fild = group.find_element(By.ID, 'registry_data_container[data_attributes]'
                                                     '[restrictions_encumbrances_data_attributes][restriction_subject]')
                    fild.clear()
                    fild.send_keys(encumbrance)
                elif '*Содержание' in group.text:
                    fild = group.find_element(By.ID, 'registry_data_container[data_attributes]'
                                                     '[restrictions_encumbrances_data_attributes]'
                                                     '[additional_encumbrance_info_attributes][restrict_info]')
                    fild.clear()
                    fild.send_keys(content)
                    break


        start()
        # print(kad_num_list)
        l_menu = browser.find_element(By.CLASS_NAME, 'react-form').find_element(By.CSS_SELECTOR,
                                                                                "*[class^='nav nav-tabs js-fixed']")

        f_scope = browser.find_elements(By.CLASS_NAME, 'scope')
        n = 0
        for scope in f_scope:
            if not scope.text:
                continue
            # print('w', scope.text)
            elif 'Ограничиваемые права' in scope.text:
                n = n + 1
                # print(n)
                # print(scope.text)
                try:
                    element = WebDriverWait(browser, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "*[class^='btn btn-default']"))
                    )
                except:
                    print("не вижу кнопки Выбрать из сведений !!")

                if n == 2:
                    scope.find_element(By.CSS_SELECTOR, "*[class^='btn btn-default']").click()
                    print('Выбрать из сведений')
                    try:
                        element = WebDriverWait(browser, 3).until(
                            EC.presence_of_element_located((By.TAG_NAME, 'tbody'))
                        )
                    except:
                        print("не вижу формы !!")


                    # Цепляем права
                    def check_manu_objects(txt):
                        try:
                            browser.find_element(By.LINK_TEXT, txt)
                        except NoSuchElementException:
                            return False
                        return True


                    def check_next(cl):
                        try:
                            browser.find_element(By.CLASS_NAME, cl)
                        except NoSuchElementException:
                            return False
                        return True


                    if check_manu_objects('Показать все'):
                        browser.find_element(By.LINK_TEXT, 'Показать все').click()
                        sleep(1)
                    elif check_next('next'):
                        try:
                            element = WebDriverWait(browser, 100).until(
                                EC.presence_of_element_located((By.CLASS_NAME, 'min-160'))
                            )
                        except:
                            print('форма не загрузилась')
                            sys.exit()
                        serch_forms = browser.find_elements(By.CLASS_NAME, 'min-200')
                        for s_f in serch_forms:
                            if s_f.text == 'Правообладатель':
                                s_f.find_element(By.TAG_NAME, 'input').send_keys(surname)
                        serch_forms = browser.find_elements(By.CLASS_NAME, 'min-160')
                        for s_f in serch_forms:
                            if s_f.text == 'Кадастровый номер':
                                s_f.find_element(By.TAG_NAME, 'input').send_keys(kad_num.text)
                        sleep(3)
                        # Если записей всёравно очень много
                    if not check_manu_objects('Показать все') and check_next('next'):
                        serch_forms = browser.find_elements(By.CLASS_NAME, 'min-200')
                        for s_f in serch_forms:
                            if s_f.text == 'Правообладатель':
                                s_f.find_element(By.TAG_NAME, 'input').clear()
                                s_f.find_element(By.TAG_NAME, 'input').send_keys(surname_)
                                sleep(3)
                    ##########
                    if check_manu_objects('Показать все'):
                        browser.find_element(By.LINK_TEXT, 'Показать все').click()
                        sleep(1)

                    try:
                        element = WebDriverWait(browser, 10).until(
                            EC.presence_of_element_located((By.TAG_NAME, 'tbody'))
                        )
                    except:
                        if 'Актуальные записи не найдены' in browser.page_source:
                            serch_forms = browser.find_elements(By.CLASS_NAME, 'min-200')
                            for s_f in serch_forms:
                                if s_f.text == 'Правообладатель':
                                    s_f.find_element(By.TAG_NAME, 'input').send_keys(Keys.CONTROL + "a")
                                    s_f.find_element(By.TAG_NAME, 'input').send_keys(Keys.DELETE)
                        else:
                            print('не загрузился список субъектов')
                            sys.exit()
                    sleep(0.5)


                    def find_reg(browser):
                        t_body = browser.find_elements(By.TAG_NAME, 'tbody')
                        find = 0
                        for t_b in t_body:
                            if kad_num.text in t_b.text and num_data[number]['ФИО'].lower().replace('ё', 'е').replace(
                                    ' ', '').replace('"', '') in t_b.text.lower().replace('ё', 'е') \
                                    .replace(' ', '').replace('"', ''):
                                for reg_n in reg_num_list:
                                    if reg_n in t_b.text:
                                        print(t_b.text)
                                        try:
                                            reg_num_list_.remove(reg_n)
                                        except:
                                            print('список пуст')
                                        t_b.find_element(By.CLASS_NAME, 'js-autofill-element').click()
                                        # sleep(1)
                                        find = 1
                        if find == 0:
                            return False
                        return True


                    find = False
                    if find_reg(browser):
                        browser.find_element(By.XPATH,
                                             '//*[@id = "complexTypeModal"]/div/div/div[2]/div/div/div/a[2]').click()
                    else:
                        chans = 0
                        while chans < 3:

                            if chans == 1 and settings['extra']['advansed_serch'] == 'yes':
                                for r, n in zip(num_data[number]["номер регистрации"], num_data[number]["вид права"]):
                                    window_before = browser.window_handles[0]
                                    browser.switch_to.new_window()  # новая вкладка
                                    face_f = myfunctions.take_face_(browser, r, num_data[number]["ФИО"],
                                                                    num_data[number]["ИНН"], n)
                                    if face_f[0] == 'Актуальная':
                                        type_face = face_f[1]
                                        num_data[number]["тип правообладателя"] = type_face
                                        # if face_f[1] != 'фио':  # если юр лицо - заменяем ФИО
                                        if face_f[2] != '-':
                                            old_fio = num_data[number]["ФИО"]
                                            num_data[number]["ФИО"] = face_f[2]
                                        # print(num_data)
                                        surname = myfunctions.surname_for_serch(face_f[2].split()[0])
                                        print(surname)
                                        print(type_face)
                                        print(face_f[2])
                                        print(num_data[number]["ФИО"])
                                        browser.close()  # закрыть текущую вкладку
                                        browser.switch_to.window(window_before)  # переключились обратно
                                        serch_forms = browser.find_elements(By.CLASS_NAME, 'min-200')
                                        for s_f in serch_forms:
                                            if s_f.text == 'Правообладатель':
                                                s_f.find_element(By.TAG_NAME, 'input').clear()
                                                s_f.find_element(By.TAG_NAME, 'input').send_keys(surname)
                                        if check_manu_objects('Показать все'):
                                            browser.find_element(By.LINK_TEXT, 'Показать все').click()
                                            sleep(1)
                                        break
                                    else:
                                        browser.close()  # закрыть текущую вкладку
                                        browser.switch_to.window(window_before)  # переключились обратно
                                        try:
                                            reg_num_list_.remove(r)
                                        except:
                                            print(f'не очистили {r}')
                                        # myfunctions.comment(browser, number, f'номер права {r} архивный')
                                        if face_f[0] == 'Погашенная':
                                            reg_num_.append(r)
                                        continue

                                ##########################
                            sleep(3)
                            if find_reg(browser):
                                browser.find_element(By.XPATH,
                                                     '//*[@id = "complexTypeModal"]/div/div/div[2]/div/div/div/a[2]').click()
                                find = True
                                break
                            else:
                                print(f'попытка {chans + 1} найти {num_data[number]["ФИО"]}')
                                chans = chans + 1
                                sleep(2)

                        if not find:
                            print(f'[ERROR] правообладатель {num_data[number]["ФИО"]} не найден !!!')
                            print(f'номер данного обращения {number}')
                            # sleep(100)
                            # записываем номер пакета в файл
                            with open(fname, 'a+') as f:
                                f.write(number + '\n')
                                f.close()
                                # и в ошибки
                            dir_err = myfunctions.make_dir('пропущенные пакеты')
                            err_file = f'{dir_err}/err_numbers.txt'
                            if os.path.isfile(err_file):
                                flag = 'a'
                            else:
                                flag = 'w'
                            with open(err_file, flag) as f:
                                f.write(
                                    f'{number} [ERROR] правообладатель {num_data[number]["ФИО"]} '
                                    f'не найден в обращении в объекте {kad_num.text}!!' + '\n')
                            if settings['extra']['next'] == 'yes':
                                myfunctions.comment(browser, number,
                                                    f'правообладатель {num_data[number]["ФИО"]}'
                                                    f' не найден в обращении в объекте {kad_num.text}')
                                browser.back()
                                browser.back()
                            break_out_flag = True
                            next_flag = False
                            err = err + 1
                            if reg_num_:
                                for r in reg_num_:
                                    print(f'пишем комменты про рег номер {r}')
                                    myfunctions.comment(browser, number, f'номер права {r} погашенный')
                                    browser.back()
                                    browser.back()
                            try:
                                fio = old_fio
                            except:
                                old_fio = False
                            if settings['extra']['advansed_serch'] == 'yes' and old_fio:
                                num_data[number]["ФИО"] = old_fio
                            break
                            # sys.exit()
                    # sleep(3)
            elif 'Срок действия' in scope.text:
                btn = True


                # проверяем наличие кнопки установления срока в неустановлен
                def it_is(btn):
                    try:
                        scope.find_element(By.CSS_SELECTOR, "*[class^='btn btn-default react-add']")
                    except:
                        btn = False
                    return btn


                btn = it_is(btn)
                # print(btn)

                if btn:
                    scope.find_element(By.CSS_SELECTOR, "*[class^='btn btn-default react-add']").click()
                    print('клик по не установлен')
                # sleep(1)
                fild = scope.find_element(By.ID, "registry_data_container[data_attributes]"
                                                 "[restrictions_encumbrances_data_attributes]"
                                                 "[period_attributes][no_period]")
                fild.clear()
                fild.send_keys(undetermined)
                # sleep(3)
                break

        if break_out_flag:
            continue
        #################
        if people == 0 and not type_face:
            f_groups = browser.find_elements(By.CLASS_NAME, 'form-group')
            for f_g in f_groups:
                if not f_g:
                    continue
                elif '*Номер регистрации вещного права' in f_g.text:
                    form = f_g.find_element(By.CLASS_NAME, 'form-control')
                    href = form.find_element(By.TAG_NAME, 'a').get_attribute("href")

                    face_f = myfunctions.take_face(browser, href)
                    type_face = face_f[0]
                    num_data[number]["тип правообладателя"] = type_face
                    if face_f[1] != 'фио':  # если юр лицо - заменяем ФИО
                        num_data[number]["ФИО"] = face_f[1]
                    # print(num_data[number])
                    # sleep(30)
                    browser.back()
                    browser.back()
                    people = 1
        ###########################
        # Входим в Сведения о лицах
        l_menu.find_element(By.LINK_TEXT, 'Сведения о лицах').click()
        print('Входим в Сведения о лицах')
        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, "bs-tabs-react-restrict_parties"))
            )
        except:
            print("не вижу страницы редактирования лиц !!")
        ##############################
        # Удаляем все сведения о лицах
        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "*[class^='icon glyphicon glyphicon-remove-circle']"))
            )
        except:
            print("не крестик !!")
        browser.find_element(By.XPATH,
                             '//*[@id="bs-tabs-react-restrict_parties"]/div/div/div/div/div[1]/div/div[2]').click()
        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "*[class^='btn btn-default react-add']"))
            )
        except:
            print("не заполнить сведения о лицах !!")
        bs = browser.find_elements(By.CSS_SELECTOR, "*[class^='btn btn-default react-add']")
        for b in bs:
            if 'Сведения о лицах' in b.text:
                b.click()
        #############################
        if check_exist("bs-tabs-react-restrict_parties"):
            btns = browser.find_element(By.ID, "bs-tabs-react-restrict_parties") \
                .find_elements(By.CSS_SELECTOR, "*[class^='btn btn-default react-add']")
            for btn in btns:
                if 'Сведения о лицах, в пользу которых установлены ограничения права и обременения ОН' in btn.text:
                    btn.click()
                elif 'Сведения о лицах, права которых ограничиваются и обременяются ОН' in btn.text:
                    btn.click()
        # sleep(1)
        f_groups = browser.find_elements(By.CLASS_NAME, 'form-group')
        for f_g in f_groups:
            # print(f_g.text)
            if not f_g.text:
                continue
            elif '*Тип лица, в пользу которых установлены ограничения права и обременения объекта недвижим' in f_g.text:
                print("ставим тип лица")

                f_g.find_element(By.CSS_SELECTOR, "*[class^='select2-selection select2-selection--single']").click()
                options = browser.find_element(By.CLASS_NAME, 'select2-results__options') \
                    .find_elements(By.CLASS_NAME, 'select2-results__option')
                for option in options:
                    if option.text == 'Не определено':
                        option.click()
                        break

            elif '*Тип лица, права которого ограничиваются и обременяются объекты недвижимости' in f_g.text:
                f_g.find_element(By.CSS_SELECTOR, "*[class^='select2-selection select2-selection--single']").click()
                options = browser.find_element(By.CLASS_NAME, 'select2-results__options') \
                    .find_elements(By.CLASS_NAME, 'select2-results__option')
                for option in options:
                    if option.text == 'Правообладатель':
                        option.click()
                        break

        scopes = browser.find_elements(By.CLASS_NAME, 'scope')
        # print('scopes ', scopes)
        l1 = 0
        for scope in scopes:
            # print('scope ' , scope.text)
            if 'Лицо, в пользу которого установлены ограничения права и обременения объекта' in scope.text and l1 == 0:
                l1 = l1 + 1
                # print("##########")
                sel = Select(browser.find_element(By.CSS_SELECTOR, "*[class^='form-control js-choice']"))
                sel.select_by_visible_text('Не определено')
                btns = browser.find_element(By.ID, "bs-tabs-react-restrict_parties") \
                    .find_elements(By.CSS_SELECTOR, "*[class^='btn btn-default react-add']")
                for btn in btns:
                    if 'Не определено' in btn.text:
                        btn.click()
                f_groups = browser.find_elements(By.CLASS_NAME, 'form-group')
                for f_g in f_groups:
                    if f_g.text == '*Не определено':
                        f_g.find_element(By.ID,
                                         'registry_data_container[data_attributes][restrict_parties_attributes]'
                                         '[restricted_rights_parties_attributes][0][subject_attributes][undefined]') \
                            .send_keys(undefined)

            elif 'Лицо, права которого ограничиваются и обременяются объекты недвижимости' in scope.text:
                sel = Select(browser.find_element(By.CSS_SELECTOR, "*[class^='form-control js-choice']"))
                sel.select_by_visible_text(num_data[number]['тип правообладателя'])
                btns = browser.find_element(By.ID, "bs-tabs-react-restrict_parties") \
                    .find_elements(By.CSS_SELECTOR, "*[class^='btn btn-default']")
                # sleep(5)

                for btn in btns:
                    if 'Выбрать из существующих' in btn.text:
                        btn.click()

                break
        # sleep(1)

        # Цепляем субъекты
        print('Цепляем субъекты')
        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "*[class^='modal in']"))
            )
        except:
            print("страници субъектов не загрузилась !!")
        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'tbody'))
            )
        except:
            print("страници субъектов не загрузилась !!")
        try:
            element = WebDriverWait(browser, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'js-autofill-element'))
            )
        except:
            print("страници субъектов не загрузилась !!")


        def take_tbody(browser):
            t_body = browser.find_elements(By.TAG_NAME, 'tbody')
            return t_body


        t_body = take_tbody(browser)
        while not t_body[0].text:
            sleep(0.5)
            t_body = take_tbody(browser)

        if check_manu_objects('Показать все'):
            browser.find_element(By.LINK_TEXT, 'Показать все').click()
            sleep(1)
            t_body = take_tbody(browser)
        elif check_next('next'):
            try:
                element = WebDriverWait(browser, 100).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'min-160'))
                )
            except:
                print('форма не загрузилась')
                sys.exit()
            serch_forms = browser.find_elements(By.CLASS_NAME, 'min-160')
            for s_f in serch_forms:
                name = num_data[number]['ФИО'].rsplit(' ')[1]
                if 'е' in name.lower() or 'ё' in name.lower():
                    if 'ё' == name.lower()[0] or 'е' == name.lower()[0]:
                        name = name[1:]
                    if 'ё' in name.lower():
                        name = name.lower().rsplit('ё')[0]
                    else:
                        if 'е' in name.lower():
                            name = name.lower().rsplit('е')[0]
                if s_f.text == 'Фамилия':
                    s_f.find_element(By.TAG_NAME, 'input').send_keys(surname)
                elif s_f.text == 'Имя' and check_next('next') and not check_manu_objects('Показать все'):
                    s_f.find_element(By.TAG_NAME, 'input').send_keys(name)
                elif s_f.text == 'Название':
                    s_f.find_element(By.TAG_NAME, 'input').send_keys(surname)
            sleep(3)
            t_body = take_tbody(browser)

            if check_manu_objects('Показать все'):
                browser.find_element(By.LINK_TEXT, 'Показать все').click()
                sleep(1)
                t_body = take_tbody(browser)
        ##################
        try:
            element = WebDriverWait(browser, 100).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'js-autofill-element'))
            )
        except:
            print('форма не загрузилась')


        def serch_s_revers_(serch: str, type):
            res = ''
            res_ = ''
            t_body = take_tbody(browser)
            for s in t_body[::-1]:
                if s:
                    if serch in s.text.lower().replace('ё', 'е').replace(' ', '').replace('"', ''):
                        res = s
                    if type == "Физическое лицо":
                        if serch in s.text.lower().replace('ё', 'е') \
                                .replace(' ', '').replace('"', '') and myfunctions.serch_snils(s.text):
                            res_ = s
                            return res_, True
                    if type == "Юридическое лицо":
                        if serch in s.text.lower().replace('ё', 'е') \
                                .replace(' ', '').replace('"', '') and myfunctions.serch_ogrn(s.text):
                            res_ = s
                            return res_, True
            if res:
                return res, False
            else:
                return False


        subject = serch_s_revers_(num_data[number]['ФИО'].lower().replace('ё', 'е').replace(' ', '').replace('"', ''),
                                  type_face)
        if not subject:
            print('записи не найдены !')
            sys.exit()
        else:
            try:
                element = WebDriverWait(browser, 30).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'js-autofill-element'))
                )
            except:
                print("не могу выбрать (( !!")
            subject[0].find_element(By.CLASS_NAME, 'js-autofill-element').click()
            print(subject[0].text)
            # sleep(10)
        if type_face == "Физическое лицо":
            if not subject[1]:
                print('нет СНИЛСа')
                snils_err = myfunctions.make_dir('snils_ogrn')
                snils_file = f'{snils_err}/snils_numbers.txt'
                if os.path.isfile(snils_file):
                    flag = 'a'
                else:
                    flag = 'w'
                with open(snils_file, flag) as f:
                    f.write(
                        f'{number} [ВНИМАНИЕ] у правообладателя {num_data[number]["ФИО"]} нет СНИЛСа !!' + '\n')
        if type_face == "Юридическое лицо":
            if not subject[1]:
                print('нет ОГРНа')
                snils_err = myfunctions.make_dir('snils_ogrn')
                snils_file = f'{snils_err}/ogrn_numbers.txt'
                if os.path.isfile(snils_file):
                    flag = 'a'
                else:
                    flag = 'w'
                with open(snils_file, flag) as f:
                    f.write(
                        f'{number} [ВНИМАНИЕ] у правообладателя {num_data[number]["ФИО"]} нет ОГРНа !!' + '\n')

                # sleep(1)
        # sleep(5)
        browser.find_element(By.XPATH,
                             '//*[@id="subjectsModal"]/div/div/div[2]/div/div/div/a').click()

        # Входим в Документы-основания
        l_menu.find_element(By.LINK_TEXT, 'Документы-основания').click()
        print('Входим в Документы-основания')
        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, "bs-tabs-react-underlying_documents"))
            )
        except:
            print("не вижу страницы редактирования документов !!")
            ##############################
            # Удаляем все документы
            try:
                element = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "*[class^='icon glyphicon glyphicon-remove-circle']"))
                )
            except:
                print("не крестик !!")


        def check_delete(xpaph):
            try:
                browser.find_element(By.XPATH, xpaph)
            except NoSuchElementException:
                return False
            return True


        i = 0
        if check_delete('//*[@id="bs-tabs-react-underlying_documents"]/div/div/div/div/div[1]/div/div[2]/div'):
            # print('-TRUE-')
            i = 1
            browser.find_element(By.XPATH,
                                 '//*[@id="bs-tabs-react-underlying_documents"]/div/div/div/div/div[1]/div/div[2]/div').click()

        #############################
        if check_exist("bs-tabs-react-underlying_documents"):
            btns = browser.find_element(By.ID, "bs-tabs-react-underlying_documents").find_elements(By.CSS_SELECTOR,
                                                                                                   "*[class^='btn btn-default']")
            for btn in btns:
                if btn.text == 'Выбрать из обращения':
                    btn.click()
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
                    browser.find_element(By.CSS_SELECTOR, "*[class^='btn btn-primary js-autofill-submit']").click()
        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "form-group"))
            )
        except:
            print("не вижу страницы редактирования общих сведений !!")
        f_groups = browser.find_elements(By.CLASS_NAME, 'form-group')
        for group in f_groups:
            if not group.text:
                continue
            elif '*Код документа' in group.text:
                print('ставим Код документа')
                group.find_element(By.CSS_SELECTOR, "*[class^='select2-selection select2-selection--single']").click()
                browser.find_element(By.CLASS_NAME, "select2-search__field").send_keys(cod_document)
                options = browser.find_element(By.CLASS_NAME, 'select2-results__options') \
                    .find_elements(By.CLASS_NAME, 'select2-results__option')
                for option in options:
                    if option.text == 'Постановление судебного пристава-исполнителя':
                        option.click()
                        break
            elif '*Наименование' in group.text:
                print('ставим наименование')
                fild = group.find_element(By.ID,
                                          f'registry_data_container[data_attributes][underlying_documents_attributes]'
                                          f'[{i}][document_name]')
                fild.clear()
                fild.send_keys(name_title)
            elif '*Номер документа' in group.text:
                print('ставим Номер документа')
                fild = group.find_element(By.ID,
                                          f'registry_data_container[data_attributes][underlying_documents_attributes]'
                                          f'[{i}][document_number]')
                fild.clear()
                fild.send_keys(num_data[number]["идентификатор"])
            elif 'Особые отметки' in group.text:
                print('ставим Особые отметки')
                fild = group.find_element(By.ID,
                                          f'registry_data_container[data_attributes][underlying_documents_attributes]'
                                          f'[{i}][special_marks]')
                fild.clear()
            elif 'Дополнительная информация' in group.text:
                print('ставим Дополнительная информация')
                fild = group.find_element(By.ID,
                                          f'registry_data_container[data_attributes][underlying_documents_attributes]'
                                          f'[{i}][additional_information]')
                fild.clear()
                fild.send_keys(num_data[number]["№ постановления"])
                break
        o = o + 1
        print('отработано ' + str(o) + ' объектов ' + 'из ' + str(len(edit_links)))
        # Нажимаем сохранить запись
        browser.find_element(By.CSS_SELECTOR,
                             "*[class^='btn btn-default btn btn-primary js-spinner-transform']").click()
        print('Сохраняем')
        sleep(1)

    ###########################
    if settings['extra']['next'] == 'no':
        if not next_flag:
            continue
    #################
    if reg_num_:
        for r in reg_num_:
            print(f'пишем комменты про рег номер {r}')
            myfunctions.comment(browser, number, f'номер права {r} погашенный')
            browser.back()
            browser.back()
    if not skip:
        print('неактуальные рег. записи = ', reg_num_list_)
        print('архивные кад. номера = ', arch_kad_number_)
        if arch_kad_number_:
            dir_comm = myfunctions.make_dir('пакеты с комментариями')
            comm_file = f'{dir_comm}/comm_numbers.txt'
            if os.path.isfile(comm_file):
                flag = 'a'
            else:
                flag = 'w'
            with open(comm_file, flag) as f:
                f.write(f'{number} оставлен комментарий' + '\n')
            comm = comm + 1

            for kad_n in arch_kad_number_:
                myfunctions.comment(browser, number, f'ОН с кадастровым номером {kad_n} архивный')

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
        f_check = browser.find_element(By.CLASS_NAME, 'js-table-group-toggle-btn')

        f_check.click()

        f_checks = browser \
            .find_elements(By.CSS_SELECTOR,
                           "*[class^='Check js-comment-check js-table-group js-status-done js-result-fail successCheck']")
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
    sleep(1)

    # записываем номер пакета в файл
    with open(fname, 'a+') as f:
        f.write(number + '\n')
        f.close()

    p = p + 1
    if settings['extra']['next'] == 'no':
        print(
            f'[INFO] отработано {p + err} ({round((p + err) / count * 100, 2)} %) обращений из {count},'
            f' осталось {count - p - err}')
    else:
        print(f'[INFO] отработано {p} ({round((p) / count * 100, 2)} %) обращений из {count}, осталось {count - p}')
    if err:
        print(f'[ВНИМАНИЕ] есть пакеты с ошибками {err} шт., проверьте файл "{dir_err}/err_numbers.txt"')
    if comm:
        print(
            f'[ВНИМАНИЕ] есть пакеты с записанными комментариями {comm} шт.,'
            f' проверьте файл "{dir_comm}/comm_numbers.txt"')
if err:
    with open(err_file, 'a') as f:
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
