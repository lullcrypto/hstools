import os
import shutil
from datetime import datetime

# 固定文件夹路径
SOURCE_DIR = "/storage/emulated/0/幻穗制作区/幻穗dat数据存放区"
DEST_DIRS = {
    "伪实体dat": "/storage/emulated/0/幻穗制作区/自动提取dat/伪实体dat",
    "普通美化dat": "/storage/emulated/0/幻穗制作区/自动提取dat/普通美化dat",
    "淘汰播报dat": "/storage/emulated/0/幻穗制作区/自动提取dat/淘汰播报dat",
    "大厅动作dat": "/storage/emulated/0/幻穗制作区/自动提取dat/大厅动作dat",
    "地铁dat": "/storage/emulated/0/幻穗制作区/自动提取dat/地铁dat",
    "称号dat": "/storage/emulated/0/幻穗制作区/自动提取dat/称号dat",
    "头像框dat": "/storage/emulated/0/幻穗制作区/自动提取dat/头像框dat"
}

# 创建目标文件夹
for dir_name, dir_path in DEST_DIRS.items():
    os.makedirs(dir_path, exist_ok=True)
    print(f"已创建目标文件夹: {dir_name} -> {dir_path}")

def find_hex_patterns(file_path, patterns):
    """检查文件中是否包含指定的十六进制模式"""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            hex_content = content.hex().upper()
            return all(pattern.replace(" ", "").upper() in hex_content for pattern in patterns)
    except Exception as e:
        print(f"处理文件 {os.path.basename(file_path)} 时出错: {str(e)}")
        return False

def process_dat_files():
    """处理dat文件"""
    file_count = 0
    processed_count = 0
    large_files = []  # 存储40M以上的文件
    
    print(f"\n开始扫描源目录: {SOURCE_DIR}")
    
    for filename in os.listdir(SOURCE_DIR):
        if not filename.lower().endswith('.dat'):
            continue
            
        file_count += 1
        file_path = os.path.join(SOURCE_DIR, filename)
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)  # 转换为MB
        
        try:
            # 处理40M以上的文件
            if file_size_mb > 40:
                if find_hex_patterns(file_path, ["3C F9 AC 13", "F8 53 3A 01"]):
                    large_files.append((file_path, file_size_mb, filename))
                    print(f"发现大文件 [{file_size_mb:.2f}MB]: {filename}")
                continue
            
            # 分类处理其他文件
            file_processed = False
            
            # 1. 淘汰播报dat (1.34M左右)
            if not file_processed and 1.34 <= file_size_mb <= 1.50:
                if find_hex_patterns(file_path, ["73 C5 0D 00", "F2 CB 0D 00"]):
                    dest_path = os.path.join(DEST_DIRS["淘汰播报dat"], filename)
                    shutil.copy2(file_path, dest_path)
                    print(f"√ 淘汰播报dat: {filename} ({file_size_mb:.2f}MB)")
                    file_processed = True
                    processed_count += 1
            
            # 2. 大厅动作dat (1.02M左右)
            if not file_processed and 1.01 <= file_size_mb <= 1.09:
                if find_hex_patterns(file_path, ["D5 E1 21 00", "5D AA 21 00"]):
                    dest_path = os.path.join(DEST_DIRS["大厅动作dat"], filename)
                    shutil.copy2(file_path, dest_path)
                    print(f"√ 大厅动作dat: {filename} ({file_size_mb:.2f}MB)")
                    file_processed = True
                    processed_count += 1
            
            # 3. 地铁dat (1.78M左右)
            if not file_processed and 1.78 <= file_size_mb <= 2.0:
                if find_hex_patterns(file_path, ["C0 F2 7B 3A", "9C 11 7C 3A"]):
                    dest_path = os.path.join(DEST_DIRS["地铁dat"], filename)
                    shutil.copy2(file_path, dest_path)
                    print(f"√ 地铁dat: {filename} ({file_size_mb:.2f}MB)")
                    file_processed = True
                    processed_count += 1
            
            # 4. 称号dat (无大小限制)
            if not file_processed:
                if find_hex_patterns(file_path, ["6C 16 7F 12", "40 CA 7E 12"]):
                    dest_path = os.path.join(DEST_DIRS["称号dat"], filename)
                    shutil.copy2(file_path, dest_path)
                    print(f"√ 称号dat: {filename} ({file_size_mb:.2f}MB)")
                    file_processed = True
                    processed_count += 1
            
            # 5. 头像框dat (400k-500k)
            if not file_processed and 0.4 <= file_size_mb <= 0.5:
                if find_hex_patterns(file_path, ["69 88 1E 00", "51 8C 1E 00"]):
                    dest_path = os.path.join(DEST_DIRS["头像框dat"], filename)
                    shutil.copy2(file_path, dest_path)
                    print(f"√ 头像框dat: {filename} ({file_size_mb:.2f}MB)")
                    file_processed = True
                    processed_count += 1
            
            if not file_processed:
                print(f"× 未分类: {filename} ({file_size_mb:.2f}MB)")
                
        except Exception as e:
            print(f"处理文件 {filename} 时发生错误: {str(e)}")
    
    # 处理40M以上的文件
    if large_files:
        large_files.sort(key=lambda x: x[1], reverse=True)  # 按文件大小排序
        
        # 伪实体dat (最大的文件)
        largest_file = large_files[0]
        dest_path = os.path.join(DEST_DIRS["伪实体dat"], largest_file[2])
        shutil.copy2(largest_file[0], dest_path)
        print(f"★ 伪实体dat: {largest_file[2]} ({largest_file[1]:.2f}MB)")
        processed_count += 1
        
        # 普通美化dat (第二大的文件)
        if len(large_files) >= 2:
            second_largest = large_files[1]
            dest_path = os.path.join(DEST_DIRS["普通美化dat"], second_largest[2])
            shutil.copy2(second_largest[0], dest_path)
            print(f"★ 普通美化dat: {second_largest[2]} ({second_largest[1]:.2f}MB)")
            processed_count += 1
    
    print(f"\n处理完成! 共扫描 {file_count} 个DAT文件, 成功分类 {processed_count} 个文件")

if __name__ == "__main__":
    start_time = datetime.now()
    print(f"开始处理时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    process_dat_files()
    
    end_time = datetime.now()
    duration = end_time - start_time
    print(f"处理完成时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总耗时: {duration.total_seconds():.2f}秒")