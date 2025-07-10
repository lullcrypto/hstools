import os
import time
import sys

# 彩虹颜色的ANSI颜色代码
RAINBOW = [
    "\033[38;5;196m",  # 红色
    "\033[38;5;202m",  # 橙色
    "\033[38;5;226m",  # 黄色
    "\033[38;5;40m",   # 绿色
    "\033[38;5;45m",   # 青色
    "\033[38;5;21m",   # 蓝色
    "\033[38;5;54m",   # 紫色
]
RESET = "\033[0m"  # 重置颜色

# 脚本信息
script_info = {
    "name": "自动语音包",
    "author": "幻穗",
    "QQ": "3111545189",
    "telegram": "@HSMHYYNB",
    "run_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
    "run_count": 1
}

# 彩虹文本生成函数
def rainbow_text(text):
    colored_text = ""
    color_index = 0
    for char in text:
        colored_text += RAINBOW[color_index % len(RAINBOW)] + char
        color_index += 1
    colored_text += RESET
    return colored_text

# 显示启动界面
def display_welcome():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # 创建HSTOOL ASCII艺术
    print("\n")
    print(rainbow_text("▀█▀ █▀█░█▀█  █░ HSTOOL v1"))
    print(rainbow_text("░█░ █░█  █  █░█░░"))
    print(rainbow_text("░█ ░███  █▄█░█▄▄░v1"))
    
    # 创建信息框
    print("┌─────────────────────────────────────┐")
    print("│ ➤ " + RAINBOW[0] + "Version: 1.0" + RESET + "   ⌘ " + RAINBOW[1] + "Channel: @HSMH" + RESET + " │")
    print("└─────────────────────────────────────┘")
    
    # 创建标题框
    print("╔═════════════════⋆★⋆══════════════════╗")
    print(rainbow_text("║░░░░░░░░░░░ 𝗛𝗦𝗧𝗢𝗢𝗟 𝗔𝘂𝘁𝗼 𝗩𝗼𝗶𝗰𝗲 ░░░░░░░░░░║"))
    print("╚══════════════════════════════════════╝")
    
    # 显示加载动画
    print(RAINBOW[2] + "正在加载幻穗语音包工具..." + RESET)
    for _ in range(3):
        for frame in ['◐', '◓', '◑', '◒']:
            sys.stdout.write('\r' + RAINBOW[3] + frame + " 处理中..." + RESET)
            sys.stdout.flush()
            time.sleep(0.1)
    print("\r[✓] 加载完成!                       ")
    
    # 显示系统信息
    print("\n" + RAINBOW[4] + "🕒 执行时间: " + script_info["run_time"])
    print(RAINBOW[5] + "👤 作者: " + script_info["author"])
    print(RAINBOW[6] + "📱 QQ: " + script_info["QQ"])
    print(RAINBOW[0] + "📢 Telegram: " + script_info["telegram"])
    print(RAINBOW[1] + "💎 使用次数: " + str(script_info["run_count"]) + "次")
    print(RESET + "---------------------------------------")

# 显示进度条
def progress_bar(current, total, width=40):
    filled = int(width * current / total)
    bar = RAINBOW[2] + '█' * filled + RESET + '░' * (width - filled)
    percent = RAINBOW[4] + f"{current/total:.0%}" + RESET
    return f"{bar} {percent}"

# 十进制转八位十六进制（小端序）
def DEC_to_HEX(decimal_number):
    hex_number = format(int(decimal_number), '08X')
    hex_array = [hex_number[i:i+2] for i in range(0, len(hex_number), 2)]
    reversed_hex = ''.join(hex_array[::-1])
    print(rainbow_text(f"🔢 {decimal_number} → 💠 {reversed_hex}"))
    return reversed_hex

# 修复版文件修改函数
def modify_file_hex(file_path, A, B, hex_start, hex_end, start_index_A=0, start_index_B=0):
    try:
        with open(file_path, "rb") as file:
            file_data = bytearray(file.read())
    except Exception as e:
        print(rainbow_text(f"⚠ 无法读取文件 {file_path}: {e}"))
        return False

    # 查找所有A和B的位置
    a_positions = []
    b_positions = []
    search_A = bytes.fromhex(A)
    search_B = bytes.fromhex(B)

    # 查找所有A的位置
    pos = -1
    while True:
        pos = file_data.find(search_A, pos + 1)
        if pos == -1:
            break
        a_positions.append(pos)

    # 查找所有B的位置
    pos = -1
    while True:
        pos = file_data.find(search_B, pos + 1)
        if pos == -1:
            break
        b_positions.append(pos)

    # 检查是否找到足够的匹配项
    if len(a_positions) <= start_index_A or len(b_positions) <= start_index_B:
        print(rainbow_text("❌ 错误：指定的起始索引超出范围"))
        return False

    # 仅处理指定索引之后的匹配项
    a_positions = a_positions[start_index_A:]
    b_positions = b_positions[start_index_B:]

    # 确定最小处理次数
    min_count = min(len(a_positions), len(b_positions))
    if min_count == 0:
        print(rainbow_text("❌ 错误：没有可替换的匹配项"))
        return False

    # 准备特征码
    start_marker = bytes.fromhex(hex_start)
    end_marker = bytes.fromhex(hex_end)

    # 执行替换操作
    modified = False
    success_count = 0
    
    print(RAINBOW[3] + f"🔍 正在处理 {min_count} 个匹配项..." + RESET)
    
    for i in range(min_count):
        # 显示进度
        sys.stdout.write('\r' + progress_bar(i+1, min_count))
        sys.stdout.flush()
        
        a_pos = a_positions[i]
        b_pos = b_positions[i]

        # 查找A的起始和结束位置
        a_start = file_data.rfind(start_marker, 0, a_pos)
        a_end = file_data.find(end_marker, a_start, a_pos)
        if a_start == -1 or a_end == -1:
            continue

        # 查找B的起始和结束位置
        b_start = file_data.rfind(start_marker, 0, b_pos)
        b_end = file_data.find(end_marker, b_start, b_pos)
        if b_start == -1 or b_end == -1:
            continue

        # 提取要交换的数据
        a_data = file_data[a_start+len(start_marker):a_end]
        b_data = file_data[b_start+len(start_marker):b_end]

        # 执行交换
        file_data[b_start+len(start_marker):b_end] = a_data
        file_data[a_start+len(start_marker):a_end] = b_data
        modified = True
        success_count += 1

    # 保存修改
    if modified:
        try:
            with open(file_path, "wb") as file:
                file.write(file_data)
            print("\n" + rainbow_text(f"✅ 文件 {os.path.basename(file_path)} 修改成功 ({success_count} 处修改)"))
            return True
        except Exception as e:
            print(rainbow_text(f"❌ 无法写入文件 {file_path}: {e}"))
    else:
        print("\n" + rainbow_text("⚠ 未找到可修改的内容"))
    return False

