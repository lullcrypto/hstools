import os
import re
from colorama import Fore, Style, init

init(autoreset=True)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title=""):
    clear_screen()
    print(Fore.CYAN + "═" * 60 + Style.RESET_ALL)
    print(Fore.YELLOW + Style.BRIGHT + "   HSTOOL 物品配置编写工具" + Style.RESET_ALL)
    print(Fore.CYAN + "═" * 60 + Style.RESET_ALL)
    if title:
        print(Fore.MAGENTA + Style.BRIGHT + f"   {title}" + Style.RESET_ALL)
        print(Fore.CYAN + "─" * 60 + Style.RESET_ALL)
    print()

def print_divider():
    """打印分隔线"""
    print(Fore.CYAN + "─" * 60 + Style.RESET_ALL)

def print_section(title):
    """打印加粗的章节标题"""
    print(Fore.MAGENTA + Style.BRIGHT + f"\n{title}" + Style.RESET_ALL)
    print_divider()

def read_h_file():
    file_path = "/storage/emulated/0/幻穗制作区/经典.h"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(Fore.RED + f"读取文件失败: {e}" + Style.RESET_ALL)
        print(Fore.RED + f"请确保文件存在: {file_path}" + Style.RESET_ALL)
        return None

def fuzzy_search(keyword, lines):
    results = []
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    for idx, line in enumerate(lines, 1):
        parts = line.split(' -- ')
        if len(parts) >= 3 and pattern.search(parts[2]):
            results.append((idx, line, parts))
    return results

def select_range(items, prompt):
    """选择要舍弃的项"""
    print_section("选择项列表")
    print(Fore.GREEN + f"可选项 ({len(items)}):" + Style.RESET_ALL)
    for i, (num, name) in enumerate(items, 1):
        print(f"{i}. {name}")
    
    print_divider()
    while True:
        choice = input(Fore.CYAN + Style.BRIGHT + prompt + Style.RESET_ALL)
        
        if choice.lower() == 'a':  # 全选
            return list(range(1, len(items)+1))
        
        if choice == '0':  # 放弃所有
            return []
            
        abandon_indexes = set()
        try:
            # 处理逗号分隔和范围
            parts = choice.split(',')
            for part in parts:
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    abandon_indexes.update(range(start, end+1))
                else:
                    abandon_indexes.add(int(part))
            return list(abandon_indexes)
        except:
            print(Fore.RED + "格式错误，请输入 1,3,5 或 1-3 或 a" + Style.RESET_ALL)

def extract_part_key(name):
    """从物品名称中提取部件关键字 - 增强版"""
    # 忽略包含"检视"和"换弹"的项
    if "检视" in name or "换弹" in name:
        return None
    
    # 定义部件关键词列表（按优先级排序）
    part_keywords = [
        "枪口补偿", "战术枪托", "快速扩容",  # 新增关键词
        "消音", "扩容", "快速", "快扩", "消焰", "半截式", "直角", "轻型", 
        "拇指", "垂直", "侧面", "红点", "全息", "2倍", "3倍", "4倍", "6倍", "8倍", "激光",
        "机", "瞄", "口", "托", "弹"
    ]
    
    # 改进：处理不完整的括号名称
    # 尝试匹配括号内的内容，即使括号不完整
    match = re.search(r'\(([^)]*?)(?:\)|$)', name)
    if match:
        part = match.group(1)
        # 在括号内查找关键词
        for keyword in part_keywords:
            if keyword in part:
                return keyword
    
    # 如果名称中有特定关键字，直接返回
    for keyword in part_keywords:
        if keyword in name:
            return keyword
    
    # 如果都没有，返回None
    return None

