import struct
import os
import importlib.machinery
import time
from termcolor import colored
import shutil
import random

# 定义彩虹颜色
RAINBOW_COLORS = ['red', 'yellow', 'green', 'cyan', 'blue', 'magenta']

# 显示作者信息
def show_author_info():
    print(colored("┌" + "─" * 48 + "┐", 'cyan'))
    author_info = [
        "作者：幻穗",
        "QQ：3111545189",
        "地铁美化工具"
    ]
    for i, text in enumerate(author_info):
        color = RAINBOW_COLORS[i % len(RAINBOW_COLORS)]
        # 修复这里：添加缺少的括号
        content = colored(text, color, attrs=['bold'])
        print(colored("│", 'cyan') + content.center(48) + colored("│", 'cyan'))
        time.sleep(0.1)
    print(colored("└" + "─" * 48 + "┘", 'cyan'))

def remove_pycache():
    # 删除当前目录及其子目录下的所有 __pycache__ 文件夹
    for dirpath, dirnames, filenames in os.walk('.'):
        if "__pycache__" in dirnames:
            pycache_dir = os.path.join(dirpath, "__pycache__")
            shutil.rmtree(pycache_dir)  # 删除 __pycache__ 文件夹
            print(f"已删除: {pycache_dir}")

def replace_decimal_in_dat():
    # 显示作者信息
    show_author_info()
    
    # 输入框
    print(colored("\n┌" + "─" * 48 + "┐", 'cyan'))
    config_file_path = input(colored("│" + "请输入配置文件的路径：".ljust(48) + "│\n", 'green'))
    print(colored("└" + "─" * 48 + "┘", 'cyan'))
    
    try:
        config_module = importlib.machinery.SourceFileLoader('config_module', config_file_path).load_module()
        integers = config_module.array
    except ImportError:
        print(colored("配置错误", 'red', attrs=['bold']))
        exit()

    if not integers:
        print(colored("配置中格式错误", 'red', attrs=['bold']))
        exit()

    # 输入框
    print(colored("\n┌" + "─" * 48 + "┐", 'cyan'))
    original_dat_path = input(colored("│" + "请输入原版dat文件的路径：".ljust(48) + "│\n", 'green'))
    print(colored("└" + "─" * 48 + "┘", 'cyan'))
    
    with open(original_dat_path, 'rb') as f:
        dat_content = f.read()

    # 开始处理框
    print(colored("\n┌" + "─" * 48 + "┐", 'yellow'))
    print(colored("│" + "开始处理文件...".center(48) + "│", 'yellow', attrs=['bold']))
    print(colored("└" + "─" * 48 + "┘", 'yellow'))
    
    for i, int_pair in enumerate(integers):
        int1, int2 = int_pair
        color = RAINBOW_COLORS[i % len(RAINBOW_COLORS)]
        
        # 处理项框
        print(colored("\n┌" + "─" * 48 + "┐", color))
        print(colored("│" + f"处理第 {i+1}/{len(integers)} 项: {int1} -> {int2}".center(48) + "│", color, attrs=['bold']))
        print(colored("│" + " " * 48 + "│", color))
        
        first_hex = struct.pack('<I', int1)
        index = dat_content.find(first_hex)
        if index != -1:
            second_hex = struct.pack('<I', int2)
            dat_content = dat_content[:index] + second_hex + dat_content[index + 4:]
            
            original_hex_str = ' '.join(f"{byte:02X}" for byte in first_hex)
            modified_hex_str = ' '.join(f"{byte:02X}" for byte in second_hex)
            print(colored("│" + f"被修改的16进制的偏移位置: 0x{index:x}".ljust(48) + "│", color))
            print(colored("│" + f"原始值: {original_hex_str}".ljust(48) + "│", 'red'))
            print(colored("│" + f"修改后: {modified_hex_str}".ljust(48) + "│", 'green'))
        else:
            print(colored("│" + f"未找到{int1}对应的十六进制位置，已跳过".ljust(48) + "│", 'yellow'))

        print(colored("└" + "─" * 48 + "┘", color))
        time.sleep(0.05)

    with open(original_dat_path, 'wb') as f:
        f.write(dat_content)

    # 成功框
    print(colored("\n┌" + "─" * 48 + "┐", 'green'))
    print(colored("│" + "修改成功！".center(48) + "│", 'green', attrs=['bold', 'reverse']))
    print(colored("└" + "─" * 48 + "┘", 'green'))

replace_decimal_in_dat()
remove_pycache()