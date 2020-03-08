import src.constants as constants
import src.utils as utils

# 有道词典api接口
from src.utils import get_url_content

URL = r"http://fanyi.youdao.com/openapi.do?keyfrom=youdaoci&key=694691143&type=data&doctype=xml&version=1.1&q=%s"


def get_meaning(word: str) -> str:
    if word:
        url = URL % (word)
        content = get_url_content(url, constants.get_conf_center().get_proxies())
        if content:
            return __analysis_content(str(content, encoding="utf-8"))
        else:
            utils.print_in_red("网络问题!")


def __analysis_content(s: str) -> str:
    result = []
    if s and s.__contains__("<explains>"):
        s = s[s.index("<explains>") + len("<explains>"):s.index("</explains>")]
        splits = s.split("\n")
        for line in splits:
            line = line.lstrip(" ").rstrip(" ").rstrip("\n")
            if line:
                result.append(line[len("<ex><![CDATA["):len(line) - len("]]></ex>")])
    else:
        result.append("查询该单词无意义，请确认输入是否为正确的单词!")
    return "\n".join(result)


if __name__ == '__main__':
    print(get_meaning("like"))
