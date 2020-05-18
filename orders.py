# coding: utf-8

import utils
import math
import sql_query as sql
import ads


def delete_rejects(arr_orders):
    if not isinstance(arr_orders, list) or len(arr_orders) == 0:
        return

    orders_without_rejects = []
    for j in xrange(0, len(arr_orders)):
        if not arr_orders[j]["isReject"]:
            orders_without_rejects.append(arr_orders[j])
    del arr_orders[:]
    arr_orders.extend(orders_without_rejects)


def set_our_shop_codes(arr_orders, arr_shops):
    if not (isinstance(arr_orders, list) and isinstance(arr_shops, tuple) and
            len(arr_orders) > 0 and len(arr_shops) > 0):
        return

    fields = arr_shops[1]
    last_they_shop = -1
    index, shop = None, None
    for j in xrange(0, len(arr_orders)):
        they_shop = arr_orders[j]["theyShop"]
        if last_they_shop != they_shop:
            index, shop = utils.find_by_key(arr_shops, "theyCode", they_shop)
            if index is None or shop is None:
                continue
        arr_orders[j]["shop"] = shop[fields["ourCode"]]
        arr_orders[j]["shopRegion"] = shop[fields["shopRegion"]]
        arr_orders[j]["client"] = shop[fields["kodorg"]]
        arr_orders[j]["manager"] = shop[fields["manager"]]
        if arr_orders[j]["shopRegion"] == 1:
            arr_orders[j]["orderTime"] = 5
        else:
            arr_orders[j]["orderTime"] = 0
        last_they_shop = arr_orders[j]["theyShop"]


def set_our_prod_codes(arr_orders, arr_prods):
    if not (isinstance(arr_orders, list) and isinstance(arr_prods, tuple) and
            len(arr_orders) > 0 and len(arr_prods) > 0):
        return

    fields = arr_prods[1]
    last_they_prod = -1
    index, prod = None, None
    for j in xrange(0, len(arr_orders)):
        they_prod = arr_orders[j]["theyProd"]
        if last_they_prod != they_prod:
            index, prod = utils.find_by_key(arr_prods, "theyCode", they_prod)
            if index is None or prod is None:
                continue
        arr_orders[j]["prod"] = prod[fields["ourCode"]]
        arr_orders[j]["koef"] = prod[fields["koef"]]
        arr_orders[j]["packSize"] = float(prod[fields["packSize"]])
        arr_orders[j]["prodWeight"] = float(prod[fields["prodWeight"]])
        arr_orders[j]["uses"] = prod[fields["uses"]]
        arr_orders[j]["exp"] = prod[fields["exp"]]
        arr_orders[j]["codeGroup"] = prod[fields["codeGroup"]].strip()
        arr_orders[j]["prodType"] = prod[fields["prodType"]]
        if arr_orders[j]["packSize"] > 0:
            arr_orders[j]["packValue"] = math.floor(arr_orders[j]["prodValue"] / arr_orders[j]["packSize"])


def split_orders_by_percent(arr_orders, split_percent=0.3):
    if not (isinstance(arr_orders, list) and len(arr_orders) > 0):
        return

    result_arr = []

    for j in xrange(0, len(arr_orders)):
        cnt = 0
        order = utils.copy_row(arr_orders[j])

        if order["prodValue"] > 0 and 0 < order["packSize"] < order["packValue"] and \
                order["prodValue"] % order["packSize"] > math.floor(order["packSize"] * split_percent):
            prod_value = order["prodValue"] % order["packSize"]
            order["prodValue"] -= prod_value

            new_order = utils.copy_row(order)
            new_order["prodValue"] = prod_value
            new_order["packValue"] = 1
            result_arr.append(new_order)
            cnt += new_order["prodValue"]

        result_arr.append(order)
        cnt += order["prodValue"]

        if arr_orders[j]["prodValue"] != cnt:
            print "Value changed: %d -> %d" % (arr_orders[j]["prodValue"], cnt)

    del arr_orders[:]
    arr_orders.extend(result_arr)


def set_ordertime(arr_orders, ordertime=0):
    if not (isinstance(arr_orders, list) and len(arr_orders) > 0):
        return

    for j in xrange(0, len(arr_orders)):
        order = arr_orders[j]
        if order["shopRegion"] == 5 and order["orderTime"] != ordertime:
            print "Order time changed: %d -> %d" % (order["orderTime"], ordertime)
            order["orderTime"] = ordertime


def set_time_from_exp(arr_orders):
    if not (isinstance(arr_orders, list) and len(arr_orders) > 0):
        return

    prod_types = [10, 49, 60]

    for j in xrange(0, len(arr_orders)):
        order = arr_orders[j]
        exp = order["exp"]
        time = order["orderTime"]
        region = order["shopRegion"]
        prod_type = order["prodType"]

        if exp == 14:
            time = 4 if prod_type in prod_types and region == 1 else 11
        elif exp == 15:
            time = 2 if region == 1 else 8
        elif exp == 13:
            time = 5 if region == 1 else 0

        if arr_orders[j]["orderTime"] != time:
            arr_orders[j]["orderTime"] = time


