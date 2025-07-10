import sys
import os
import importlib.util
from itertools import cycle
import shutil
# 移除了colorama相关导入和初始化

def remove_pycache():
    # 删除当前目录及其子目录下的所有 __pycache__ 文件夹
    for dirpath, dirnames, filenames in os.walk('.'):
        if "__pycache__" in dirnames:
            pycache_dir = os.path.join(dirpath, "__pycache__")
            shutil.rmtree(pycache_dir)  # 删除 __pycache__ 文件夹

# 简化文本输出函数
def simple_text(text):
    return text

# 获取文件路径
file_path = input(simple_text("请输入dat文件的路径: "))
# 获取配置文件路径
config_file_path = input(simple_text("请输入配置文件的路径: "))
# 获取要添加的十六进制字符串
additional_hex = input(simple_text("请输入特征码: "))

# 动态加载配置文件
try:
    spec = importlib.util.spec_from_file_location("config_module", config_file_path)
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)
    integers = config_module.array
except Exception as e:
    print(f"配置错误: {e}")
    exit()
if not integers:
    print("配置中格式错误")
    exit()

# 创建一个函数
def DEC_to_HEX(decimal_number, additional_hex):
    try:
        hex_number = format(int(decimal_number), '08X')  # '08X' 表示输出为8位十六进制数,不足部分用0填充
    except ValueError:
        print(f"无效的十进制数: {decimal_number}")
        return None
    hex_array = [hex_number[i:i + 2] for i in range(0, len(hex_number), 2)]
    reversed_hex_array = hex_array[::-1]  # 反转数组
    reversed_hex_number = ''.join(reversed_hex_array)
    print(f"{decimal_number} 转换为：{reversed_hex_number}")
    return reversed_hex_number + additional_hex  # 添加用户输入的十六进制字符串

# 修改文件十六进制函数
def modify_file_hex(file_path, A, B):
    search_seq1 = bytes.fromhex(A)
    search_seq2 = bytes.fromhex(B)
    try:
        with open(file_path, "rb") as file:
            file_contents = file.read()
    except FileNotFoundError:
        print(f"文件未找到: {file_path}")
        return False
    search_index1 = file_contents.find(search_seq1)
    search_index2 = file_contents.find(search_seq2)
    if search_index1 == -1 or search_index2 == -1:
        print("未找到指定的搜索序列。")
        return False
    data_to_replace1 = file_contents[search_index1:search_index1 + len(search_seq1)]
    data_to_replace2 = file_contents[search_index2:search_index2 + len(search_seq2)]
    new_contents = bytearray(file_contents)
    new_contents[search_index2:search_index2 + len(search_seq1)] = data_to_replace1
    new_contents[search_index1:search_index1 + len(search_seq2)] = data_to_replace2
    try:
        with open(file_path, "wb") as file:
            file.write(new_contents)
    except Exception as e:
        print(f"写入文件时出错: {e}")
        return False
    print("文件已编辑")
    return True

# 循环遍历二维数组
for i in range(len(integers)):
    A = DEC_to_HEX(integers[i][0], additional_hex)
    B = DEC_to_HEX(integers[i][1], additional_hex)
    if A is None or B is None:
        print(f"跳过无效的代码对: {integers[i][0]} -> {integers[i][1]}")
        continue
    success = modify_file_hex(file_path, A, B)
    if not success:
        print(f"处理第 {i+1} 组代码失败: {integers[i][0]} -> {integers[i][1]}")
    else:
        print(f"处理第 {i+1} 组代码成功: {integers[i][0]} -> {integers[i][1]}")
    print("----------------------------------------------------")
remove_pycache()