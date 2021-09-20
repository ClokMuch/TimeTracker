# TimeTracker
# By Clok Much
#
# ver.2

# 原生库
import json
from tkinter import Tk
from tkinter.messagebox import showerror
from os import mkdir
from os import path
from os import remove
from time import sleep
import datetime

# 第三方库
from matplotlib import pyplot
from matplotlib import rc
import psutil

Tk().withdraw()
now_day = datetime.datetime.now().strftime('%Y-%m-%d')
# 初始化 检查 config.json
try:
    with open("config.json", "rb") as file_obj:
        config = json.load(file_obj)
        file_obj.close()
except IOError:
    showerror(title="Error: config.json", 
              message="IOError: config.json is not accessible!\n"
                      "It must be saved in the same dir with this program!")
    exit()
except json.decoder.JSONDecodeError:
    showerror(title="Error: config.json",
              message="JsonFormatError: json file has something wrong like brackets or comma...\n"
                      "In short, it not a recognizable json file.")
    exit()


# 检查 tracker.json
try:    # 验证目录设定的有效性
    if not path.isdir(config["output_dir"]):
        mkdir(config["output_dir"])
    if not path.isdir(config["output_dir"] + config["sub_dir"]):
        mkdir(config["output_dir"] + config["sub_dir"])
    with open(config["output_dir"] + "PermissionTest", mode='w', encoding='utf8') as file_obj:
        file_obj.write("TEST")
        file_obj.close()
    with open(config["output_dir"] + "PermissionTest", mode='r', encoding='utf8') as file_obj:
        tmp = file_obj.read()
        file_obj.close()
    if tmp == "TEST":
        remove(config["output_dir"] + "PermissionTest")
except IOError:
    showerror(title="Error: config.json", message="IOError: dir in config is not accessible!")
    exit()

try:    # 验证 tracker.json 配置是否可访问及基本数据是否有误
    with open('tracker.json', 'rb') as file_obj:
        tracker_config = json.load(file_obj)
        tmp = tracker_config[0]['other']
        if not len(set(tracker_config[1].keys())) == len(tracker_config[1].keys()):
            # 存在重复进程名时，找出重复进程名，然后退出程序
            process_name_in_tracker_json = list(tracker_config[1].keys())
            same_process_names = []
            tmp = []
            for i in process_name_in_tracker_json:
                if i in tmp:
                    same_process_names.append(i)
                else:
                    tmp.append(i)
            showerror(title='Error: tracker.json',
                      message="Exist multiple same process_name: " + ','.join(same_process_names))
            exit()
        for i in tracker_config[1].keys():  # 用于检查每项进程是否有对应的名称，没有则会抛出 KeyError 异常
            tmp = tracker_config[1][i]['name']

except IOError:
    showerror(title='Error: tracker.json', message="IOError: tracker.json is not accessible!")
    exit()
except KeyError:
    showerror(title='Error: tracker.json',
              message='KeyError:\n'
                      '1. Catalog in tracker.json must be contained;\n'
                      '2. Catalog must contain "other";\n'
                      '3. Detailed information must contain "name"!')
    exit()
except json.decoder.JSONDecodeError:
    showerror(title='Error: tracker.json',
              message="JsonFormatError: json file has something wrong like brackets or comma...\n"
                      "In short, it not a recognizable json file.")
    exit()

# 判断是否已有今日的数据，有则载入，若 tracker 新增进程，将把新增进程添加到末尾，并在大循环末尾更新文件；无则重新统计
try:
    with open(config["output_dir"] + now_day + '.json', 'rb') as file_obj:
        tracker_process = json.load(file_obj)
        for i in tracker_config[1].keys():
            if i not in tracker_process:
                tracker_process[i] = 0
            else:
                pass
        file_obj.close()
except IOError:
    tracker_process = {}  # 灌入进程的时间计数，写入和读取数据时，以此变量为依据
    for i in tracker_config[1].keys():
        tracker_process[i] = 0
tracker_list = set(tracker_config[1].keys())


