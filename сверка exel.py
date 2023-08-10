import pandas as pd


def compare_files(file1, file2, column_name):
    if '.xlsx' not in file1:
        file1 = f'{file1}.xlsx'
    if '.xlsx' not in file2:
        file2 = f'{file2}.xlsx'
    if not column_name:
        column_name = "Рег. № пр./огран."
    # Чтение первого файла
    df1 = pd.read_excel(file1)

    # Чтение второго файла
    df2 = pd.read_excel(file2)

    # Поиск записей из первого файла, которых нет во втором
    df_difference = df1[~df1[column_name].isin(df2[column_name])]

    # Запись результатов в новый файл
    df_difference.to_excel("difference.xlsx", index=False)


if __name__ == '__main__':
    a = input('введите имя первого файла: ')
    b = input('введите имя второго файла: ')
    c = input('по какому столбцу сравнивать, по умолчанию "Рег. № пр./огран.": ')
    compare_files(a, b, c)
    # compare_files("file1.xlsx", "file2.xlsx", "column_name")
    # compare_files("09-08-2023 16_57часть номеров корректировки.xlsx", "09-08-2023 17_44часть номеров корректировки.xlsx", "Рег. № пр./огран.")