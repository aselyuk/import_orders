# coding: utf-8

import os
from datetime import datetime
import utils
import excel
import ads
import sql_query as sql
import send_mail
import orders

if __name__ == "__main__":
    print "Start..."

    config = utils.get_config()
    admin_email = config["admin_email"]

    ads_config = config["ads"]
    ads.set_ads_settings(ads_config)

    email_config = config["email_robot"]

    excel_defaults = config["excel_defaults"]
    name = excel_defaults["name"]
    excel_path = excel_defaults["excel_path"]
    date_row_col = excel_defaults["date_row_col"]
    prod_row_col = excel_defaults["prod_row_col"]
    shop_row_col = excel_defaults["shop_row_col"]
    use_own_prod_code = excel_defaults["use_own_prod_code"]
    use_own_shop_code = excel_defaults["use_own_shop_code"]
    zero_as_rejects = excel_defaults["zero_as_rejects"]
    client_code = excel_defaults["client_code"]
    need_second_route = excel_defaults["need_second_route"]
    need_split_orders = excel_defaults["need_split_orders"]
    from_manager = excel_defaults["from_manager"]

    excel_config = config["excel"]

    for x in xrange(0, len(excel_config)):
        xls_cfg = excel_config[x]

        if not xls_cfg["enabled"]:
            continue

        name = utils.get_cfg_value(xls_cfg, "name", name)
        excel_path = utils.get_cfg_value(xls_cfg, "excel_path", excel_path)
        excel_path = excel_path if excel_path.endswith("\\") else excel_path + "\\"
        processed_path = excel_path + "processed\\"
        errors_path = excel_path + "errors\\"

        if not os.path.isdir(excel_path):
            continue
        files = os.listdir(excel_path)
        xls = filter(lambda a: a.endswith('.xls') or a.endswith('.xlsx'), files)
        if len(xls) == 0:
            print "Folder [%s] is empty! Move next...\n" % excel_path
            continue

        emails = [admin_email]
        email = xls_cfg.get("email")
        if email is not None and len(email) > 0:
            emails.extend(email)

        date_row_col = utils.get_cfg_value(xls_cfg, "date_row_col", date_row_col)
        prod_row_col = utils.get_cfg_value(xls_cfg, "prod_row_col", prod_row_col)
        shop_row_col = utils.get_cfg_value(xls_cfg, "shop_row_col", shop_row_col)
        use_own_prod_code = utils.get_cfg_value(xls_cfg, "use_own_prod_code", use_own_prod_code)
        use_own_shop_code = utils.get_cfg_value(xls_cfg, "use_own_shop_code", use_own_shop_code)
        zero_as_rejects = utils.get_cfg_value(xls_cfg, "zero_as_rejects", zero_as_rejects)
        client_code = utils.get_cfg_value(xls_cfg, "client_code", client_code)
        need_second_route = utils.get_cfg_value(xls_cfg, "need_second_route", need_second_route)
        need_split_orders = utils.get_cfg_value(xls_cfg, "need_split_orders", need_split_orders)
        from_manager = utils.get_cfg_value(xls_cfg, "from_manager", from_manager)

        for i in xrange(0, len(xls)):
            current_excel_file = xls[i]

            print "Current file:", current_excel_file
            orders_list = excel.read_excel(excel_path, current_excel_file,
                                           date_row_col, shop_row_col, prod_row_col)

            count = len(orders_list)
            print "Got %d. " % count + ("" if count > 0 else "Move next...")

            order_date = orders_list[0]["orderDate"]
            print "Order date:", order_date

            if orders.already_loaded(current_excel_file, order_date):
                print "Already loaded [%s, %s]! Move next...\n" % (
                    order_date, current_excel_file
                )
                # todo: send email alert
                utils.move_file(excel_path + current_excel_file, errors_path)
                continue

            # todo: FSP
            # need for FSP
            # loaded_prods = ads.select_sql(sql.SQL_ALREADY_LOADED_PROD, None, (order_date, "orderdate"))

            print "Get products from db"
            if use_own_prod_code:
                sql_str = sql.SQL_PRODS
                prods = ads.select_sql(sql_str)
            else:
                sql_str = sql.SQL_PRODS_CLIENT
                prods = ads.select_sql(sql_str, None, (client_code, client_code))

            orders.set_our_prod_codes(orders_list, prods)

            print "Get shops from db"
            if name == "FERMER":
                sql_str = sql.SQL_SHOPS_FERMER
                shops = ads.select_sql(sql_str)
            elif use_own_shop_code:
                sql_str = sql.SQL_SHOPS
                shops = ads.select_sql(sql_str)
            else:
                sql_str = sql.SQL_SHOPS_CLIENT
                shops = ads.select_sql(sql_str, None, (client_code, "client"))

            orders.set_our_shop_codes(orders_list, shops)

            print "Set order time"
            orders.set_time_from_exp(orders_list)

            print "Before modification:", len(orders_list)

            if from_manager:
                orders.set_property(orders_list, "isMgrOrder", True)

            if not zero_as_rejects:
                print "Before delete rejects:", len(orders_list)
                orders.delete_rejects(orders_list)
                print "After delete rejects:", len(orders_list)

            if need_second_route and order_date.date() == datetime.now().date():
                print "Set order time for second routes"
                orders.set_ordertime(orders, 12)
            elif order_date.date() <= datetime.now().date():
                print "Order date (%s) must be > (%s)" % (
                    order_date.date().strftime("%Y-%m-%d"), datetime.now().date().strftime("%Y-%m-%d")
                )
                # todo: send email alert
                utils.move_file(excel_path + current_excel_file, errors_path)
                continue

            if need_split_orders:
                print "Before split : %d" % len(orders_list)
                orders.split_orders_by_percent(orders_list)
                print "After split: %d" % len(orders_list)

            print "After modification:", len(orders_list)

            print "Find errors"
            errors = orders.get_errors(orders_list)
            if len(errors) > 0:
                email_text = ""
                for error in errors:
                    email_text += error.values()[0] + "\n"
                print "Send email alert"
                send_mail.send(email_config, ["mr.null@list.ru"],
                               "Ошибки при примеме заказов из excel",
                               email_text,
                               [excel_path + current_excel_file]
                               )

            print "Insert orders into db"
            inserted_rows = orders.insert_orders(orders_list)
            print "Inserted %d of %d" % (inserted_rows, len(orders_list))

            orders.set_single_pack_value(order_date)

            print "Move file"
            utils.move_file(excel_path + current_excel_file, processed_path)

            print "Well done!!!\n"

    print "Finish!!!"
