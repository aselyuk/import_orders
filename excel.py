# coding: utf-8

import datetime
import re
import xlrd


def read_excel(path, file_name, date_cell, shop_cell, prod_cell):
    file_path = path + file_name
    book = xlrd.open_workbook(file_path)
    sheet = book.sheet_by_index(0)

    max_row = sheet.nrows
    max_col = sheet.ncols

    date_col = date_cell[1] - 1
    date_row = date_cell[0] - 1

    shop_col = shop_cell[1] - 1  # horizontal
    shop_row = shop_cell[0] - 1
    shop_txt = shop_cell[2] - 1

    prod_col = prod_cell[1] - 1  # vertical
    prod_row = prod_cell[0] - 1
    prod_txt = prod_cell[2] - 1

    result = []

    try:
        order_date = get_date_from_string(sheet.cell_value(date_row, date_col))
        if order_date is None:
            raise

        shop_offset = 0

        while order_date is not None and shop_col + shop_offset < max_col:
            prod_offset = 0
            line_number = 0

            while prod_row + prod_offset < max_row:
                prod_value = sheet.cell_value(prod_row + prod_offset, shop_col + shop_offset)
                empty_value = prod_value is None or prod_value == u''

                row = {
                    "orderDate": order_date,
                    "orderTime": 0,
                    "client": 0,
                    "shop": 0,
                    "prod": 0,
                    "uses": False,
                    "exp": 13,
                    "prodType": 0,
                    "codeGroup": 0,
                    "koef": 100,
                    "prodWeight": 0.00,
                    "packSize": 0,
                    "packValue": 0,
                    "prodValue": prod_value if not empty_value else 0,
                    "shopRegion": 0,
                    "done": False,
                    "fileName": file_name,
                    "lineNumber": ++line_number,
                    "theyProd": "",
                    "theyShop": "",
                    "theyProdName": "",
                    "theyShopName": "",
                    "isMgrOrder": False,
                    "manager": 0,
                    "note": "",
                    "isReject": empty_value
                }

                they_prod_code = sheet.cell_value(prod_row + prod_offset, prod_col)
                they_shop_code = sheet.cell_value(shop_row, shop_col + shop_offset)

                they_prod_name = sheet.cell_value(prod_row + prod_offset, prod_txt)
                they_shop_name = sheet.cell_value(shop_txt, shop_col + shop_offset)

                if isinstance(they_prod_code, unicode):
                    they_prod_code = re.sub(r'\s+', ' ', str(they_prod_code))
                if they_prod_code is None or they_prod_code == u'':
                    they_prod_code = 0
                row['theyProd'] = int(they_prod_code)

                if isinstance(they_shop_code, unicode):
                    they_shop_code = get_number_from_string(they_shop_code)
                if they_shop_code is None or they_shop_code == u'':
                    they_shop_code = 0
                row['theyShop'] = int(they_shop_code)

                they_shop_name = re.sub(r'\s+', ' ', they_shop_name)
                they_prod_name = re.sub(r'\s+', ' ', they_prod_name)
                row['theyProdName'] = they_prod_name
                row['theyShopName'] = they_shop_name

                result.append(row)

                prod_offset += 1

            shop_offset += 1

    except Exception as ex:
        print ex
    finally:
        book.release_resources()

    return result


def get_number_from_string(string):
    string = string.lower()
    regexpr = ur'\d+'
    matches = re.search(regexpr, string, re.IGNORECASE)

    number = None
    if matches is not None:
        str_number = matches.group(0)
        if str_number.isnumeric():
            number = int(str_number)

    if number is None:
        print u"Не удалось извлечь число из строки {%s}" % string

    return number


def get_date_from_string(string):
    string = string.lower()
    regexpr = [r"[0-9]{1,2}.[0-9]{1,2}.[0-9]{4}", ur'дата поставки \d{1,2} [а-яА-Я]+ \d{4}']
    date = None
    for j in xrange(0, len(regexpr)):
        matches = re.search(regexpr[j], string, re.IGNORECASE)
        if matches is None:
            continue

        parts = matches.group(0).split(".")
        if len(parts) == 3:
            dd = int(parts[0])
            mm = int(parts[1])
            yyyy = int(parts[2])
            date = datetime.datetime(yyyy, mm, dd, 0, 0, 0)

        if date is None:
            month = {u"января": 1, u"февраля": 2, u"марта": 3,
                     u"апреля": 4, u"мая": 5, u"июня": 6,
                     u"июля": 7, u"августа": 8, u"сентября": 9,
                     u"октября": 10, u"ноября": 11, u"декабря": 12}
            parts = matches.group(0).split(" ")
            dd = 0
            mm = 0
            yyyy = 0
            for k in xrange(0, len(parts)):
                if parts[k].isnumeric():
                    if dd == 0:
                        dd = int(parts[k])
                    elif yyyy == 0:
                        yyyy = int(parts[k])
                if parts[k] in month.keys():
                    mm = month[parts[k]]

            if dd > 0 and mm > 0 and yyyy > 0:
                date = datetime.datetime(yyyy, mm, dd, 0, 0, 0)

    if date is None:
        print u"Не удалось извлечь дату из стрки {%s}" % string

    return date
