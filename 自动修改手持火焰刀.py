import os
import importlib
import importlib.machinery
from termcolor import colored
import random
import time

# 定义彩虹颜色
RAINBOW_COLORS = ['red', 'yellow', 'green', 'cyan', 'blue', 'magenta']

# 显示作者信息
def show_author_info():
    author_info = [
        "作者：幻穗",
        "QQ：3111545189",
        "感谢使用本工具！"
    ]
    for i, text in enumerate(author_info):
        color = RAINBOW_COLORS[i % len(RAINBOW_COLORS)]
        print(colored(text, color, attrs=['bold']))
        time.sleep(0.1)

# 将十进制数转换为十六进制并格式化输出
def DEC_to_HEX(decimal_number):
    hex_number = format(int(decimal_number), '08X')  # '08X' 表示输出为8位十六进制数,不足部分用0填充

    # 将十六进制数拆分成数组并反转顺序
    hex_array = [hex_number[i:i+2] for i in range(0, len(hex_number), 2)]
    reversed_hex_array = hex_array[::-1]  # 反转数组

    # 重新组合反转后的十六进制数并输出
    reversed_hex_number = ''.join(reversed_hex_array)
    print(colored(f"{decimal_number} 转换为: {reversed_hex_number}", 'cyan'))
    return reversed_hex_number

# 将十六进制数转换为十进制
def HEX_to_DEC(decimal_hex):
    hex_array = [decimal_hex[i:i+2] for i in range(0, len(decimal_hex), 2)]
    reversed_hex_array = hex_array[::-1]  # 反转数组
    reversed_hex_number = ''.join(reversed_hex_array)
    dec = int(reversed_hex_number, 16)
    return dec

# 修改文件十六进制函数
def modify_file_hex(file_path, original, replacement):
    # 将整数转换为十六进制形式
    original_hex = DEC_to_HEX(original)
    replacement_hex = DEC_to_HEX(replacement)

    # 要搜索和替换的十六进制序列
    search_seq = bytes.fromhex(original_hex)
    replace_seq = bytes.fromhex(replacement_hex)

    # 搜索序列前的偏移量（以字节为单位）
    offset_before_search_seq = 0

    # 读取文件内容
    with open(file_path, "rb") as file:
        file_contents = file.read()

    # 查找搜索序列的位置
    search_index = file_contents.rfind(search_seq)

    # 检查是否找到了序列
    if search_index == -1:
        print(colored(f"{HEX_to_DEC(original_hex)}未找到指定的搜索序列。", 'yellow')) 
    else:
        # 计算需要修改的序列的偏移位置
        replace_index = search_index - offset_before_search_seq

        # 检查偏移量是否导致替换位置超出文件开始位置
        if replace_index < 0:
            print(colored("偏移量导致替换位置超出文件开始位置。", 'red'))
        else:
            # 输出搜索到的序列的偏移位置和偏移后的值
            color = random.choice(RAINBOW_COLORS)
            print(colored(f"搜索的十六进制偏移位置: {hex(search_index)}", color))
            print(colored(f"需要修改的十六进制偏移位置及值 {hex(replace_index)}: {file_contents[replace_index:replace_index + 4].hex()}", color))

            # 创建一个新文件内容的副本,用于修改
            new_contents = bytearray(file_contents)

            # 将替换后的值写入到指定位置
            new_contents[replace_index:replace_index + 4] = replace_seq

            # 输出修改后的序列的偏移位置和偏移后的值
            print(colored(f"修改后的十六进制偏移位置 {hex(replace_index)}: {new_contents[replace_index:replace_index + 4].hex()}", 'green'))

            # 将修改后的内容写回文件
            with open(file_path, "wb") as file:
                file.write(new_contents)

            print(colored(f"文件已成功编辑", 'green', attrs=['bold']))

# 显示作者信息
show_author_info()

# 提示用户输入配置文件路径和.dat文件路径
print(colored("\n" + "="*50, 'cyan'))
config_file_path = input(colored("请输入配置路径: ", 'green'))
dat_path = input(colored("请输入dat文件路径: ", 'green'))
print(colored("="*50, 'cyan'))

try:
    config_module = importlib.machinery.SourceFileLoader('config_module', config_file_path).load_module()
    integers = config_module.array
except ImportError:
    print(colored("配置错误", 'red', attrs=['bold']))
    exit()

if not integers:
    print(colored("配置中格式错误", 'red', attrs=['bold']))
    exit()

# 循环遍历配置数组
for i in range(len(integers)):
    print(colored(f"\n处理第 {i+1}/{len(integers)} 个配置项", 'yellow', attrs=['bold']))
    modify_file_hex(dat_path, integers[i][0], integers[i][1])
    print(colored("-"*50, 'magenta'))

print(colored("\n所有修改已完成！", 'green', attrs=['bold', 'reverse']))