import os
import shutil
import sys
from termcolor import colored
from time import sleep

# ============= 视觉模块 =============
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(colored(r'''    _    _  _____ _______  ____ ___  _ 
   | |  |  |/ ____|__   __|/ __ \ / _ \| |
   | |__|  | (___    | |  | |  | | | | | |
   |  __  | \___ \   | |  | |  | | | | | |
   | |  |  |____) |  | |  | |__| | |_| |_|
   |_|  | _|_____/   |_|   \____/ \___/(_)

    ''', 'magenta'))
    print(colored("⋆⁺₊⋆ ☾⋆⁺₊⋆ 幻穗DAT提取工具 ⋆⁺₊⋆ ☾⋆⁺₊⋆".center(50), 'cyan', attrs=['bold']))
    print(colored("═"*60 + "\n", 'blue'))

def dynamic_spinner():
    frames = ['◐', '◓', '◑', '◒']
    while True:
        for frame in frames:
            yield colored(frame, 'cyan')

def progress_bar(current, total):
    bar_length = 30
    filled = int(bar_length * current / total) if total > 0 else 0
    return colored('█'*filled + '░'*(bar_length-filled), 'magenta')

# ============= 核心功能 =============
def magical_input(prompt, default=None):
    spinner = dynamic_spinner()
    while True:
        sys.stdout.write(f"\r{next(spinner)} {colored(prompt, 'cyan')}")
        sys.stdout.flush()
        user_input = input('\r' + ' '*80 + '\r').strip()
        if default and not user_input:
            return default
        if user_input:
            return user_input

def validate_hex(hex_str):
    clean_hex = hex_str.replace(" ", "").replace(":", "").upper()
    try:
        if len(clean_hex) % 2 != 0:
            err_pos = len(clean_hex)//2
            raise ValueError(f"无效长度 → {clean_hex[:err_pos]}❌{clean_hex[err_pos:]}")
        bytes.fromhex(clean_hex)
        return " ".join([clean_hex[i:i+2] for i in range(0, len(clean_hex), 2)])
    except ValueError as e:
        print(colored(f"\n⚠ {str(e)}", 'yellow'))
        sleep(1)
        return None

def main_flow():
    clear_screen()
    
    # 十六进制输入
    while True:
        hex_pattern = magical_input("请输入幻影代码 (例: 94 24 FF 05)")
        verified_hex = validate_hex(hex_pattern)
        if verified_hex: break

    # 路径设置
    search_path = magical_input("搜索目录", "/storage/emulated/0/幻穗制作区/幻穗dat数据存放区")
    save_path = magical_input("保存位置", "/storage/emulated/0/幻穗制作区/幻穗dat提取结果")
    os.makedirs(save_path, exist_ok=True)

    # 准备搜索
    clear_screen()
    print(colored("\n🔮 正在启动星轨扫描系统...", 'cyan'))
    sleep(1)
    
    print(colored(f"\n{' 星图参数 ':━^50}", 'white', 'on_blue'))
    print(f"{colored('✦', 'magenta')} 目标代码: {colored(verified_hex, 'cyan')}")
    print(f"{colored('✦', 'magenta')} 扫描路径: {colored(search_path, 'cyan')}")
    print(f"{colored('✦', 'magenta')} 星轨存档: {colored(save_path, 'cyan')}\n")

    # 执行扫描
    dat_files = [f for f in os.listdir(search_path) if f.lower().endswith('.dat')]
    total = len(dat_files)
    found = 0

    print(colored(f"{' 星轨扫描进度 ':━^50}", 'white', 'on_blue'))
    for idx, filename in enumerate(dat_files, 1):
        file_path = os.path.join(search_path, filename)
        
        # 进度显示
        sys.stdout.write(f"\r{progress_bar(idx, total)} {colored(f'{idx/total:.0%}', 'yellow')}")
        sys.stdout.flush()

        try:
            with open(file_path, 'rb') as f:
                if bytes.fromhex(verified_hex.replace(" ", "")) in f.read():
                    shutil.copy(file_path, save_path)
                    found += 1
                    print(colored(f"\n✨ 星标文件: {filename}", 'green', attrs=['bold']))
        except Exception as e:
            print(colored(f"\n🌀 星际乱流: {filename} - {str(e)}", 'red'))

    # 最终报告
    print(colored(f"\n\n{' 星轨扫描报告 ':━^50}", 'white', 'on_blue'))
    print(f"{colored('⌛', 'cyan')} 已扫描星体: {colored(total, 'yellow')}")
    print(f"{colored('💎', 'magenta')} 捕获星核: {colored(found, 'green' if found else 'red')}")
    print(f"{colored('📁', 'cyan')} 星核仓库: {colored(save_path, 'cyan')}\n")

if __name__ == "__main__":
    try:
        main_flow()
    except KeyboardInterrupt:
        print(colored("\n🌌 星轨扫描已中断", 'red'))
    except Exception as e:
        print(colored(f"\n💥 超新星爆发: {str(e)}", 'red', attrs=['bold']))