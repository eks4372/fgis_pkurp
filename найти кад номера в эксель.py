import pandas as pd
import re
from myfunctions import take_file_name

file = input('введите имя файла: ')
file = take_file_name(file, 'xlsx')
print(f'выбрано имя файла: {file}')
r = input('введите название столбца (record_number): ')
if not r:
    r = 'record_number'
print(f'выбран столбец: {r}')
print(f'чтение файла {file}')
df = pd.read_excel(file)


def extract_cadastral_numbers(text):
    pattern = r'\b(\d{2}:\d{2}:\d{7}:\d+)\b'
    clean_matches = re.findall(pattern, text)
    if clean_matches:
        return clean_matches[0]  # Выбираем первый элемент из списка найденных совпадений
    return ''


for index, row in df.iterrows():
    print(f'{index + 1} из {len(df)}')
    num = row[r]
    df.at[index, 'Кадастровый №'] = extract_cadastral_numbers(num)

out_file = take_file_name(file, 'xlsx', False, True)
print(f'сохраняем файл {out_file["name"]}_.{out_file["ext"]}')
df.to_excel(out_file['name'] + '_' + '.' + out_file['ext'], index=False)
print('завершено')
