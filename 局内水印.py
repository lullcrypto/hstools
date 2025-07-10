import os
import re
import ast

def encode_to_hex_utf16le(text):
    """将文本编码为 UTF-16 Little Endian 十六进制字符串"""
    return text.encode('utf-16le').hex().upper()

def replace_in_dat_file(file_path, replacements):
    """在DAT文件中查找并替换十六进制模式，保持文件大小不变"""
    if not os.path.exists(file_path):
        print(f"错误：文件 '{file_path}' 不存在")
        return False
    
    print(f"\n处理文件: {os.path.basename(file_path)}")
    
    # 读取二进制文件内容
    with open(file_path, 'rb') as f:
        content = f.read()
    
    hex_content = content.hex().upper()
    original_len = len(hex_content)
    modified = False
    
    # 执行所有替换
    for original_hex, new_hex in replacements.items():
        # 检查长度是否相同
        if len(original_hex) != len(new_hex):
            print(f"  ⚠️ 跳过: {original_hex} -> {new_hex} (长度不同 {len(original_hex)} vs {len(new_hex)})")
            continue
            
        # 统计替换次数
        count = hex_content.count(original_hex)
        
        if count > 0:
            modified = True
            print(f"  - 找到 {count} 处 {original_hex} ({decode_hex(original_hex)})")
            print(f"  - 替换为 {new_hex} ({decode_hex(new_hex)})")
            
            # 执行替换
            hex_content = hex_content.replace(original_hex, new_hex)
    
    if not modified:
        print("  - 未找到需要替换的内容")
        return False
    
    # 验证长度是否保持不变
    if len(hex_content) != original_len:
        print(f"错误: 替换后长度改变 (原长度: {original_len}, 新长度: {len(hex_content)}), 跳过写入")
        return False
    
    # 将十六进制字符串转换回字节
    try:
        new_content = bytes.fromhex(hex_content)
    except ValueError:
        print("错误: 无效的十六进制数据，跳过写入")
        return False
    
    # 写回文件
    with open(file_path, 'wb') as f:
        f.write(new_content)
    
    print(f"  - ✅ 文件已更新 (大小保持不变: {len(content)} 字节)")
    return True

def decode_hex(hex_str):
    """将十六进制字符串解码为文本(用于显示)"""
    try:
        return bytes.fromhex(hex_str).decode('utf-16le')
    except:
        return f"[无法解码: {hex_str}]"

def main():
    # 获取配置文件路径
    config_path = input("请输入Python配置文件的完整路径: ")
    
    # 读取配置文件内容
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_content = f.read()
    except Exception as e:
        print(f"读取文件错误: {e}")
        return
    
    # 提取替换规则
    try:
        # 匹配array变量中的所有内容
        match = re.search(r'array\s*=\s*\[([\s\S]*?)\]', config_content)
        if not match:
            print("在配置文件中找不到 array 定义")
            return
        
        # 提取内容并处理为规则列表
        rules_str = match.group(1).strip()
        rules = []
        
        # 按行处理
        for line in rules_str.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue  # 跳过空行和注释
                
            # 提取键值对
            if '=' in line:
                parts = line.split('=', 1)
                key = parts[0].strip()
                value = parts[1].split('#')[0].strip()  # 移除行内注释
                
                # 处理引号
                for quote in ["'", '"']:
                    if key.startswith(quote) and key.endswith(quote):
                        key = key[1:-1]
                    if value.startswith(quote) and value.endswith(quote):
                        value = value[1:-1]
                
                rules.append((key, value))
        
        if not rules:
            print("未找到有效的替换规则")
            return
            
        replacement_rules = {}
        print("\n解析的替换规则:")
        for key, value in rules:
            key_hex = encode_to_hex_utf16le(key)
            value_hex = encode_to_hex_utf16le(value)
            
            # 检查长度是否相同
            if len(key_hex) != len(value_hex):
                print(f"  ⚠️ 跳过: {key} -> {value} (十六进制长度不同 {len(key_hex)} vs {len(value_hex)})")
            else:
                replacement_rules[key_hex] = value_hex
                print(f"  ✅ {key} -> {value}")
                print(f"     原: {key_hex}")
                print(f"     新: {value_hex}")
    
    except Exception as e:
        print(f"解析配置错误: {e}")
        import traceback
        traceback.print_exc()
        return
    
    if not replacement_rules:
        print("错误: 没有有效的替换规则")
        return
    
    # 获取DAT文件路径
    dat_file_path = input("\n请输入要修改的DAT文件完整路径: ").strip()
    
    # 处理DAT文件
    replace_in_dat_file(dat_file_path, replacement_rules)

if __name__ == "__main__":
    print("=" * 50)
    print("DAT文件十六进制替换工具 (修改后文件大小不变)")
    print("=" * 50)
    main()