def select_item(lines, step):
    """选择物品，支持范围选择和询问是否去重"""
    prompt = f"\n>>> {step}：请输入物品名称（支持模糊搜索，0返回）: "
    while True:
        keyword = input(Fore.CYAN + Style.BRIGHT + prompt + Style.RESET_ALL)
        if keyword == '0':
            return None
            
        matches = fuzzy_search(keyword, lines)
        if not matches:
            print(Fore.YELLOW + "未找到匹配项，请重新输入" + Style.RESET_ALL)
            continue
            
        if len(matches) == 1:
            m = matches[0]
            # 返回中间数字和物品名称
            return [(m[2][1], m[2][2])]
        
        # 多个匹配项时提示范围选择
        print_header(f"{step} - 搜索到 {len(matches)} 个匹配项")
        print(Fore.YELLOW + "提示：可输入范围（如 10-20），或输入 a 选择全部，或输入单行号" + Style.RESET_ALL)
        
        # 显示匹配项（包括重复项）
        print_section("匹配结果")
        for m in matches:
            formatted_line = f"行号{m[0]}, 名称:{m[2][2]}"
            print(Fore.GREEN + formatted_line + Style.RESET_ALL)
        print_divider()
        
        # 获取用户选择
        while True:
            choice = input(Fore.CYAN + Style.BRIGHT + f">>> {step}：请选择行号范围或单行号 (a=全选): " + Style.RESET_ALL)
            
            if choice.lower() == 'a':  # 全选
                selected = matches
                break
                
            if '-' in choice:  # 范围选择
                try:
                    start, end = map(int, choice.split('-'))
                    selected = [m for m in matches if start <= m[0] <= end]
                    if selected:
                        break
                    print(Fore.RED + "范围内无匹配项，请重新输入" + Style.RESET_ALL)
                except:
                    print(Fore.RED + "格式错误，请输入 起始行号-结束行号" + Style.RESET_ALL)
            else:  # 单个选择
                try:
                    line_num = int(choice)
                    selected = [m for m in matches if m[0] == line_num]
                    if selected:
                        break
                    print(Fore.RED + "无效的行号，请重新选择" + Style.RESET_ALL)
                except ValueError:
                    print(Fore.RED + "请输入有效行号或范围" + Style.RESET_ALL)
        
        # 询问用户是否要去重
        if len(selected) > 1:
            print_divider()
            dedup_choice = input(Fore.CYAN + Style.BRIGHT + ">>> 是否要去除重复名称的项？(y/n): " + Style.RESET_ALL)
            if dedup_choice.lower() == 'y':
                # 去重：保留每个名称的最后一个项
                unique_items = {}
                for m in selected:
                    name = m[2][2]
                    # 总是保存最新出现的项（行号更大的）
                    if name not in unique_items or m[0] > unique_items[name][0]:
                        unique_items[name] = (m[0], m[2][1], name)
                
                selected_items = [(item[1], item[2]) for item in unique_items.values()]
                print(Fore.GREEN + f"去重后剩余 {len(selected_items)} 项" + Style.RESET_ALL)
                return selected_items
            else:
                print(Fore.YELLOW + "保留所有重复项" + Style.RESET_ALL)
        
        # 返回所有选中的项（包括重复项）
        selected_items = []
        for m in selected:
            num = m[2][1]
            name = m[2][2]
            selected_items.append((num, name))
        return selected_items

def match_items_by_part(items1, items2):
    """根据部件关键字智能匹配物品 - 改进版"""
    # 创建部件映射字典
    part_map1 = {}
    for num, name in items1:
        key = extract_part_key(name)
        # 如果没有部件关键字，使用名称作为关键字
        if key is None:
            key = name
        part_map1.setdefault(key, []).append((num, name))
    
    part_map2 = {}
    for num, name in items2:
        key = extract_part_key(name)
        if key is None:
            key = name
        part_map2.setdefault(key, []).append((num, name))
    
    # 尝试匹配相同部件关键字的物品
        matched = []  # 修复了这里的缩进
    unmatched1 = []
    unmatched2 = []
    
    # 先匹配相同关键字的物品
    for key in set(part_map1.keys()) & set(part_map2.keys()):
        min_len = min(len(part_map1[key]), len(part_map2[key]))
        for i in range(min_len):
            matched.append((part_map1[key][i], part_map2[key][i]))
    
    # 收集未匹配项
    for key in part_map1:
        if key not in part_map2:
            unmatched1.extend(part_map1[key])
        else:
            unmatched1.extend(part_map1[key][min_len:])
    
    for key in part_map2:
        if key not in part_map1:
            unmatched2.extend(part_map2[key])
        else:
            unmatched2.extend(part_map2[key][min_len:])
    
    # 新增逻辑：分离无部件项
    no_part1 = []
    no_part2 = []
    
    # 检查匹配项中是否有无部件项
    new_matched = []
    for (num1, name1), (num2, name2) in matched:
        part1 = extract_part_key(name1)
        part2 = extract_part_key(name2)
        
        # 如果匹配对中有一个是无部件，移到无部件列表
        if part1 is None or part2 is None:
            if part1 is None:
                no_part1.append((num1, name1))
            if part2 is None:
                no_part2.append((num2, name2))
        else:
            new_matched.append(((num1, name1), (num2, name2)))
    
    # 检查未匹配项中是否有无部件项
    new_unmatched1 = []
    new_unmatched2 = []
    
    for item in unmatched1:
        num, name = item
        if extract_part_key(name) is None:
            no_part1.append(item)
        else:
            new_unmatched1.append(item)
    
    for item in unmatched2:
        num, name = item
        if extract_part_key(name) is None:
            no_part2.append(item)
        else:
            new_unmatched2.append(item)
    
    return new_matched, new_unmatched1, new_unmatched2, no_part1, no_part2

