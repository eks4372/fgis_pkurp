import os
import pandas as pd
from myfunctions import make_dir
import datetime


def merge_files(directory, file_mask, field_name):
    if not directory:
        directory = os.getcwd()
    if '.xlsx' not in file_mask:
        file_mask = f'{file_mask}.xlsx'
    # Получаем список файлов в указанной директории
    files = [f for f in os.listdir(directory) if f.endswith(file_mask)]

    # Создаем пустой DataFrame для объединения данных
    combined_data = pd.DataFrame()

    # Обрабатываем каждый файл
    for file in files:
        # Открываем файл и загружаем данные
        file_path = os.path.join(directory, file)
        data = pd.read_excel(file_path)

        # Проверяем, есть ли поле в текущем файле
        if field_name in data.columns:
            # Фильтруем строки, где поле не заполнено
            filtered_data = data[data[field_name].notnull()]

            # Объединяем существующие и новые данные
            combined_data = pd.concat([combined_data, filtered_data], ignore_index=True)

    if file_mask == 'корректировки.xlsx':
        out_f = 'корректировка решение.xlsx'
    elif file_mask == 'решений.xlsx':
        out_f = 'на подпись.xlsx'
    elif file_mask == 'подписанные.xlsx':
        d = make_dir('завершенные')
        out_f = f'{d}\\{datetime.datetime.now().strftime("%d-%m-%Y %H_%M")}_завершенные.xlsx'
        # out_f = f'завершенные.xlsx'
    else:
        out_f = 'merged_file.xlsx'
    # Создаем новый файл с объединенными данными
    output_file = os.path.join(directory, out_f)
    combined_data.to_excel(output_file, index=False)

    print(f'Объединенный файл создан: {output_file}')


if __name__ == '__main__':
    d = input(f'укадите папку, по умолчанию {os.getcwd()} :')
    files = input('укажите маку файлов или введите 1 - корректировки, 2 - решений, 3 - подписанные: ')
    if files == '1':
        files = 'корректировки'
        field = 'номер обращения корректировки'
    elif files == '2':
        files = 'решений'
        field = 'выполнено'
    elif files == '3':
        files = 'подписанные'
        field = 'подписано'
    else:
        field = input('укажите поле для валидации: ')
    merge_files(d, files, field)
    input('Всё завершено удачно, нажмите ENTER для выхода')  # чтоб не закрывалась консоль)
    # Пример использования
    # merge_files('/path/to/directory', '_часть.xlsx', 'название поля')
    # merge_files('D:\PycharmProjects\ФГИС_пром', 'часть номеров корректировки.xlsx', 'номер обращения корректировки')
