import pandas as pd


def processing_file(filename=r"result\обращения.txt", file_out='корректировка прав.xlsx'):
    '''Функция создает файл для бота "решение по правам"'''
    # Чтение файла
    with open(filename, 'r') as file:
        lines = file.readlines()

    # Извлечение номеров обращений и ФИО из строк
    data = []
    for line in lines:
        line = line.strip()
        parts = line.split(';')
        number = parts[0]
        number_obr = parts[1]
        reg = parts[2]
        data.append((number, number_obr, reg))

    # Создание DataFrame
    df = pd.DataFrame(data, columns=['реестровый номер', 'номер обращения корректировки', 'Рег. № пр./огран.'])
    # df = df.drop_duplicates(subset=['номер обращения'])
    df.to_excel(file_out, index=False)
    print(f'создан файл: {file_out}')


t = input(f'введите название исходного файла (по умолчанию "result\обращения.txt"): ')
# processing_file('result\обращения_17-01-2024 08_49.txt')
if t:
    processing_file(t)
else:
    processing_file()