def manual_match(unmatched1, unmatched2):
    """手动匹配未匹配的项"""
    manual_matches = []
    
    while unmatched1 and unmatched2:
        print_header("手动匹配未匹配项")
        
        # 显示第一步未匹配项
        print_section("第一步未匹配项")
        for i, (num, name) in enumerate(unmatched1, 1):
            part_key = extract_part_key(name)
            part_display = part_key if part_key is not None else "无部件"
            print(f"{i}. {name} (部件:{part_display})")
        
        # 显示第二步未匹配项
        print_section("第二步未匹配项")
        for i, (num, name) in enumerate(unmatched2, 1):
            part_key = extract_part_key(name)
            part_display = part_key if part_key is not None else "无部件"
            print(f"{i}. {name} (部件:{part_display})")
        
        print_section("操作说明")
        print(Fore.YELLOW + "请选择要匹配的项 (格式: 第一步序号 第二步序号)" + Style.RESET_ALL)
        print(Fore.YELLOW + "例如: 1 3 表示匹配第一步的第1项和第二步的第3项" + Style.RESET_ALL)
        print(Fore.YELLOW + "输入 'q' 退出手动匹配" + Style.RESET_ALL)
        
        choice = input(Fore.CYAN + Style.BRIGHT + ">>> 请输入选择: " + Style.RESET_ALL)
        
        if choice.lower() == 'q':
            break
            
        try:
            idx1, idx2 = map(int, choice.split())
            if 1 <= idx1 <= len(unmatched1) and 1 <= idx2 <= len(unmatched2):
                item1 = unmatched1.pop(idx1-1)
                item2 = unmatched2.pop(idx2-1)
                manual_matches.append((item1, item2))
                print(Fore.GREEN + f"\n匹配成功: {item1[1]} -> {item2[1]}" + Style.RESET_ALL)
            else:
                print(Fore.RED + "序号超出范围，请重新输入" + Style.RESET_ALL)
        except:
            print(Fore.RED + "输入格式错误，请按格式输入" + Style.RESET_ALL)
        
        # 如果还有未匹配项，继续
        if unmatched1 and unmatched2:
            input(Fore.CYAN + Style.BRIGHT + "按回车继续手动匹配..." + Style.RESET_ALL)
    
    return manual_matches, unmatched1, unmatched2

