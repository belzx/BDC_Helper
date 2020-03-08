import hashlib
import os
from threading import Thread
from time import sleep

from src.utils import print_in_red

TIP_MESSAGE = "提示输入@,不知道#,不再显示$,上一个不再显示%,翻译单词^+word,退出输入&,"

OPTION_EMUS = {
    0: "A",
    1: "B",
    2: "C",
    3: "D",
}

SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__)).split(r"src")[0]
SRC_PATH = os.path.join(SCRIPT_PATH, "src")
XL_PATH = os.path.join(SCRIPT_PATH, "data", "dc_src.xlsx")
FREQUENCY_PATH = os.path.join(SCRIPT_PATH, "data", "frequency_statistics.xlsx")
MEMORY_XL_PATH = os.path.join(SCRIPT_PATH, "data", "dc_memory_statistics.xlsx")
GITHUB_URL = r"https://github.com/lizhixiong1994/bdc_helper"

TEMP_CONF_PATH = os.path.join(SCRIPT_PATH, "src", "temp.conf")
BDC_CONF_PATH = os.path.join(SCRIPT_PATH, "config", "bdc.conf")
BDC_TEMP_CONF_PATH = os.path.join(SCRIPT_PATH, "config", "bdc-%s.conf")

REMOTE_PATH = r"https://gitee.com/lizhixiong1994/bdc_helper/raw/master/"
REMOTE_DIR = "src/"
CHECK_FILE_REMOTE_PATH = REMOTE_PATH + "check/check.txt"
EXCLUDE_FILES = ["automatic_update.py"]
CHECK_FILE_LOCAL_PATH = os.path.join(SCRIPT_PATH, "check", "check.txt")

MP3_TYPE_EN = 1
MP3_TYPE_AM = 2

EN_PATH = os.path.join(SCRIPT_PATH, "media", "en")
AM_PATH = os.path.join(SCRIPT_PATH, "media", "am")


class ConfCenter:
    # 具体权重计算规则可以参考get_weight方法
    # 下面一些参数比较重要

    # nums的系数
    FORMAL_WEIGHT = 600
    # hit_nums的系数
    ORIGIN_WEIGHT = 0

    # 正数权重值（当hit_nums大于0时，该值越大，则nums越大的单词出现的概率越大，更加大）
    POSITIVE_WEIGHT = 1
    # 最大正数权重值（当hit_nums为最大值，权值的系数）
    MAX_POSITIVE_WEIGHT = 1
    # 最大正数常数值
    MAX_POSITIVE_CONSTANT_WEIGHT = 0

    # 负数权重值（当hit_nums小于0时的系数）
    MINUS_WEIGHT = 1
    # 最小负数权重值(当hit_nums为最小值时的系数)
    MIN_MINUS_WEIGHT = 1
    # 最小负数的常数值
    MIN_MINUS_CONSTANT_WEIGHT = 0

    # 最大分值，要求大于0
    MAX_HIT_NUM = 10
    # 最小分值，要求小于0
    MIN_HIT_NUM = -10

    # 单词保证出现概率为0
    NO_SHOW_HIT_NUM = -999
    # 正确得分
    RIGHT_SCORE = 5
    # 有提示后的得分
    HALF_RIGHT_SCORE = 2
    # 错误即不知道的得分
    WRONG_SCORE = -7
    # 问题类型占重
    # 填充
    FILL_QUESTION = 30
    # 选择题
    OPTION_QUESTION = 70
    # 默写中文意思题目
    MEANING_WRITE_QUESTION = 5
    # 扫描配置文件间隔 秒
    PERIOD_OF_MONITOR_CONF = 2
    # 每几个刷新缓存到磁盘
    FLUSH_CACHE_SIZE = 10
    # 代理http
    PROXY_HTTP = None
    # 代理https
    PROXY_HTTPS = None
    # 已经更新
    HAD_UPDATE = False

    FREQUENCY_STATISTICS = True
    # 频率统计工具刷新长度
    MAX_FREQUENCY_FLUSH_SIZE = 2
    # 频率最高分
    MAX_FREQUENCY_SCORE = 4
    # 半频率得分
    FREQUENCY_HALF_SCORE = 1
    # 全频率得分
    FREQUENCY_SCORE = 3
    # 单词发音 1 是 英式 2 是 美式
    PRONOUNCE_TYPE = MP3_TYPE_EN
    # 开启发音 on 或者 off
    PRONOUNCE_SWITCH = "on"
    # name - md5
    EX_NAMES = {}

    def __init__(self):
        if not os.path.exists(os.path.join(SCRIPT_PATH, "media")):
            os.mkdir(os.path.join(SCRIPT_PATH, "media"))
        if not os.path.exists(EN_PATH):
            os.mkdir(EN_PATH)
        if not os.path.exists(AM_PATH):
            os.mkdir(AM_PATH)

    def get_proxies(self):
        proxies = {}
        if self.PROXY_HTTP:
            proxies["http"] = self.PROXY_HTTP
        if self.PROXY_HTTPS:
            proxies["https"] = self.PROXY_HTTPS
        return proxies