def set_property(arr_orders, property_name, value):
    if not (isinstance(arr_orders, list)):
        return

    properties = arr_orders[0].keys()
    if not (property_name in properties):
        return

    for j in xrange(0, len(arr_orders)):
        print "Set property [%s]: " % property_name, arr_orders[j][property_name], " -> ", value
        arr_orders[j][property_name] = value


def insert_orders(arr_orders):
    if not (isinstance(arr_orders, list) and len(arr_orders) > 0):
        return

    insert_stmt = sql.SQL_INSERT_PROD
    sql_string = ""
    last_shop = arr_orders[0]["shop"]
    inserted = 0

    for j in xrange(0, len(arr_orders)):
        order = arr_orders[j]
        if order["shop"] == 0 or order["prod"] == 0 or order["uses"] != 2:
            continue

        if last_shop != order["shop"] and sql_string != "":
            inserted += ads.exec_sql(sql_string)
            sql_string = ""

        tmp = insert_stmt
        tmp = tmp.replace(":orderDate", order["orderDate"].strftime("%Y-%m-%d"))
        tmp = tmp.replace(":orderTime", str(order["orderTime"]))
        tmp = tmp.replace(":client", str(order["client"]))
        tmp = tmp.replace(":packSize", str(order["packSize"]))
        tmp = tmp.replace(":packValue", str(order["packValue"]))
        tmp = tmp.replace(":prodValue", str(order["prodValue"]))
        tmp = tmp.replace(":theyProdName", order["theyProdName"][:50])
        tmp = tmp.replace(":theyProd", str(order["theyProd"]))
        tmp = tmp.replace(":theyShopName", order["theyShopName"][:50])
        tmp = tmp.replace(":theyShop", str(order["theyShop"]))
        tmp = tmp.replace(":prodWeight", str(order["prodWeight"]))
        tmp = tmp.replace(":fileName", order["fileName"])
        tmp = tmp.replace(":lineNumber", str(order["lineNumber"]))
        tmp = tmp.replace(":shop", str(order["shop"]))
        tmp = tmp.replace(":prod", str(order["prod"]))
        tmp = tmp.replace(":isMgrOrder", str(order["isMgrOrder"]))
        tmp = tmp.replace(":manager", str(order["manager"]))
        tmp = tmp.replace(":isReject", str(order["isReject"]))
        tmp = tmp.replace(":note", order["note"][:255])

        sql_string += tmp

        last_shop = order["shop"]

    if sql_string != "":
        inserted += ads.exec_sql(sql_string)

    return inserted


def set_single_pack_value(date, pack_amnt=1):
    return ads.exec_sql(sql.SQL_SET_PACK, None, (pack_amnt, date))


def already_loaded(filename, date):
    res, fields = ads.select_sql(sql.SQL_ALREADY_LOADED, None, (filename, date))
    return res is not None and res[0][fields["cnt"]] > 0


def get_errors(arr_orders):
    if not (isinstance(arr_orders, list) and len(arr_orders) > 0):
        return

    errors_prod = []
    errors_shop = []
    errors_order = []
    errors_uses = []
    error_list = []

    for j in xrange(0, len(arr_orders)):
        order = arr_orders[j]
        prod = order["prod"]
        they_prod = order["theyProd"]
        they_prod_name = order["theyProdName"]
        shop = order["shop"]
        they_shop = order["theyShop"]
        they_shop_name = order["theyShopName"]
        prod_value = order["prodValue"]

        if prod == 0 and shop > 0 and prod_value > 0:
            if not utils.has_dict_key(errors_prod, they_prod):
                errors_prod.append({they_prod: u"Неизвестная продукция: (%d) %s"
                                               % (they_prod, they_prod_name)})
            if not utils.has_dict_key(errors_order, shop):
                errors_order.append({shop: u"Заказ с неизвестной продукцией: (%d) %s"
                                           % (they_shop, they_shop_name)})

        if shop == 0 and prod > 0:
            if not utils.has_dict_key(errors_shop, they_shop):
                errors_shop.append({they_shop: u"Неизвестный покупатель: (%d) %s"
                                               % (they_shop, they_shop_name)})
        if prod > 0 and order["uses"] != 2 and prod_value > 0:
            if not utils.has_dict_key(errors_uses, prod):
                errors_uses.append({prod: u"Продукция (%d) %s не производится!!!"
                                          % (they_prod, they_prod_name)})

    if len(errors_shop) > 0:
        error_list.extend(errors_shop)
    if len(errors_uses) > 0:
        error_list.extend(errors_uses)
    if len(errors_prod) > 0:
        error_list.extend(errors_prod)
    if len(errors_order) > 0:
        error_list.extend(errors_order)

    return error_list
