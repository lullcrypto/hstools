import os
import subprocess
import time
from glob import glob

def jb():  
    print("请选择要解包的PAK文件：")
    print("0. 操作取消")
    pak_files = glob("/storage/emulated/0/幻穗制作区/pak/*.pak")
    for i, file in enumerate(pak_files, start=1):
        print(f"{i}. {os.path.basename(file)}")
    
    while True:
        try:
            choice = int(input("请输入选项："))
            if choice == 0:
                print("操作取消，正在返回...")
                time.sleep(1)
                return
            elif 1 <= choice <= len(pak_files):
                selected_file = pak_files[choice - 1]
                break
            else:
                print("无效选择，请重新输入。")
        except ValueError:
            print("无效输入，请输入数字。")
    
    output_dir = "/storage/emulated/0/幻穗制作区/uexp解包/"
    command = "./urpack -a \"{}\" \"{}\"".format(selected_file, output_dir)
    print("正在解包，请稍候...")
    result = subprocess.run(command, shell=True)
    
    if result.returncode == 0:
        print("解包成功")  # 移除文件列表显示，仅提示成功
    else:
        print(f"解包失败，错误码：{result.returncode}")
    time.sleep(1)

def main_menu():
    jb()

if __name__ == "__main__":
    main_menu()