CONF_CENTER = ConfCenter()


class Monitor(Thread):
    def run(self):
        while True:
            sleep(CONF_CENTER.PERIOD_OF_MONITOR_CONF)
            center = get_conf_center()
            # 判断是否所有文件是否md5有变化
            for key in center.EX_NAMES:
                if not center.EX_NAMES[key] == get_file_md5(key):
                    # 已经更新过,更改标签
                    center.HAD_UPDATE = True
                    reload()
                    break


def load():
    global CONF_CENTER
    # 先读取config中的文件
    # 再读取config中的其他文件
    with open(BDC_CONF_PATH, encoding="utf-8") as file:
        print_in_red("加载配置文件%s" % BDC_CONF_PATH)
        lines = file.readlines()
        CONF_CENTER.EX_NAMES[BDC_CONF_PATH] = get_file_md5(BDC_CONF_PATH)
        for line in lines:
            if line:
                line = line.lstrip(" ").rstrip("\n")
            if line and not line.startswith("#"):
                index = line.index("=")
                key = line[0:index].lstrip(" ").rstrip(" ")
                value = line[index + 1:].lstrip(" ").rstrip(" ") if line[index + 1:] else None
                if hasattr(CONF_CENTER, key):
                    try:
                        if value:
                            if key in ("EX_NAMES",):
                                for ex in value.split(","):
                                    CONF_CENTER.EX_NAMES[BDC_TEMP_CONF_PATH % ex] = None
                            elif key in ("PROXY_HTTP", "PROXY_HTTPS", "PRONOUNCE_SWITCH",):
                                setattr(CONF_CENTER, key, str(value))
                            elif key in ("FREQUENCY_STATISTICS",):
                                setattr(CONF_CENTER, key, bool(value))
                            else:
                                setattr(CONF_CENTER, key, float(value))

                    except Exception as e:
                        print_in_red("加载数据失败")
                        print_in_red(e)

    for path in CONF_CENTER.EX_NAMES:
        if path == BDC_CONF_PATH:
            continue
        CONF_CENTER.EX_NAMES[path] = get_file_md5(path)
        print_in_red("加载配置文件%s" % path)
        with open(path, encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                if line:
                    line = line.lstrip(" ").rstrip("\n")
                if line and not line.startswith("#"):
                    index = line.index("=")
                    key = line[0:index].lstrip(" ").rstrip(" ")
                    value = line[index + 1:].lstrip(" ").rstrip(" ") if line[index + 1:] else None
                    if hasattr(CONF_CENTER, key):
                        try:
                            if value:
                                if key in ("PROXY_HTTP", "PROXY_HTTPS", "PRONOUNCE_SWITCH",):
                                    setattr(CONF_CENTER, key, str(value))
                                elif key in ("FREQUENCY_STATISTICS",):
                                    setattr(CONF_CENTER, key, bool(value))
                                else:
                                    setattr(CONF_CENTER, key, float(value))

                        except Exception as e:
                            print_in_red("加载数据失败")
                            print_in_red(e)


def reload():
    global CONF_CENTER
    print_in_red("重新加载配置文件!")
    load()
    print_in_red("配置文件加载完毕!")


def load_init():
    print_in_red("加载配置文件!")
    load()
    print_in_red("配置文件加载完毕!")


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


def get_conf_center() -> ConfCenter:
    return CONF_CENTER
