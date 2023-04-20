from peewee import *
import configparser
# import os

settings = configparser.ConfigParser()
settings.read('settings.ini', encoding="utf-8")
db_path = settings['db']['path']
##  для бд, хранящихся в виде файла
# if not os.path.isfile(db_path):
#     input(f'[ВНИМАНИЕ!] отсутствует файл базы данных {db_path}, нажмите enter для создания файла ')
conn = SqliteDatabase(db_path)


class BaseModel(Model):
    class Meta:
        database = conn


class Ban(BaseModel):
    numbers = CharField(column_name='Number', unique=True)
    dates = CharField()
    ban_numbers = CharField()
    unban = CharField()


with conn:
    conn.create_tables([Ban])


def add_ban(data):
    with conn:
        for i in data:
            try:
                ban = Ban(numbers=i, dates=data[i]['дата документа'], ban_numbers=data[i]['№ постановления'], unban='')
                ban.save()
            except IntegrityError:
                print(f'обращение {i} уже есть в базе')


def get_number_of_ban(ban_num, date, new=''):
    try:
        number = Ban.get(Ban.ban_numbers == ban_num, Ban.dates == date)
    except:
        number = ''
    if new and number:
        number.unban = new
        number.save()
    if number:
        return number.numbers
    return ''


def update_ban(search_num, new):
    un = Ban.get(Ban.numbers == search_num)
    un.unban = new
    un.save()


def delete_ban(search_num=''):
    if search_num:
        ban = Ban.get(Ban.numbers == search_num)
        ban.delete_instance()
    else:
        unban_del = Ban.select().where(Ban.unban != '')
        for i in unban_del:
            i.delete_instance()


def main():
    print(get_number_of_ban('250050727/7206', "2022-07-16", 'new num'))
    print(get_number_of_ban('340611944/7210', "2022-12-07", 'new num'))


if __name__ == '__main__':
    main()
