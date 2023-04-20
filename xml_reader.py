import urllib.request
import xml.etree.ElementTree as ET


def xml_parser(url_xml):
    xml_file = urllib.request.urlopen(url_xml)
    root_node = ET.parse(xml_file).getroot()
    # print(root_node)
    cod = root_node.find(".//DocCode").text  # Вид постановления
    fio = root_node.find(".//DebtorName").text  # ФИО
    ip_num = root_node.find(".//IPNum").text  # идентификарот постановления
    num = root_node.find(".//DocNum").text  # Номер постановления
    osp = root_node.find(".//OSPCode").text  # Код структурного подразделения
    i_key = root_node.find(".//InternalKey").text  # Уникальный ид
    try:
        inn = root_node.find(".//DebtorINN").text  # ИНН
    except:
        inn = '-'
    kad_number = []
    kad_numbers = root_node.findall(".//KadastrN")
    for number in kad_numbers:
        if kad_number.count(number.text) < 1:
            kad_number.append(number.text)
    reg_number = []
    reg_numbers = root_node.findall(".//regNumber")
    reg_name = []
    reg_names = root_node.findall(".//rightName")
    for number, name in zip(reg_numbers, reg_names):
        if reg_number.count(number.text) < 1:
            reg_number.append(number.text)
            reg_name.append(name.text)
    doc_date = root_node.find(".//DocDate").text  # дата постановления
    if cod == 'O_IP_ACT_ENDBAN_REG':
        ban_num = root_node.find(".//RestrDocNumber").text  # номер нажожения ареста
        ban_date = root_node.find(".//RestrDocDate").text  # дата нажожения ареста
        return cod, fio, ip_num, num, osp, i_key, kad_number, reg_number, inn, reg_name, doc_date, ban_num, ban_date
    else:
        return cod, fio, ip_num, num, osp, i_key, kad_number, reg_number, inn, reg_name, doc_date, '-', '-'
