import os
import re
import shutil
from datetime import datetime

# 工具名称
TOOL_NAME = "\n频道:@HSMH886"

# 彩虹颜色序列（ANSI转义码）
COLORS = [
    "\033[38;5;196m",  # 红色
    "\033[38;5;208m",  # 橙色
    "\033[38;5;226m",  # 黄色
    "\033[38;5;34m",   # 绿色
    "\033[38;5;45m",   # 青色
    "\033[38;5;13m",   # 蓝色
    "\033[38;5;125m"   # 紫色
]
RESET = "\033[0m"    # 重置颜色

# 日志记录函数
def log_message(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"
    
    if level == "ERROR":
        cprint(log_entry, 0)  # 红色
    elif level == "WARNING":
        cprint(log_entry, 1)  # 橙色
    elif level == "SUCCESS":
        cprint(log_entry, 3)  # 绿色
    elif level == "INFO":
        cprint(log_entry, 4)  # 青色
    
    # 写入日志文件
    with open("modification_log.txt", "a") as log_file:
        log_file.write(log_entry + "\n")

# 彩色打印函数
def cprint(text, color_index=0):
    color = COLORS[color_index % len(COLORS)]
    print(f"{color}{text}{RESET}")

# 将整数转换为对应的字节数组（小端序）
def int_to_byte_array(num):
    return num.to_bytes(4, byteorder='little')

# 查找特征码之间的数据并进行替换（优化版）
def modify_file_hex(file_path, int_A, int_B, additional_hex, max_search_range=2048):
    hex_A_bytes = int_to_byte_array(int_A)
    hex_B_bytes = int_to_byte_array(int_B)
    
    try:
        additional_hex_bytes = bytes.fromhex(additional_hex)
    except ValueError:
        log_message(f"无效的特征码: {additional_hex}", "ERROR")
        return False

    # 创建备份文件
    backup_path = f"{file_path}.bak"
    if not os.path.exists(backup_path):
        shutil.copy2(file_path, backup_path)
        log_message(f"已创建备份文件: {backup_path}", "INFO")

    try:
        with open(file_path, "rb") as file:
            file_contents = bytearray(file.read())
    except IOError as e:
        log_message(f"文件读取失败: {e}", "ERROR")
        return False

    # 查找整数 A 和 B 的位置
    index_A = file_contents.find(hex_A_bytes)
    index_B = file_contents.find(hex_B_bytes)

    if index_A == -1:
        log_message(f"错误: 文件中未找到整数 {int_A} 的字节序列 {hex_A_bytes.hex().upper()}", "ERROR")
        return False
    if index_B == -1:
        log_message(f"错误: 文件中未找到整数 {int_B} 的字节序列 {hex_B_bytes.hex().upper()}", "ERROR")
        return False

    # 在有限范围内查找特征码
    def find_marker(start_index):
        # 限制搜索范围防止跨区域匹配
        end_index = min(start_index + max_search_range, len(file_contents))
        marker_index = file_contents.find(additional_hex_bytes, start_index, end_index)
        
        if marker_index == -1:
            log_message(f"在位置 {start_index} 后未找到特征码 (搜索范围: {end_index-start_index}字节)", "WARNING")
            return -1
        
        # 查找下一个特征码
        next_marker = file_contents.find(additional_hex_bytes, marker_index + len(additional_hex_bytes), end_index)
        return marker_index, next_marker

    # 查找A区域的特征码
    a_result = find_marker(index_A)
    if a_result == -1:
        return False
    index_A_marker, next_A_marker = a_result

    # 查找B区域的特征码
    b_result = find_marker(index_B)
    if b_result == -1:
        return False
    index_B_marker, next_B_marker = b_result

    # 计算数据块范围
    start_A = index_A_marker + len(additional_hex_bytes)
    end_A = next_A_marker if next_A_marker != -1 else len(file_contents)
    
    start_B = index_B_marker + len(additional_hex_bytes)
    end_B = next_B_marker if next_B_marker != -1 else len(file_contents)

    # 验证数据范围
    if end_A <= start_A or end_B <= start_B:
        log_message("数据范围计算无效，可能特征码距离过近或配置错误", "ERROR")
        return False

    # 提取数据块
    data_A = file_contents[start_A:end_A]
    data_B = file_contents[start_B:end_B]

    # 强制处理数据块长度不一致
    if len(data_A) != len(data_B):
        max_len = max(len(data_A), len(data_B))
        log_message(f"警告: 数据块长度不一致 (A={len(data_A)}字节, B={len(data_B)}字节)，将以0x00填充至{max_len}字节", "WARNING")
        
        # 填充较短的块
        padded_A = data_A.ljust(max_len, b'\x00')
        padded_B = data_B.ljust(max_len, b'\x00')
        
        # 执行填充后的交换
        file_contents[start_A:start_A + max_len] = padded_B
        file_contents[start_B:start_B + max_len] = padded_A
        
        log_message(f"成功: 整数 {int_A} 和 {int_B} 对应的数据块已互换（填充后长度: {max_len}字节）", "SUCCESS")
    else:
        # 长度相等时直接交换
        file_contents[start_B:start_B + len(data_B)] = data_A
        file_contents[start_A:start_A + len(data_A)] = data_B
        log_message(f"成功: 整数 {int_A} 和 {int_B} 对应的数据块已互换", "SUCCESS")

    # 写回文件
    try:
        with open(file_path, "wb") as file:
            file.write(file_contents)
        return True
    except IOError as e:
        log_message(f"文件写入失败: {e}", "ERROR")
        return False

# 读取配置文件（增强版）
def read_config(config_path):
    pairs = []
    config_pattern = re.compile(r'^\s*\[?\s*(\d+)\s*,\s*(\d+)\s*\]?\s*,?\s*(#.*)?$')
    
    try:
        with open(config_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                # 去除注释
                line = line.split('#', 1)[0].strip()
                if not line:
                    continue
                
                # 使用正则表达式匹配
                match = config_pattern.match(line)
                if match:
                    try:
                        a = int(match.group(1))
                        b = int(match.group(2))
                        pairs.append((a, b))
                    except ValueError:
                        log_message(f"第 {line_num} 行包含非整数数据: {line}", "WARNING")
                else:
                    log_message(f"第 {line_num} 行格式错误: {line}", "WARNING")
    except IOError as e:
        log_message(f"配置文件读取失败: {e}", "ERROR")
    
    return pairs

# 主函数（优化版）
def main():
    # 彩虹标题
    title_lines = TOOL_NAME.split('\n')
    for i, line in enumerate(title_lines):
        cprint(line, i)
    
    # 用户输入
    file_path = input("请输入原版载具dat文件路径: ")
    config_path = input("请输入配置文件路径: ")
    additional_hex = input("请输入特征码(回车使用默认特征码 '6002'): ").strip() or "6002"
    
    log_message(f"文件路径: {file_path}", "INFO")
    log_message(f"配置文件: {config_path}", "INFO")
    log_message(f"使用特征码: {additional_hex}", "INFO")

    # 验证文件存在
    if not os.path.isfile(file_path):
        log_message(f"文件不存在: {file_path}", "ERROR")
        return
    if not os.path.isfile(config_path):
        log_message(f"配置文件不存在: {config_path}", "ERROR")
        return

    # 读取配置
    pairs = read_config(config_path)
    if not pairs:
        log_message("配置文件中未找到有效的整数对", "ERROR")
        return
    
    log_message(f"找到 {len(pairs)} 组需要处理的整数对", "INFO")

    # 处理每个整数对
    success_count = 0
    for idx, (int_A, int_B) in enumerate(pairs):
        log_message(f"处理进度: {idx+1}/{len(pairs)} - 正在处理整数对: {int_A} 和 {int_B}", "INFO")
        if modify_file_hex(file_path, int_A, int_B, additional_hex):
            success_count += 1
    
    # 最终报告
    log_message(f"处理完成! 成功交换 {success_count}/{len(pairs)} 组数据块", 
                "SUCCESS" if success_count == len(pairs) else "WARNING")
    
    if success_count < len(pairs):
        log_message(f"有 {len(pairs)-success_count} 组数据未能成功交换，请查看日志了解详情", "WARNING")

if __name__ == "__main__":
    main()
        