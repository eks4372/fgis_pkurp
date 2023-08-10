import os
import pandas as pd


def combine_files(directory, file_mask='_подписанные'):
    if not directory:
        directory = os.getcwd()
    if '.xlsx' not in file_mask:
        file_mask = f'{file_mask}.xlsx'
    # Получаем список файлов, соответствующих заданной маске
    files = [f for f in os.listdir(directory) if f.endswith(file_mask)]

    if len(files) < 2:
        print("Недостаточно файлов для объединения.")
        return

    # Создаем пустой DataFrame для объединенных данных
    combined_data = pd.DataFrame()

    # Объединяем данные из всех файлов
    for file in files:
        # Читаем файл и объединяем его данные с общим датафреймом
        data = pd.read_excel(os.path.join(directory, file))
        combined_data = pd.concat([combined_data, data], ignore_index=True)

    # Создаем новый объединенный файл в Excel формате
    combined_file_path = os.path.join(directory, "combined.xlsx")
    combined_data.to_excel(combined_file_path, index=False)

    print("Объединение файлов завершено. Создан файл: {}".format(combined_file_path))


if __name__ == '__main__':
    d = input(f'укадите папку, по умолчанию {os.getcwd()} :')
    files = input('укажите маку файлов, по умолчанию _подписанные.xlsx: ')
    combine_files(d,files)
    # combine_files("путь_к_директории", "_подписанные.xlsx")
    # combine_files("D:\PycharmProjects\ФГИС_пром", "часть номеров корректировки.xlsx")
    # combine_files(file_mask="часть номеров корректировки.xlsx")