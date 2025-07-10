import os
import time
import re
from datetime import datetime, timedelta

# 定义文件路径
metro_file = "/storage/emulated/0/幻穗制作区/地铁.h"
classic_file = "/storage/emulated/0/幻穗制作区/经典.h"
output_dir = "/storage/emulated/0/幻穗制作区/地铁写配置/"

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

# 当前打开的文件和打开时间
current_file = None
file_start_time = None

# HS LOGO
HS_LOGO = r"""
███████╗██╗  ██╗    ██████╗ ███████╗██████╗ ███████╗███████╗██╗  ██╗
██╔════╝██║  ██║    ██╔══██╗██╔════╝██╔══██╗██╔════╝██╔════╝██║  ██║
███████╗███████║    ██████╔╝█████╗  ██████╔╝███████╗█████╗  ███████║
╚════██║██╔══██║    ██╔══██╗██╔══╝  ██╔══██╗╚════██║██╔══╝  ██╔══██║
███████║██║  ██║    ██║  ██║███████╗██║  ██║███████║███████╗██║  ██║
╚══════╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝
幻穗地铁配置 v2.0
"""

def extract_number(line):
    """从行中提取第二个数字"""
    parts = line.split(' -- ')
    if len(parts) >= 2:
        return parts[1].strip()
    return None

def extract_description(line):
    """提取描述文本"""
    parts = line.split(' -- ', 2)
    if len(parts) >= 3:
        # 获取第三个部分并移除后面的任何额外字段
        desc = parts[2].split(' -- ')[0].strip()
        return desc
    return ""

def get_current_output_file():
    """获取或创建当前输出文件"""
    global current_file, file_start_time
    
    now = datetime.now()
    # 如果没有打开文件或超过2小时，创建新文件
    if current_file is None or (now - file_start_time) > timedelta(hours=2):
        if current_file:
            current_file.close()
        
        # 生成基于时间的文件名
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        filename = f"metro_config_{timestamp}.py"
        filepath = os.path.join(output_dir, filename)
        
        current_file = open(filepath, 'a', encoding='utf-8')
        file_start_time = now
        print(f"\n📁 创建新配置文件: {filename}")
    
    return current_file

def main():
    global current_file
    
    try:
        # 显示HS LOGO
        print(HS_LOGO)
        
        # 获取第一个搜索词
        search_term1 = input("🔍 请输入地铁中搜索的内容: ").strip()
        if not search_term1:
            print("❌ 搜索词不能为空")
            return
        
        # 在地铁.h中搜索
        found_lines = []
        with open(metro_file, 'r', encoding='utf-8') as f:
            for line in f:
                if search_term1 in line:
                    found_lines.append(line.strip())
        
        if not found_lines:
            print(f"❌ 未找到包含 '{search_term1}' 的行")
            return
        
        # 显示找到的行
        print(f"\n✅ 找到 {len(found_lines)} 个匹配项:")
        for i, line in enumerate(found_lines, 1):
            print(f"{i}. {line}")
        
        # 获取第二个搜索词
        search_term2 = input("\n🔍 请输入在经典中搜索的内容: ").strip()
        if not search_term2:
            print("❌ 搜索词不能为空")
            return
        
        # 在经典.h中搜索
        found_lines2 = []
        with open(classic_file, 'r', encoding='utf-8') as f:
            for line in f:
                if search_term2 in line:
                    found_lines2.append(line.strip())
        
        if not found_lines2:
            print(f"❌ 未找到包含 '{search_term2}' 的行")
            return
        
        # 显示找到的行
        print(f"\n✅ 找到 {len(found_lines2)} 个匹配项:")
        for i, line in enumerate(found_lines2, 1):
            print(f"{i}. {line}")
        
        # 让用户选择经典文件中的行
        choice2 = int(input("\n👉 请输入要选择的经典配置行号: ")) - 1
        if choice2 < 0 or choice2 >= len(found_lines2):
            print("❌ 无效的选择")
            return
        
        selected_line2 = found_lines2[choice2]
        num2 = extract_number(selected_line2)
        if not num2:
            print("❌ 无法提取经典配置数字")
            return
        
        # 提取经典配置描述
        desc2 = extract_description(selected_line2)
        
        # 获取输出文件
        output_file = get_current_output_file()
        
        # 为地铁文件中每个匹配项生成配置
        config_count = 0
        for i, metro_line in enumerate(found_lines):
            num1 = extract_number(metro_line)
            if not num1:
                print(f"⚠️ 跳过地铁文件第 {i+1} 行，无法提取数字")
                continue
            
            desc1 = extract_description(metro_line)
            
            # 生成配置字符串 - 在描述前添加井号(#)
            config_str = f"[{num1},{num2}],#{desc1} = {desc2}"
            
            # 写入文件
            output_file.write(config_str + '\n')
            config_count += 1
            print(f"✨ 生成配置: {config_str}")
        
        # 确保写入磁盘
        output_file.flush()
        
        print(f"\n✅ 成功生成 {config_count} 条配置")
        print(f"💾 配置已保存到: {output_file.name}")
        
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
    finally:
        if current_file:
            # 不关闭文件，以便后续写入
            pass

if __name__ == "__main__":
    while True:
        main()
        print("\n" + "="*50)
        cont = input("\n是否继续生成配置? (y/n): ").strip().lower()
        if cont != 'y':
            if current_file:
                current_file.close()
                print("📂 文件已关闭")
            print("🎉 感谢使用幻穗地铁配置生成工具!")
            break