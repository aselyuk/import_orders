# coding: utf-8

import json
import os
import copy
import shutil
import socket
import datetime

LOG_PATH = ".\\Logs\\"


def get_config():
    file_name = os.path.dirname(__file__) + "\\config.json"
    with open(file_name, "r") as read_file:
        data = read_file.readlines()
        json_data = ""
        for x in data:
            if isinstance(x, unicode):
                x = x.encode("utf-8")
            json_data += x
        conf = json.loads(json_data)
        # conf = json.load(read_file)
    return conf


def get_cfg_value(cfg_dict, cfg_key, default_value):
    value = default_value

    if isinstance(cfg_dict, dict) and cfg_key in cfg_dict.keys():
        value = cfg_dict.get(cfg_key)
        value = value if value is not None else default_value

    return value


def copy_row(row):
    return copy.copy(row)


def find_by_key(iterable, key, value):
    fields = iterable[1]
    has_key = key in fields
    index_key = fields[key]
    for index, dict_ in enumerate(iterable[0]):
        if has_key and dict_[index_key] == value:
            return index, dict_
    return None, None


def has_dict_key(dict_list, key):
    has = False
    for dict_ in dict_list:
        if key in dict_:
            has = True
            break
    return has


def move_file(target_file, new_location):
    if not os.path.isfile(target_file):
        pass
    if not os.path.isdir(new_location):
        os.makedirs(new_location)
    file_name = os.path.basename(target_file)
    new_location = new_location if new_location.endswith("\\") else new_location + "\\"
    new_location += file_name
    cnt = 1
    while os.path.isfile(new_location):
        tmp = os.path.splitext(file_name)
        new_file_name = tmp[0] + " (%d)%s" % (cnt, tmp[1])
        new_location = os.path.dirname(new_location) + "\\" + new_file_name
        cnt += 1

    try:
        shutil.move(target_file, new_location)
    except Exception as ex:
        print ex.args


def get_good_dir(base_dir, target_dir):
    base_dir = base_dir if base_dir.endswith("\\") else base_dir + "\\"
    starts_with = ".\\"
    if target_dir.startswith(starts_with):
        target_dir = target_dir[len(starts_with):]
        target_dir = base_dir + target_dir
    return target_dir


def add_to_log(text, file_name=None):
    if isinstance(text, unicode):
        text = text.encode("utf-8")
    current_date = datetime.datetime.now()
    hostname = get_hostname()
    ip = get_ip(hostname)
    if file_name is None:
        file_name = os.path.abspath(LOG_PATH)
        file_name += "\\Log_%s_%s.log" % (current_date.strftime('%Y-%m-%d'),
                                          ip.replace(".", "").replace(",", "_"))

    strtime = current_date.strftime("[%d.%m-%Y %H.%M.%S ") + hostname + "] "
    text = strtime + text + "\n"

    if not os.path.isfile(file_name):
        save_file(os.path.dirname(file_name), os.path.basename(file_name), text)
    else:
        f = open(file_name, "a")
        f.writelines(text)
        f.close()


def get_hostname():
    hostname = socket.gethostname()
    return hostname


def get_ip(hostname=None):
    if hostname is None:
        hostname = socket.gethostname()
    ip = socket.gethostbyname_ex(hostname)
    s = ''
    for x in range(0, len(ip[2])):
        s += ip[2][x] + ","
    return s.strip(',')


def get_mmyy(date):
    return date.strftime("%m%y")


def get_sql_date(date):
    return date.strftime("%Y-%m-%d")


def lead0(number):
    return ("0" if number < 10 else "") + str(number)


def get_good_file_name(file_path, file_name):
    file_path = file_path if file_path.endswith("\\") else file_path + "\\"

    if not os.path.isdir(file_path):
        try:
            os.makedirs(file_path)
        except OSError as ex:
            print ex.args
            return None

    count = 0
    new_file_name = file_name
    while os.path.isfile(file_path + new_file_name):
        count += 1
        tmp = os.path.splitext(file_name)
        new_file_name = tmp[0] + "(%d)%s" % (count, tmp[1])

    return file_path + new_file_name


def save_file(file_path, file_name, text):
    file_path = file_path if isinstance(file_path, str) else file_path.encode("utf-8")
    new_file_name = get_good_file_name(file_path, file_name)

    if new_file_name is None:
        return False

    f = open(new_file_name, "w")
    f.writelines(text)
    f.close()

    return os.path.isfile(new_file_name), new_file_name


def save_json_file(file_path, file_name, json_data):
    new_file_name = get_good_file_name(file_path, file_name)

    if new_file_name is None:
        return

    with open(new_file_name, 'w') as f:
        json.dump(json_data, f)
