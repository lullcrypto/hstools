import os
import re

def DEC_to_HEX(decimal_number):
    """将十进制数转换为8位十六进制字符串，并反转字节顺序"""
    hex_number = format(int(decimal_number), '08X')
    hex_array = [hex_number[i:i + 2] for i in range(0, len(hex_number), 2)]
    reversed_hex_array = hex_array[::-1]
    reversed_hex_number = ''.join(reversed_hex_array)
    print(f"{decimal_number}: 转换为 {reversed_hex_number}")
    return reversed_hex_number

def modify_file_hex(file_contents, A, B, fixed_hex, replacement_value):
    """在二进制数据中定位并替换品质相关的十六进制值"""
    search_seq1 = bytes.fromhex(A)
    search_seq2 = bytes.fromhex(B)
    fixed_hex_bytes = bytes.fromhex(fixed_hex)

    search_index1 = file_contents.find(search_seq1)
    search_index2 = file_contents.find(search_seq2)

    if search_index1 == -1 or search_index2 == -1:
        print("未找到指定的搜索序列。")
        return file_contents

    start_index1 = file_contents.find(fixed_hex_bytes, search_index1)
    if start_index1 == -1:
        print(f"未找到十六进制数 {fixed_hex}")
        return file_contents

    start_index2 = file_contents.find(fixed_hex_bytes, search_index2)
    if start_index2 == -1:
        print(f"未找到十六进制数 {fixed_hex}")
        return file_contents

    new_contents = bytearray(file_contents)
    new_contents[start_index1 - 8:start_index1] = bytes.fromhex(replacement_value)
    new_contents[start_index2 - 8:start_index2] = bytes.fromhex(replacement_value)

    return new_contents

def merge_files_in_folder(folder_path):
    """合并文件夹内所有文件的二进制内容"""
    merged_content = bytearray()
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            with open(file_path, "rb") as file:
                merged_content += file.read()
    return merged_content

def write_back_to_files(folder_path, modified_content, original_files):
    """将修改后的二进制内容按原文件拆分并写回"""
    offset = 0
    for filename in original_files:
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            with open(file_path, "rb") as file:
                file_size = len(file.read())
            with open(file_path, "wb") as file:
                file.write(modified_content[offset:offset + file_size])
            offset += file_size

def calculate_codes(input_hex):
    """根据输入的特征码计算定位用的十六进制值"""
    input_hex = input_hex.upper().zfill(4)
    big_endian_hex = input_hex[2:4] + input_hex[0:2]

    fixed_hex = hex(int(big_endian_hex, 16) + 8)[2:].upper().zfill(4)
    fixed_hex = fixed_hex[2:4] + fixed_hex[0:2]

    suffix_hex = hex(int(big_endian_hex, 16) - 0x0D)[2:].upper().zfill(4)
    suffix_hex = suffix_hex[2:4] + suffix_hex[0:2]

    backup_suffix_hex = hex(int(big_endian_hex, 16) + 1)[2:].upper().zfill(4)
    backup_suffix_hex = backup_suffix_hex[2:4] + backup_suffix_hex[0:2]

    return fixed_hex, suffix_hex, backup_suffix_hex

def main():
    """主函数：执行品质修改流程"""
    print("启用改品质功能")
    
    # 用户输入阶段
    folder_path = input("请输入小包文件夹路径: ")
    input_hex = input("请输入伪实体特征码: ")

    fixed_hex, suffix_hex, backup_suffix_hex = calculate_codes(input_hex)

    print("3")
    print("2")
    print("1")

    print("1衣服紫色2粉3红4橙5金6地铁品质金7橙8红9粉10紫11蓝12绿13白")
    replacement_choice = input("请输入修改的品质: ")
    array_file_path = input("请输入包含数组的文件路径: ")

    # 品质映射字典
    replacement_values = {
        '1': '0000000005000000',
        '2': '0000000006000000',
        '3': '0000000007000000',
        '4': '0000000008000000',
        '5': '0000000009000000',
        '6': '000000006C000000',
        '7': '000000006B000000',
        '8': '000000006A000000',
        '9': '0000000069000000',
        '10': '0000000068000000',
        '11': '0000000067000000',
        '12': '0000000066000000',
        '13': '0000000065000000'
    }

    # 验证用户输入
    if replacement_choice not in replacement_values:
        print("无效的替换值选项！")
        return

    replacement_value = replacement_values[replacement_choice]

    try:
        # 解析数组文件
        with open(array_file_path, 'r') as file:
            content = file.read()
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            array = []

            for line_num, line in enumerate(lines, 1):
                bracket_match = re.match(r'^\s*[  $$ $]\s*(\d+)\s*,\s*(\d+)\s*[$$ $]\s*$', line)
                if bracket_match:
                    num1, num2 = int(bracket_match.group(1)), int(bracket_match.group(2))
                    array.append((num1, num2))
                    continue

                nums = re.findall(r'\d+', line)
                if len(nums) == 2:
                    try:
                        num1, num2 = int(nums[0]), int(nums[1])
                        array.append((num1, num2))
                    except ValueError:
                        print(f"第{line_num}行：数字转换失败，内容：{line}")
                else:
                    print(f"第{line_num}行：格式错误，需包含两个数字，内容：{line}")

        # 执行文件修改
        original_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        merged_content = merge_files_in_folder(folder_path)

        for i in range(len(array)):
            A = DEC_to_HEX(array[i][0])
            B = DEC_to_HEX(array[i][1])
            merged_content = modify_file_hex(merged_content, A, B, fixed_hex, replacement_value)

        write_back_to_files(folder_path, merged_content, original_files)
        print("失格牛逼666")

    except Exception as e:
        print(f"操作出错: {e}")

if __name__ == "__main__":
    main()