import hashlib
import logging
import os

import requests

SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__)).split(r"src")[0]

logging.basicConfig(level=logging.INFO,  # 控制台打印的日志级别
                    filename=os.path.join(SCRIPT_PATH, "logs", "bdc.log"),
                    filemode='a',  ##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
                    # a是追加模式，默认如果不写的话，就是追加模式
                    format=
                    '%(asctime)s : %(message)s'  # 日志格式

                    )


def get_file_md5(filepath):
    # 获取文件的md5
    if not os.path.isfile(filepath):
        return
    myhash = hashlib.md5()
    f = open(filepath, "rb")
    while True:
        b = f.read(8096)
        if not b:
            break
        myhash.update(b)
    f.close()
    return myhash.hexdigest()


def get_all_files(dir):
    files_ = []
    list = os.listdir(dir)
    for i in range(0, len(list)):
        path = os.path.join(dir, list[i])
        if os.path.isdir(path):
            files_.extend(get_all_files(path))
        if os.path.isfile(path):
            files_.append(path)
    return files_


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


def print_in_red(str):
    logging.info(str)
    print('\033[31m%s\033[0m' % str)


def print_in_green(str):
    logging.info(str)
    # print('\033[32m%s\033[0m' % str)


def print_in_tip(str):
    print_in_red("提示：%s,请重新输入！" % str)


def print_in_yellow(str):
    logging.info(str)
    # print('\033[33m%s\033[0m' % str)


def print_in_wihte(str):
    logging.info(str)
    print('\033[0m%s\033[0m' % str)


def get_url_content(file_url, proxies: dict = {}) -> bytes:
    # 输出内容:user=admin&password=admin
    header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko'}
    try:
        req = requests.get(url=file_url, headers=header_dict, verify=False, proxies=proxies)
        if req.status_code == 200:
            content = req.content
            return content
        else:
            print_in_red("请求异常，返回码[%s]" % req.status_code)
            return None
    except Exception as e:
        print_in_red(e)
        return None
