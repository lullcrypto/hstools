import os
import re
from datetime import datetime

def get_file_path():
    """询问用户输入.h文件路径"""
    while True:
        file_path = input("请输入.h文件的完整路径: ").strip()
        if os.path.isfile(file_path) and file_path.endswith('.h'):
            return file_path
        print("错误: 文件不存在或不是.h文件，请重新输入。")

def process_content(content):
    """处理文件内容，转换格式"""
    # 转换时间戳
    timestamp = datetime.now().strftime("// 转换时间: %Y-%m-%d %H:%M:%S\n\n")
    
    # 转换格式的正则表达式
    pattern = re.compile(r'(\d+)--(\d+)--\[([^\]]+)\]')
    
    # 替换为指定格式
    processed_content = pattern.sub(r'\1 -- \2 -- \3 -- 0x7B038', content)
    
    return timestamp + processed_content

def main():
    print("=== .h文件格式转换工具 ===")
    file_path = get_file_path()
    
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as file:
            original_content = file.read()
        
        # 处理内容
        new_content = process_content(original_content)
        
        # 备份原文件
        backup_path = file_path + '.bak'
        os.rename(file_path, backup_path)
        print(f"已创建备份文件: {backup_path}")
        
        # 写入新内容
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        print("格式转换完成！")
    
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")

if __name__ == "__main__":
    main()