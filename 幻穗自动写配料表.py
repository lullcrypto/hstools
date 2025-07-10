import os
import re

def process_line(line):
    """
    严格匹配格式：[数字列表], # 注释内容
    返回处理后的字符串或None
    """
    pattern = r'^\s*\[[\d,\s]+\],\s*#\s*(.*)$'
    match = re.match(pattern, line)
    
    if not match:
        return None
    
    comment = match.group(1).strip()
    
    # 替换第一个中文/英文逗号为等号，并清理空格
    processed = re.sub(r'[，,]\s*', '=', comment, count=1)
    return re.sub(r'\s*=\s*', '=', processed, count=1)

def main():
    print(r"""
  _    _  ____  ____  _     ____  ____  
 | |  | |/ ___||  _ \| |   | __ )| __ ) 
 | |__| |\___ \| |_) | |   |  _ \|  _ \ 
 |  __  | ___) |  __/| |___| |_) | |_) |
 |_|  |_||____/|_|   |_____|____/|____/ 
幻穗配料表生成 v1版 v1.1
""")
    
    src_path = input("请输入.py文件完整路径：")
    dest_dir = "/storage/emulated/0/幻穗制作区/幻穗写配料表"
    dest_path = os.path.join(dest_dir, "配料表.txt")
    
    try:
        with open(src_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        results = []
        for idx, line in enumerate(lines, 1):
            processed = process_line(line)
            if processed:
                results.append(processed)
                print(f"第{idx}行：有效数据 -> {processed}")
            else:
                print(f"第{idx}行：格式不符（已跳过）")
        
        os.makedirs(dest_dir, exist_ok=True)
        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(results))
        
        print(f"\n成功处理 {len(results)} 条有效数据")
        print(f"保存路径：{dest_path}")
        
    except Exception as e:
        print(f"\n处理异常：{str(e)}")
        print("建议操作：请检查：")
        print("1. 文件路径是否正确")
        print("2. 文件是否具有读取权限")
        print("3. 文件编码是否为UTF-8")

if __name__ == "__main__":
    main()