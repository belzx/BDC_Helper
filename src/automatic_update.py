import os

import requests

from src.constants import CHECK_FILE_REMOTE_PATH, CHECK_FILE_LOCAL_PATH, REMOTE_DIR, REMOTE_PATH, \
    EXCLUDE_FILES, SRC_PATH, get_conf_center
from src.utils import get_file_md5, get_all_files, print_in_red


def auto_update():
    print_in_red("测试网络是否联通[%s]!" % (CHECK_FILE_REMOTE_PATH,))
    try:
        content = get_url_content(CHECK_FILE_REMOTE_PATH)
    except Exception as e:
        print_in_red("网络测试失败，项目文件不进行更新使用!")
        print_in_red(e)
        return
    print_in_red("网络测试联通!")
    print_in_red("开始检查远程是否有文件更新!")
    content = get_url_content(CHECK_FILE_REMOTE_PATH)
    file_names = content.split("\n")
    for file_name in file_names:
        if file_name:
            split = file_name.split("||")
            name = split[0]
            md5 = split[1]
            local_path = os.path.join(SRC_PATH, name)
            remote_path = REMOTE_PATH + REMOTE_DIR + name
            if os.path.exists(local_path):
                if get_file_md5(local_path) == md5:
                    pass
                else:
                    # md5值与远程不一致则看作有更新
                    print_in_red("[%s]文件有更新，更新本地文件!" % (local_path,))
                    # 获取文件内容
                    url_content = get_url_content(remote_path)
                    # 删除本地文件
                    os.remove(local_path)
                    # 创建新的文件 并更新内容
                    t = open(local_path, "a", encoding="utf-8")
                    t.write(url_content)
                    t.close()
                    print_in_red("[%s]文件更新完毕!" % (local_path,))
            else:
                print_in_red("新增文件[%s]，更新本地文件!" % (local_path,))
                # 更新文件
                url_content = get_url_content(remote_path)
                # 创建新的文件 并更新内容
                t = open(local_path, "a", encoding="utf-8")
                t.write(url_content)
                t.close()
                print_in_red("[%s]文件更新完毕!" % (local_path,))
    print_in_red("更新检查完毕!")


def generate_file():
    # 获取src 下面所有的文件
    files = get_all_files(SRC_PATH)
    if os.path.exists(CHECK_FILE_LOCAL_PATH):
        os.remove(CHECK_FILE_LOCAL_PATH)
    auto_file = open(CHECK_FILE_LOCAL_PATH, "a", encoding="utf-8")
    for file in files:
        # 获取每个文件的md5
        file_path = file[len(SRC_PATH) + 1:]
        if not file_path.startswith("__") and not file_path in EXCLUDE_FILES:
            md5 = get_file_md5(file)
            auto_file.write("%s||%s\n" % (file_path, md5))
    auto_file.close()


def get_url_content(file_url):
    proxies = {}
    center = get_conf_center()
    if center.PROXY_HTTP:
        proxies["http"] = center.PROXY_HTTP
    if center.PROXY_HTTPS:
        proxies["https"] = center.PROXY_HTTPS
    # 输出内容:user=admin&password=admin
    header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko'}
    req = requests.get(url=file_url, headers=header_dict, proxies=proxies, verify=False)
    content = req.content
    return str(content, encoding='utf-8')


if __name__ == '__main__':
    # auto_update()
    generate_file()
