import os
import subprocess
import datetime
import json
from colorama import Fore, Style
import shutil
import hashlib
import time

viod = "           "
# 标准目录
directories = [
    "/storage/emulated/0/幻穗制作区/",
    "/storage/emulated/0/幻穗制作区/pak/",          # 待解包/打包的pak位置
    "/storage/emulated/0/幻穗制作区/uexp打包/",      # 待打包的文件存放位置
    "/storage/emulated/0/幻穗制作区/uexp解包/",      # 解包输出位置
    "/storage/emulated/0/幻穗制作区/dat打包/",
    "/storage/emulated/0/幻穗制作区/dat解包/"
]

# 创建目录（若不存在）
for directory in directories:
    try:
        os.makedirs(directory, exist_ok=True)
    except Exception as e:
        print(f"Failed to create directory {directory}. Error: {e}")

def copy_file(src, dst):
    try:
        shutil.copyfile(src, dst)
    except IOError as e:
        print(f"Unable to copy file. {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def copy_only_directories(src_dir, dst_dir):
    for root, dirs, files in os.walk(src_dir):
        rel_path = os.path.relpath(root, src_dir)
        dst_path = os.path.join(dst_dir, rel_path) if rel_path != '.' else dst_dir
        os.makedirs(dst_path, exist_ok=True)

def toast(str):
    count = 0
    total = 3
    start = time.time()
    while count < total:
        time.sleep(1)
        cur = time.time()
        count += 1
        pd = count * 73 // total
        runtime = int(cur - start)
        estremain = (runtime * total // count) - runtime
        percent = count * 100 // total
        tenths = (count * 1000 // total) % 10
        minutes = estremain // 60
        seconds = estremain % 60
        print(f"\r{percent}.{tenths}% complete - est {minutes}:{seconds:02d} remaining", end="")
    print(f"\n{str}完成")

def gradient_text(text, start_color, end_color):
    start_rgb = [int(start_color[i:i+2], 16) for i in (0, 2, 4)]
    end_rgb = [int(end_color[i:i+2], 16) for i in (0, 2, 4)]
    gradient = ''
    for i in range(len(text)):
        ratio = i / len(text)
        rgb = [int(start_rgb[j] + (end_rgb[j] - start_rgb[j]) * ratio) for j in range(3)]
        gradient += f"\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m{text[i]}"
    return gradient + Style.RESET_ALL

def get_current_datetime():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

def list_files_in_directory(directory, file_extension):
    try:
        if not os.path.exists(directory):
            raise FileNotFoundError(f"找不到目录: '{directory}'")
        files = os.listdir(directory)
        target_files = [file for file in files if file.endswith(file_extension)]
        if not target_files:
            print(gradient_text(f"找不到扩展名为 {file_extension} 在目录中 {directory}.", "FF0000", "FFFFFF"))
            return None
        print(gradient_text(f"目录中的文件 {directory}: ", "00FF00", "FFFFFF"))
        for index, file_name in enumerate(target_files, start=1):
            print(gradient_text(f"{index}) {file_name}", "0000FF", "00FFFF"))
        return target_files
    except FileNotFoundError as e:
        print(gradient_text(str(e), "FF0000", "FFFFFF"))
    except PermissionError:
        print(gradient_text(f"拒绝访问目录: '{directory}.", "FF0000", "FFFFFF"))
    except Exception as e:
        print(gradient_text(f"目录访问错误: {e}", "FF0000", "FFFFFF"))
    return None

def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(gradient_text(result.stdout.strip(), "00FF00", "FFFFFF"))
    except subprocess.CalledProcessError as e:
        print(gradient_text(f"命令执行错误: {e}\n{e.stderr.strip()}", "FF0000", "FFFFFF"))
def yunmeng():
    directory = directories[1]
    files = list_files_in_directory(directory, '.pak')
    if files:
        index_input = input(gradient_text("输入要解包的pak索引文件（或输入0返回）: ", "00FF00", "FFFFFF")).strip()
        if index_input == '0':
            return
        if not index_input:
            print(gradient_text("输入不能为空，请再试一次", "FF0000", "FFFFFF"))
            return
        try:
            index = int(index_input) - 1
            if 0 <= index < len(files):
                base_name = os.path.splitext(os.path.basename(os.path.join(directory, files[index])))[0]
                OUTPUTNC = os.path.join(f"{directories[3]}64kbuexp限制", base_name)
                if os.path.isdir(OUTPUTNC):
                    pd = input(gradient_text("解包文件已存在(是否重新解包y/n): ", "FF0000", "FFFFFF"))
                    if pd == 'y':
                        execute_command(f"rm -rf {OUTPUTNC}/*")
                    else:
                        return
                else:
                    os.makedirs(OUTPUTNC)
                command = f"./paks -a \"{os.path.join(directory, files[index])}\" {OUTPUTNC}"
                subprocess.run(command, shell=True)
                copy_only_directories(f"{OUTPUTNC}", f"{directories[2]}{base_name}")
                toast("解包")
            else:
                print(gradient_text("无效索引，请再试一次", "FF0000", "FFFFFF"))
        except ValueError:
            print(gradient_text("请输入一个有效的整数", "FF0000", "FFFFFF"))
def yunemengnb():
    pak_dir = directories[1]
    uexp_dir = directories[2]
    
    # 显示pak目录中的pak文件
    print(gradient_text("\n===== pak目录中的文件 =====", "00FF00", "FFFFFF"))
    pak_files = list_files_in_directory(pak_dir, '.pak')
    if not pak_files:
        print(gradient_text("pak目录中无pak文件，无法打包", "FF0000", "FFFFFF"))
        return
    
    # 选择目标pak
    index_input = input(gradient_text("输入目标pak的索引（或输入0返回）: ", "00FF00", "FFFFFF")).strip()
    if index_input == '0':
        return
    if not index_input:
        print(gradient_text("输入不能为空，请再试一次", "FF0000", "FFFFFF"))
        return
    
    try:
        index = int(index_input) - 1
        if 0 <= index < len(pak_files):
            pak_file = pak_files[index]
            pak_path = os.path.join(pak_dir, pak_file)
            pak_base_name = os.path.splitext(pak_file)[0]
            
            # 显示uexp打包目录内容
            print(gradient_text(f"\n===== uexp打包目录内容（将打包到 {pak_file}）=====", "00FF00", "FFFFFF"))
            uexp_files = os.listdir(uexp_dir)
            if not uexp_files:
                print(gradient_text("uexp打包目录中无文件，无法打包", "FF0000", "FFFFFF"))
                return
            for file in uexp_files:
                print(f"- {file}")
                
            command = f"./paks -a -r \"{pak_path}\" \"{uexp_dir}\""
            print(gradient_text(f"执行打包命令: {command}", "00FFFF", "FFFFFF"))
            subprocess.run(command, shell=True)
            
            # 显示进度和MD5
            toast("打包")
            new_md5 = hashlib.md5(open(pak_path, 'rb').read()).hexdigest()
            print(gradient_text(f"打包后MD5: {new_md5}", "FF0000", "FFFFFF"))
            
            # 显示打包后pak目录内容（移除display_msg参数）
            print(gradient_text("\n===== 打包后pak目录内容 =====", "00FF00", "FFFFFF"))
            list_files_in_directory(pak_dir, '.pak')  # 此处删除display_msg=True
            
        else:
            print(gradient_text("无效索引，请再试一次", "FF0000", "FFFFFF"))
    except ValueError:
        print(gradient_text("请输入一个有效的整数", "FF0000", "FFFFFF"))
if __name__ == "__main__":
    yunemengnb()