def adjust_mismatched_items(items1, items2):
    """调整数量不匹配的项，允许用户选择舍弃哪一步的项"""
    
    while True:
        print_header("数量不匹配处理")
        print(Fore.RED + Style.BRIGHT + f"数量不匹配: 第一步选择了 {len(items1)} 项, 第二步选择了 {len(items2)} 项" + Style.RESET_ALL)
        
        # 显示第一步选择的项
        print_section("第一步选择的项")
        for i, (num, name) in enumerate(items1, 1):
            part_key = extract_part_key(name)
            part_display = part_key if part_key is not None else "无部件"
            print(f"{i}. {name} (部件:{part_display})")
        
        # 显示第二步选择的项
        print_section("第二步选择的项")
        for i, (num, name) in enumerate(items2, 1):
            part_key = extract_part_key(name)
            part_display = part_key if part_key is not None else "无部件"
            print(f"{i}. {name} (部件:{part_display})")
        
        # 询问用户操作
        print_section("操作选项")
        print("1. 智能匹配")
        print("2. 手动匹配")
        print("3. 调整第一步项")
        print("4. 调整第二步项")
        print("0. 放弃所有")
        step_choice = input(Fore.CYAN + Style.BRIGHT + ">>> 请选择操作: " + Style.RESET_ALL)
        
        if step_choice == '0':
            return None, None
            
        if step_choice == '1':
            # 智能匹配
            matched, unmatched1, unmatched2, no_part1, no_part2 = match_items_by_part(items1, items2)
            
            # 新增逻辑：处理无部件项
            if no_part1 or no_part2:
                print_header("发现无部件项")
                print(Fore.RED + "以下物品无法自动匹配，需要手动配置:" + Style.RESET_ALL)
                
                if no_part1:
                    print_section("第一步无部件项")
                    for i, (num, name) in enumerate(no_part1, 1):
                        print(f"{i}. {name}")
                
                if no_part2:
                    print_section("第二步无部件项")
                    for i, (num, name) in enumerate(no_part2, 1):
                        print(f"{i}. {name}")
                
                print_divider()
                input(Fore.CYAN + Style.BRIGHT + "按回车开始手动配置无部件项..." + Style.RESET_ALL)
                
                # 手动匹配无部件项
                manual_matches, remaining_no_part1, remaining_no_part2 = manual_match(no_part1, no_part2)
                
                # 将手动匹配成功的项添加到匹配列表中
                for item1, item2 in manual_matches:
                    matched.append((item1, item2))
                
                # 将未匹配的无部件项放回未匹配列表
                unmatched1.extend(remaining_no_part1)
                unmatched2.extend(remaining_no_part2)
            
            if matched:
                print_header("智能匹配结果")
                print_section("匹配成功项")
                for (num1, name1), (num2, name2) in matched:
                    part1 = extract_part_key(name1) or "无部件"
                    part2 = extract_part_key(name2) or "无部件"
                    print(f"{name1} (部件:{part1}) -> {name2} (部件:{part2})")
                
                if unmatched1 or unmatched2:
                    print_section("未匹配项")
                    if unmatched1:
                        print("第一步未匹配:")
                        for num, name in unmatched1:
                            part_display = extract_part_key(name) or "无部件"
                            print(f"  {name} (部件:{part_display})")
                    if unmatched2:
                        print("第二步未匹配:")
                        for num, name in unmatched2:
                            part_display = extract_part_key(name) or "无部件"
                            print(f"  {name} (部件:{part_display})")
                    
                    # 询问是否手动匹配未匹配项
                    manual_choice = input(Fore.CYAN + Style.BRIGHT + ">>> 是否手动匹配未匹配项？(y/n): " + Style.RESET_ALL)
                    if manual_choice.lower() == 'y':
                        manual_matches, unmatched1, unmatched2 = manual_match(unmatched1, unmatched2)
                        # 将手动匹配项添加到智能匹配结果中
                        matched.extend(manual_matches)
                
                # 询问用户是否接受匹配结果
                accept = input(Fore.CYAN + Style.BRIGHT + ">>> 是否接受此匹配结果？(y/n): " + Style.RESET_ALL)
                if accept.lower() == 'y':
                    # 提取匹配的项
                    items1_matched = [item1 for item1, _ in matched]
                    items2_matched = [item2 for _, item2 in matched]
                    return items1_matched, items2_matched
                else:
                    print(Fore.YELLOW + "匹配结果未应用" + Style.RESET_ALL)
                    continue
            else:
                print(Fore.RED + "智能匹配失败，没有找到对应部件" + Style.RESET_ALL)
                continue
            
        elif step_choice == '2':
            # 直接手动匹配所有项
            manual_matches, unmatched1, unmatched2 = manual_match(items1.copy(), items2.copy())
            
            if manual_matches:
                # 提取匹配的项
                items1_matched = [item1 for item1, _ in manual_matches]
                items2_matched = [item2 for _, item2 in manual_matches]
                return items1_matched, items2_matched
            else:
                print(Fore.RED + "未进行手动匹配" + Style.RESET_ALL)
                continue
            
        elif step_choice == '3':
            # 调整第一步项
            abandon_indexes = select_range(
                items1, 
                ">>> 选择要舍弃的第一步项 (格式: 1,3,5 或 1-3 或 a=全选, 0=不放弃): "
            )
            
            if abandon_indexes is not None:
                # 注意：abandon_indexes是从1开始的索引
                items1 = [item for i, item in enumerate(items1, 1) if i not in abandon_indexes]
                return items1, items2
            
        elif step_choice == '4':
            # 调整第二步项
            abandon_indexes = select_range(
                items2, 
                ">>> 选择要舍弃的第二步项 (格式: 1,3,5 或 1-3 或 a=全选, 0=不放弃): "
            )
            
            if abandon_indexes is not None:
                items2 = [item for i, item in enumerate(items2, 1) if i not in abandon_indexes]
                return items1, items2
            
        else:
            print(Fore.RED + "无效选择，请重新输入" + Style.RESET_ALL)

