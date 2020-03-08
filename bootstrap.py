import os

from src.automatic_update import auto_update
from src.bdc import init
from src.constants import Monitor, load_init
from src.utils import print_in_red

if __name__ == '__main__':
    os.system("")
    print_in_red("START!!")
    # 查看是否有更新
    auto_update()
    # 加载全局配置
    load_init()
    # 初始化监控线程
    monitor = Monitor()
    # 设置为守护线程
    monitor.setDaemon(True)
    monitor.start()
    os.system("")
    # 程序启动
    init()
    print_in_red("END!!")
