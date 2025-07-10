import os
import subprocess
import sys
import random
import time
import importlib.machinery
import shutil
from termcolor import colored

# 定义彩虹颜色
RAINBOW_COLORS = ['red', 'yellow', 'green', 'cyan', 'blue', 'magenta']

# 显示作者信息
def show_author_info():
    author_info = [
        "作者：幻穗",
        "QQ：3111545189",
        "大厅动作头像框播报美化"
    ]
    for i, text in enumerate(author_info):
        color = RAINBOW_COLORS[i % len(RAINBOW_COLORS)]
        print(colored(text, color, attrs=['bold']))
        time.sleep(0.1)
    print(colored("\n" + "="*50, 'cyan'))

def remove_pycache():
    # 删除当前目录及其子目录下的所有 __pycache__ 文件夹
    for dirpath, dirnames, filenames in os.walk('.'):
        if "__pycache__" in dirnames:
            pycache_dir = os.path.join(dirpath, "__pycache__")
            shutil.rmtree(pycache_dir)  # 删除 __pycache__ 文件夹

def get_random_color():
    return random.choice(RAINBOW_COLORS)

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(bytes_obj):
    return bytes_obj.hex()

def find_and_swap(data, marker1, marker2, int1, int2):
    marker1 = hex_to_bytes(marker1)
    marker2 = hex_to_bytes(marker2)
    marker_len = len(marker1)

    def find_marker_above_int(data, marker1, marker2, int_pos):
        pos1 = data.rfind(marker1, 0, int_pos)
        if pos1 == -1:
            return None, None

        pos2 = data.find(marker2, pos1 + marker_len, int_pos)
        if pos2 == -1:
            return None, None

        byte_start = pos1 + marker_len
        byte_end = pos2
        return byte_start, data[byte_start:byte_end]

    int1_pos = data.find(int1.to_bytes(4, byteorder='little'))
    int2_pos = data.find(int2.to_bytes(4, byteorder='little'))

    if int1_pos == -1 or int2_pos == -1:
        return False, f"{int1}或{int2}没有在dat中搜索到"

    byte1_start, byte1 = find_marker_above_int(data, marker1, marker2, int1_pos)
    if byte1_start is None:
        return False, f"{int1}没有在dat中搜索到"

    byte2_start, byte2 = find_marker_above_int(data, marker1, marker2, int2_pos)
    if byte2_start is None:
        return False, f"{int2}没有在dat中搜索到"

    temp_data = bytearray(data)
    temp_data[byte1_start:byte1_start + len(byte1)] = byte2
    temp_data[byte2_start:byte2_start + len(byte2)] = byte1
    data = bytes(temp_data)

    color = get_random_color()
    print(colored("\n" + "-" * 50, color, attrs=['bold']))
    print(colored(f"交换数值: {int1} <-> {int2}", color, attrs=['bold']))
    print(colored(f"第1个数值偏移位置: 0x{byte1_start:08x}", color))
    print(colored(f"原始值: {bytes_to_hex(byte1)}", 'red'))
    print(colored(f"修改后: {bytes_to_hex(temp_data[byte1_start:byte1_start + len(byte1)])}", 'green'))
    print()
    print(colored(f"第2个数值偏移位置: 0x{byte2_start:08x}", color))
    print(colored(f"原始值: {bytes_to_hex(byte2)}", 'red'))
    print(colored(f"修改后: {bytes_to_hex(temp_data[byte2_start:byte2_start + len(byte2)])}", 'green'))
    print(colored("修改成功！", color, attrs=['bold']))
    print(colored("-" * 50, color, attrs=['bold']))
    time.sleep(0.05)
    return True, data

# 显示作者信息
show_author_info()

config_file_path = input(colored("请输入配置文件的路径：", 'green'))
if not os.path.exists(config_file_path):
    print(colored("文件不存在，请检查路径！", 'red', attrs=['bold']))
    exit()

file_path = input(colored("请输入要修改的dat文件路径：", 'green'))
if not os.path.exists(file_path):
    print(colored("文件不存在，请检查路径！", 'red', attrs=['bold']))
    exit()

marker1 = input(colored("请输入第一个特征码：", 'yellow'))
marker2 = input(colored("请输入第二个特征码：", 'yellow'))
print(colored("="*50, 'cyan'))

with open(file_path, 'rb') as file:
    data = file.read()

try:
    config_module = importlib.machinery.SourceFileLoader('config_module', config_file_path).load_module()
    integers = config_module.array
except ImportError:
    print(colored("配置错误", 'red', attrs=['bold']))
    exit()

if not integers:
    print(colored("配置中格式错误", 'red', attrs=['bold']))
    exit()

print(colored(f"\n开始处理 {len(integers)} 个配置项...", 'yellow', attrs=['bold']))

for i, (int1, int2) in enumerate(integers):
    print(colored(f"\n处理第 {i+1}/{len(integers)} 项", 'cyan', attrs=['bold']))
    success, result = find_and_swap(data, marker1, marker2, int1, int2)
    if not success:
        color = get_random_color()
        print(colored("-" * 50, color, attrs=['bold']))
        print(colored(f"{int1}  {int2}", color, attrs=['bold']))
        print(colored(result, 'yellow'))
        print(colored("已跳过修改", color))
        print(colored("-" * 50, color, attrs=['bold']))
        time.sleep(0.05)
    else:
        data = result

with open(file_path, 'wb') as file:
    file.write(data)

print(colored("\n" + "="*50, 'green'))
print(colored("全部修改完成！", 'green', attrs=['bold', 'reverse']))
print(colored("="*50, 'green'))

# 删除 __pycache__ 文件夹
remove_pycache()