while True:     # 开始程序的大循环
    # 开始程序的小循环
    for small_loop_tmp in range(config["graph_time"]):
        sleep(config["track_time"])    # 暂停运行指定秒数
        now_pid = psutil.pids()     # 固定当前所有进程 pid
        now_processes = set()   # 创建、清空进程名
        for i in now_pid:   # 尝试根据 pid 获取进程名称
            try:
                now_processes.add(psutil.Process(i).name())
            except psutil.AccessDenied:     # 进程拒绝访问
                pass
            except psutil.NoSuchProcess:    # 进程被销毁，从 pid 无法获取到进程名称时忽略掉
                pass
        fin_process = [-99999, 'no_process']    # ['priority', 'process_name']
        for i in (now_processes & tracker_list):     # 根据权重选择本次统计周期计入数据的进程，当权重一致时，优先为 tracker.json 中靠前者
            if "priority" in tracker_config[1][i]:
                if tracker_config[1][i]['priority'] > fin_process[0]:
                    fin_process = [tracker_config[1][i]['priority'], i]
            elif "catalog" in tracker_config[1][i]:
                if tracker_config[0][tracker_config[1][i]['catalog']][1] > fin_process[0]:
                    fin_process = [tracker_config[0][tracker_config[1][i]['catalog']][1], i]
            else:
                fin_process = [tracker_config[0]['other'][1], i]
        # 将计数周期对应的时间灌入进程时间计数
        if not fin_process == [-99999, 'no_process']:
            tracker_process[fin_process[1]] += config["track_time"]
    # 回到大循环
    # 将进程对应的时间转化为应用、分类，最后重新获取日期
    tracker_app = {}  # 重置应用时间计数
    for i in tracker_config[1].keys():
        tracker_app[tracker_config[1][i]['name']] = 0
    tracker_catalog = {}  # 重置类别时间计数
    for i in tracker_config[0].keys():
        tracker_catalog[i.title()] = 0
    # 加入应用和类别时间计数增量，并去除值为 0 的条目
    for key in tracker_process.keys():
        tracker_app[tracker_config[1][key]['name']] += tracker_process[key]
        if 'catalog' in tracker_config[1][key]:
            tracker_catalog[tracker_config[1][key]['catalog'].title()] += tracker_process[key]
        else:
            tracker_catalog['other'.title()] += tracker_process[key]
    no_zero = {}
    for key in tracker_app.keys():
        if tracker_app[key] > 0:
            no_zero[key] = tracker_app[key]
    tracker_app.clear()
    for key, value in no_zero.items():
        tracker_app[key] = value
    no_zero.clear()
    for key in tracker_catalog.keys():
        if tracker_catalog[key] > 0:
            no_zero[key] = tracker_catalog[key]
    tracker_catalog.clear()
    for key, value in no_zero.items():
        tracker_catalog[key] = value
    del no_zero
    # 输出保存 tracker_process ，权限等问题已在初始化验证，故此处不再捕捉错误
    with open(config["output_dir"] + now_day + '.json', 'w') as file_obj:
        json.dump(tracker_process, file_obj)
        file_obj.close()
    # 对应用和分类时间进行绘图，然后释放掉变量
    # 首先绘制应用计时图
    x = sorted(tracker_app, key=tracker_app.get)
    y = []
    for i in range(0, len(tracker_app.values())):
        y.append(tracker_app[x[i]] / 60)
    font = {'family': config["graph_font"], "size": 24}
    rc('font', **font)
    pyplot.figure(figsize=(20, 10))
    pyplot.barh(x, y, color=config["app_color"])
    pyplot.title('分应用统计运行时间')
    pyplot.xlabel('大概时长（min）')
    pyplot.ylabel('应用名称')
    pyplot.subplots_adjust(top=0.935,
                           bottom=0.125,
                           left=0.19,
                           right=0.975,
                           hspace=0.2,
                           wspace=0.2)
    pyplot.savefig(config["output_dir"] + '\\app.png')
    pyplot.close()
    del tracker_app
    # 随后绘制分类计时图
    x = sorted(tracker_catalog, key=tracker_catalog.get)
    y = []
    colors = []
    for i in range(0, len(tracker_catalog.values())):
        y.append(tracker_catalog[x[i]] / 60)
    for i in x:
        colors.append(tracker_config[0][i.lower()][0])
    pyplot.figure(figsize=(20, 10))
    pyplot.barh(x, y, color=colors)
    pyplot.title('分类统计时长')
    pyplot.xlabel('大概时长（min）')
    pyplot.ylabel('类型')
    pyplot.subplots_adjust(top=0.935,
                           bottom=0.125,
                           left=0.160,
                           right=0.975,
                           hspace=0.2,
                           wspace=0.2)
    pyplot.savefig(config["output_dir"] + '\\catalog.png')
    pyplot.close()
    del tracker_catalog
    # 最后获取当前日期，不是同一天则先将数据保存为起点日期，后将 now_day 更改为新日期，并重置进程时间计数
    if not datetime.datetime.now().strftime('%Y-%m-%d') == now_day:
        now_day = datetime.datetime.now().strftime('%Y-%m-%d')
