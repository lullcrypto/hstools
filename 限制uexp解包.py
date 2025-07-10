import os
import subprocess
import datetime
import json
from colorama import Fore, Style
import shutil
import hashlib
import time
viod = "           "
# Стандартные директории
directories = [
    "/storage/emulated/0/幻穗制作区/",
    "/storage/emulated/0/幻穗制作区/pak/",          # 待解包/打包的pak位置
    "/storage/emulated/0/幻穗制作区/uexp打包/",      # 待打包的文件存放位置
    "/storage/emulated/0/幻穗制作区/uexp解包/",      # 解包输出位置
    "/storage/emulated/0/幻穗制作区/dat打包/",
    "/storage/emulated/0/幻穗制作区/dat解包/"
]
for directory in directories:
    try:
        os.makedirs(directory, exist_ok=True)  # exist_ok=True 表示如果目录已经存在，不会抛出异常
        #print(f"Created or already exists: {directory}")
        pass
    except Exception as e:
        print(f"Failed to create directory {directory}. Error: {e}")
        
def copy_file(src, dst):
    """
    复制文件从src到dst。
    :param src: 源文件路径
    :param dst: 目标文件路径
    """
    #print(f"{src}\n{dst}")
    try:
        shutil.copyfile(src, dst)
        #print(f"File copied successfully from {src} to {dst}")
    except IOError as e:
        print(f"Unable to copy file. {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
def copy_only_directories(src_dir, dst_dir):
    """
    仅复制源目录下的所有子目录结构到目标目录中，不包括文件。
    :param src_dir: 源目录路径
    :param dst_dir: 目标目录路径
    """
    for root, dirs, files in os.walk(src_dir):
        # 计算相对于源目录的相对路径
        rel_path = os.path.relpath(root, src_dir)
        # 构建目标目录的完整路径
        dst_path = os.path.join(dst_dir, rel_path) if rel_path != '.' else dst_dir
        # 创建目标目录（如果尚不存在）
        os.makedirs(dst_path, exist_ok=True)
        # 打印已创建的目标目录（可选）
        #print(f"Created directory: {dst_path}")
def toast(str):
    count = 0
    total = 3
    start = time.time()
    while count < total:
        time.sleep(1)  # this is work
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
        # The \r character moves the cursor back to the beginning of the line, and end="" prevents print from adding a new line.   
    print(f"\n{str}完成")
def gradient_text(text, start_color, end_color):
    """Создает градиентный текст от start_color до end_color."""
    start_rgb = [int(start_color[i:i + 2], 16) for i in (0, 2, 4)]
    end_rgb = [int(end_color[i:i + 2], 16) for i in (0, 2, 4)]
    gradient = ''
    for i in range(len(text)):
        ratio = i / len(text)
        rgb = [int(start_rgb[j] + (end_rgb[j] - start_rgb[j]) * ratio) for j in range(3)]
        gradient += f"\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m{text[i]}"
    
    return gradient + Style.RESET_ALL
def get_current_datetime():
    """Возвращает текущую дату и время в отформатированной строке."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
def list_files_in_directory(directory, file_extension):
    """Показывает файлы в данном каталоге с заданным расширением."""
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
    """Выполняет данную команду оболочки и выводит результат или ошибку."""
    try:
        #print(command)
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(gradient_text(result.stdout.strip(), "00FF00", "FFFFFF"))  # Вывод результата команды
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
                OUTPUTNC = directories[3] 
                # 移除原有的解包文件存在判断逻辑
                command = f"./paks -a \"{os.path.join(directory, files[index])}\" {OUTPUTNC}"
                subprocess.run(command, shell=True)
                toast("解包")
            else:
                print(gradient_text("无效索引，请再试一次", "FF0000", "FFFFFF"))
        except ValueError:
            print(gradient_text("请输入一个有效的整数", "FF0000", "FFFFFF"))
def yunemengnb():
    directory = directories[1]                  
    files = list_files_in_directory(directory, '.pak')
    if files:
        index_input = input(gradient_text("输入要打包的pak索引文件（或输入0返回）: ", "00FF00", "FFFFFF")).strip()
        if index_input == '0':
            return  
        if not index_input:
            print(gradient_text("输入不能为空，请再试一次", "FF0000", "FFFFFF"))
            return  
        try:
            index = int(index_input) - 1
            if 0 <= index < len(files):
                copy_file(
                    f"{os.path.join(directory, files[index])}",
                    f"{directories[2]}{os.path.basename(os.path.join(directory, files[index]))}"
                )
                md5 = hashlib.md5(
                    open(
                        f"{directories[2]}{os.path.basename(os.path.join(directory, files[index]))}", 
                        'rb'
                    ).read()
                ).hexdigest()
                command = (
                    f"./paks -a -r "
                    f"\"{directories[2]}{os.path.basename(os.path.join(directory, files[index]))}\" "
                    f"\"{directories[2]}{os.path.splitext(os.path.basename(os.path.join(directory, files[index])))[0]}\""
                )
                subprocess.run(command, shell=True)
                toast("打包")
                newmd5 = hashlib.md5(
                    open(
                        f"{directories[2]}{os.path.basename(os.path.join(directory, files[index]))}", 
                        'rb'
                    ).read()
                ).hexdigest()
                print(gradient_text(f"原MD5: {md5}", "FF0000", "FFFFFF"))
                print(gradient_text(f"现MD5: {newmd5}", "FF0000", "FFFFFF"))
            else:
                print(gradient_text("无效索引，请再试一次", "FF0000", "FFFFFF"))
        except ValueError:
            print(gradient_text("请输入一个有效的整数", "FF0000", "FFFFFF"))
            
if __name__ == "__main__":
    yunmeng()