# 主程序
def main():
    script_info["run_count"] += 1
    display_welcome()

    # 获取用户输入
    print("\n" + rainbow_text("📂 请输入文件路径: "))
    file_path = input(">>> ")
    
    print("\n" + rainbow_text("📝 请输入包含数组的文件路径: "))
    array_file_path = input(">>> ")
    
    print("\n" + rainbow_text("🔑 类型特征码: "))
    hex_start = input(">>> ")
    
    print("\n" + rainbow_text("🔑 型型特征码: "))
    hex_end = input(">>> ")
    
    # 读取配置文件
    try:
        with open(array_file_path, 'r') as file:
            config_array = eval(file.read())
        if not isinstance(config_array, list):
            raise ValueError("配置文件格式错误")
    except Exception as e:
        print(rainbow_text(f"❌ 配置文件错误: {e}"))
        return

    # 处理每个配置项
    total = len(config_array)
    success_count = 0
    
    print(rainbow_text(f"\n🔧 开始处理 {total} 个配置项"))
    print(rainbow_text("══════════════════════════════"))
    
    for idx, config in enumerate(config_array, 1):
        if len(config) != 2:
            print(rainbow_text(f"⚠ 配置第{idx}行格式错误，跳过"))
            continue

        print(rainbow_text(f"\n🔧 处理第 {idx}/{total} 行配置"))
        print(rainbow_text(f"🔠 配置内容: {config}"))
        
        A_hex = DEC_to_HEX(config[0])
        B_hex = DEC_to_HEX(config[1])
        
        print(rainbow_text(f"💠 A的十六进制值: {A_hex}"))
        print(rainbow_text(f"💠 B的十六进制值: {B_hex}"))

        # 统计出现次数
        try:
            with open(file_path, "rb") as file:
                                data = file.read()
            a_count = data.count(bytes.fromhex(A_hex))
            b_count = data.count(bytes.fromhex(B_hex))
            print(rainbow_text(f"🔢 A出现次数: {a_count}"))
            print(rainbow_text(f"🔢 B出现次数: {b_count}"))
        except Exception as e:
            print(rainbow_text(f"❌ 读取文件失败: {e}"))
            continue

        # 用户确认
        choice = input(rainbow_text("❓ 是否修改? (1: 修改, 其他: 跳过): "))
        if choice != '1':
            print(rainbow_text("⏭️ 跳过当前配置"))
            continue

        # 获取起始索引
        try:
            start_a = int(input(rainbow_text(f"📍 从第几个A开始修改? (1-{a_count}): "))) - 1
            start_b = int(input(rainbow_text(f"📍 从第几个B开始修改? (1-{b_count}): "))) - 1
        except ValueError:
            print(rainbow_text("⚠ 输入无效，使用默认值0"))
            start_a = start_b = 0

        # 执行修改
        if modify_file_hex(file_path, A_hex, B_hex, hex_start, hex_end, start_a, start_b):
            success_count += 1
            print(rainbow_text(f"✅ 第{idx}行配置修改成功"))
        else:
            print(rainbow_text(f"❌ 第{idx}行配置修改失败"))

        print(rainbow_text("──────────────────────────────"))

    # 最终统计
    print(rainbow_text("\n══════════════════════════════"))
    print(rainbow_text(f"📊 处理完成: {success_count}/{total} 项成功"))
    
    # 显示退出信息
    print("\n" + rainbow_text("▀█▀ █▀█░█▀█  █░ HSTOOL v1"))
    print(rainbow_text("        ░█░ █░█  █  █░█░░"))
    print(rainbow_text("      ░  █ ░███  █▄█░█▄▄░v1"))
    print(rainbow_text("\n💎 感谢使用幻穗TOOL"))
    input(rainbow_text("\n按任意键退出..."))

if __name__ == "__main__":
    main()