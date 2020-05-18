# coding: utf-8

import adsdb

DATA_SOURCE = ""
LOGIN = ""
PASSWORD = ""


def set_ads_settings(ads_config):
    ads_data_source = ads_config["data_source"]
    ads_login = ads_config["login"]
    ads_password = ads_config["password"]

    global DATA_SOURCE
    global LOGIN
    global PASSWORD

    DATA_SOURCE = ads_data_source
    LOGIN = ads_login
    PASSWORD = ads_password

    print "Database: '%s'" % DATA_SOURCE


def get_connection(data_source=DATA_SOURCE, login=LOGIN):
    if isinstance(data_source, unicode):
        data_source = data_source.encode("utf-8")

    if isinstance(login, unicode):
        login = login.encode("utf-8")

    if data_source == "":
        data_source = DATA_SOURCE.encode("utf-8")
    if login == "":
        login = LOGIN.encode("utf-8")

    conn = None
    try:
        conn = adsdb.connect(DataSource=data_source, UserID=login, ServerType='local or remote')
    except Exception as ex:
        print ex.args
    return conn


def select_sql(sql, connection=None, parameters=()):
    conn = connection
    result = None
    fields = {}
    curs = None

    try:
        if conn is None:
            conn = get_connection()
        curs = conn.cursor()
        curs.execute(sql, parameters)
        result = curs.fetchall()
        for x in range(0, len(curs.description)):
            fields.update({str(curs.description[x][0]): x})
    except Exception as ex:
        print ex
    finally:
        if connection is None and curs is not None:
            curs.close(True)
            conn.close()

    return result, fields


def exec_sql(sql, connection=None, parameters=()):
    conn = connection
    affected = 0
    curs = None

    try:
        if conn is None:
            conn = get_connection()
        conn.begin_transaction()
        curs = conn.cursor()
        curs.execute(sql, parameters)
        conn.commit()
        affected = curs.rowcount
    except Exception as ex:
        if connection is not None:
            conn.rollback()
        print ex
    finally:
        if connection is None and curs is not None:
            curs.close(True)
            conn.close()

    return affected