def save_configs(configs, save_path):
    """保存配置到文件，保留所有项（不去重）"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # 写入文件（追加模式）
        with open(save_path, 'a', encoding='utf-8') as f:
            for config in configs:
                f.write(f"[{config}],\n")
        
        print(Fore.GREEN + f"成功添加 {len(configs)} 条配置" + Style.RESET_ALL)
        return len(configs)
    except Exception as e:
        print(Fore.RED + f"保存配置失败: {e}" + Style.RESET_ALL)
        return 0

def main():
    save_dir = "/storage/emulated/0/幻穗制作区"
    save_path = os.path.join(save_dir, "幻穗配置.py")
    
    print_header("欢迎使用幻穗配置生成器")
    print(Fore.CYAN + "固定读取路径: /storage/emulated/0/幻穗制作区/经典.h" + Style.RESET_ALL)
    
    lines = read_h_file()
    if not lines:
        return
    
    while True:
        print_header("主菜单")
        print(Fore.MAGENTA + Style.BRIGHT + "当前数据条目: " + Fore.YELLOW + f"{len(lines)}" + Style.RESET_ALL)
        
        # 获取第一个物品范围
        print_section("第一步: 请输入要替换的物品")
        items1 = select_item(lines, "第一步")
        if not items1:
            break
            
        # 获取第二个物品范围
        print_header("第二步")
        print_section("第二步: 请输入替换后的物品")
        items2 = select_item(lines, "第二步")
        if not items2:
            break
                
        # 检查数量是否匹配
        if len(items1) != len(items2):
            adjusted = adjust_mismatched_items(items1, items2)
            if adjusted and adjusted[0] is None:
                print(Fore.YELLOW + "已放弃本次配置" + Style.RESET_ALL)
                input(Fore.CYAN + Style.BRIGHT + "按回车返回主菜单..." + Style.RESET_ALL)
                continue
            if adjusted:
                items1, items2 = adjusted
        else:
            # 如果数量匹配，尝试智能匹配
            # 修复这里：接收5个返回值
            matched, unmatched1, unmatched2, no_part1, no_part2 = match_items_by_part(items1, items2)
            
            # 处理无部件项
            if no_part1 or no_part2:
                print_header("发现无部件项")
                print(Fore.RED + "以下物品无法自动匹配，需要手动配置:" + Style.RESET_ALL)
                
                if no_part1:
                    print_section("第一步无部件项")
                    for i, (num, name) in enumerate(no_part1, 1):
                        print(f"{i}. {name}")
                
                if no_part2:
                    print_section("第二步无部件项")
                    for i, (num, name) in enumerate(no_part2, 1):
                        print(f"{i}. {name}")
                
                print_divider()
                input(Fore.CYAN + Style.BRIGHT + "按回车开始手动配置无部件项..." + Style.RESET_ALL)
                
                # 手动匹配无部件项
                manual_matches, remaining_no_part1, remaining_no_part2 = manual_match(no_part1, no_part2)
                
                # 将手动匹配成功的项添加到匹配列表中
                for item1, item2 in manual_matches:
                    matched.append((item1, item2))
                
                # 将未匹配的无部件项放回未匹配列表
                unmatched1.extend(remaining_no_part1)
                unmatched2.extend(remaining_no_part2)
            
            # 处理未匹配项
            if unmatched1 or unmatched2:
                print_header("未匹配项处理")
                print_section("未匹配项")
                if unmatched1:
                    print("第一步未匹配:")
                    for num, name in unmatched1:
                        part_display = extract_part_key(name) or "无部件"
                        print(f"  {name} (部件:{part_display})")
                if unmatched2:
                    print("第二步未匹配:")
                    for num, name in unmatched2:
                        part_display = extract_part_key(name) or "无部件"
                        print(f"  {name} (部件:{part_display})")
                
                manual_choice = input(Fore.CYAN + Style.BRIGHT + ">>> 是否手动匹配未匹配项？(y/n): " + Style.RESET_ALL)
                if manual_choice.lower() == 'y':
                    manual_matches, unmatched1, unmatched2 = manual_match(unmatched1, unmatched2)
                    matched.extend(manual_matches)
            
            # 更新items1和items2为匹配成功的项
            items1 = [item1 for item1, _ in matched]
            items2 = [item2 for _, item2 in matched]
        
        # 生成所有配置
        configs = []
        for (num1, name1), (num2, name2) in zip(items1, items2):
            config = f"{num1},{num2}],#{name1}={name2}"
            configs.append(config)
        
        # 保存到文件
        saved_count = save_configs(configs, save_path)
        
        print_header("配置已保存")
        print(Fore.GREEN + Style.BRIGHT + "√ 配置已保存: " + Style.RESET_ALL)
        print(Fore.CYAN + "文件路径: " + Fore.YELLOW + save_path)
        print(Fore.CYAN + f"生成 {len(configs)} 条配置" + Style.RESET_ALL)
        
        # 显示所有配置
        print_section("所有配置")
        for i, cfg in enumerate(configs, 1):
            print(f"{i}. {cfg}")
        
        print()
        input(Fore.CYAN + Style.BRIGHT + "按回车继续生成..." + Style.RESET_ALL)

if __name__ == "__main__":
    main()