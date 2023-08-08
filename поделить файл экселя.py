import pandas as pd

y = ['y', 'yes', 'д', 'да', 'ага']


def split_xlsx(file_path, num_rows, head=False):
    # Читаем исходный файл
    df = pd.read_excel(file_path)

    # Получаем количество строк и столбцов исходного файла
    num_total_rows, num_cols = df.shape

    # Вычисляем количество файлов, на которые нужно разделить исходный файл
    num_files = num_total_rows // num_rows

    # Извлекаем название файла без расширения
    file_name = file_path.split(".xlsx")[0]

    # Разделяем исходный файл на несколько файлов
    for file_num in range(num_files + 1):
        start_row = file_num * num_rows
        end_row = (file_num + 1) * num_rows

        # Если это последний файл, то установим конечную строку, чтобы включить все оставшиеся строки
        if file_num == num_files:
            end_row = num_total_rows

        # Создаем новый DataFrame с нужными строками
        new_df = df.iloc[start_row:end_row]

        # Если head=True, добавляем заголовки таблицы в каждый файл
        if head:
            new_df = pd.concat([df.head(1), new_df])

        # Создаем новый файл с названием "файл_номер.xlsx"
        new_file_name = f"{file_name}_{file_num}.xlsx"
        new_df.to_excel(new_file_name, index=False)


if __name__ == '__main__':
    # split_xlsx("исходный_файл.xlsx", 1000, head=True)
    f = input('введите имя файла: ')
    if '.xlsx' not in f:
        f = f'{f}.xlsx'
    n = int(input('на сколько строк разделить файл: '))
    h = input('содержит ли файл заголовок таблицы? (enter - нет по умолчанию) ')
    if h.lower() in y:
        h = True
    else:
        h = False
    split_xlsx(f, n, h)