import os
import re
import shutil
import tempfile
import hashlib
import zipfile
import datetime
import ast

def DEC_to_HEX(decimal_number):
    """将十进制数转换为8位十六进制数，并反转字节顺序"""
    try:
        decimal_int = int(decimal_number)
        hex_number = format(decimal_int, '08X')
        return ''.join([hex_number[i:i+2] for i in range(0, 8, 2)][::-1])
    except (ValueError, TypeError):
        print(f"错误: 无效的十进制数字 '{decimal_number}'")
        return None

def HEX_to_DEC(hex_number):
    """将反转后的十六进制数转换为十进制数"""
    try:
        hex_array = [hex_number[i:i+2] for i in range(0, 8, 2)]
        reversed_hex_str = ''.join(hex_array[::-1])
        return int(reversed_hex_str, 16)
    except (ValueError, TypeError, IndexError):
        return None

def calculate_md5(file_path):
    """计算文件的MD5哈希值"""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except IOError:
        print(f"无法读取文件: {file_path}")
        return None

def modify_file_hex(file_path, A, B):
    """修改文件中的十六进制序列"""
    if A is None or B is None:
        return False
    
    try:
        with open(file_path, "rb") as file:
            file_contents = file.read()
    except IOError:
        print(f"无法读取文件: {file_path}")
        return False
    
    search_seq1 = bytes.fromhex(A)
    search_seq2 = bytes.fromhex(B)
    
    # 定位序列A和B
    search_index1 = file_contents.rfind(search_seq1)
    search_index2 = file_contents.rfind(search_seq2)
    
    if search_index1 == -1 or search_index2 == -1:
        if search_index1 == -1:
            orig_value = HEX_to_DEC(A)
            print(f"未找到序列: {A} (原始值: {orig_value})")
        if search_index2 == -1:
            new_value = HEX_to_DEC(B)
            print(f"未找到序列: {B} (原始值: {new_value})")
        return False
    
    # 查找"FFFFFF"标记序列
    ff_seq = bytes.fromhex("FFFFFF")
    offset_before_search_seq = 63
    
    # 查找"FFFFFF"序列的位置
    offset_index1 = file_contents.rfind(ff_seq, 0, search_index1)
    offset_index2 = file_contents.rfind(ff_seq, 0, search_index2)
    
    if offset_index1 == -1 or offset_index2 == -1:
        print("未找到FFFFFF标记序列")
        return False
    
    # 计算修改位置
    replace_index1 = offset_index1 - offset_before_search_seq
    replace_index2 = offset_index2 - offset_before_search_seq
    
    # 执行字节交换
    new_contents = bytearray(file_contents)
    value1 = new_contents[replace_index1:replace_index1+2]
    value2 = new_contents[replace_index2:replace_index2+2]
    
    new_contents[replace_index2:replace_index2+2] = value1
    new_contents[replace_index1:replace_index1+2] = value2
    
    # 保存修改
    try:
        with open(file_path, "wb") as file:
            file.write(new_contents)
    except IOError:
        print(f"无法写入文件: {file_path}")
        return False
    
    orig_dec = HEX_to_DEC(A) or A
    new_dec = HEX_to_DEC(B) or B
    print(f"成功交换: {A} ↔ {B} (原始值: {orig_dec} ↔ {new_dec})")
    return True

def merge_uexp_files(folder_path, output_file):
    """合并文件夹中的所有uexp文件"""
    uexp_files = []
    file_sizes = []
    
    # 收集uexp文件信息
    for filename in sorted(os.listdir(folder_path)):
        if filename.lower().endswith('.uexp') and not filename.startswith('.'):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                uexp_files.append((filename, file_path))
    
    if not uexp_files:
        print("警告: 未找到任何uexp文件!")
        return None
    
    # 合并文件
    total_size = 0
    try:
        with open(output_file, 'wb') as out_file:
            for filename, file_path in uexp_files:
                file_size = os.path.getsize(file_path)
                file_sizes.append((filename, file_size))
                total_size += file_size
                
                with open(file_path, 'rb') as in_file:
                    shutil.copyfileobj(in_file, out_file)
    except IOError:
        print("文件合并操作失败")
        return None
    
    print(f"已合并 {len(uexp_files)} 个uexp文件到临时文件")
    return file_sizes

def split_uexp_files(input_file, file_sizes, folder_path):
    """将临时文件拆分为原始uexp文件"""
    if not os.path.exists(input_file):
        print(f"错误: 输入文件不存在 {input_file}")
        return False
    
    total_size = sum(size for _, size in file_sizes)
    actual_size = os.path.getsize(input_file)
    
    if total_size != actual_size:
        print(f"警告: 文件大小不匹配! 预期: {total_size}, 实际: {actual_size}")
    
    try:
        with open(input_file, 'rb') as in_file:
            for filename, size in file_sizes:
                output_path = os.path.join(folder_path, filename)
                
                try:
                    with open(output_path, 'wb') as out_file:
                        out_file.write(in_file.read(size))
                except IOError:
                    print(f"无法写入文件: {output_path}")
                    return False
    except IOError:
        print("文件拆分操作失败")
        return False
    
    return True

def extract_code_list(config_file):
    """从配置文件中提取修改指令"""
    if not os.path.isfile(config_file):
        print(f"错误: 配置文件不存在 {config_file}")
        return None
    
    try:
        with open(config_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 方法1: 尝试解析整个文件为Python模块
        try:
            # 尝试解析文件内容中的数组定义
            pattern = r'array\s*=\s*\[.*?\]'
            match = re.search(pattern, content, re.DOTALL)
            if match:
                array_content = match.group(0)
                # 执行安全解析
                parsed = ast.literal_eval(array_content.split('=', 1)[1].strip())
                if isinstance(parsed, list):
                    code_list = []
                    for item in parsed:
                        if isinstance(item, list) and len(item) == 2:
                            try:
                                code_list.append((int(item[0]), int(item[1])))
                            except (ValueError, TypeError):
                                print(f"忽略无效值对: {item}")
                    
                    if code_list:
                        print(f"方法1: 从配置文件中解析 {len(code_list)} 条修改指令")
                        return code_list
        except (SyntaxError, ValueError, TypeError) as e:
            pass
        
        # 方法2: 替代方法解析
        code_list = []
        pattern = r'\[\s*(\d+)\s*,\s*(\d+)\s*\]'
        matches = re.findall(pattern, content)
        
        for original, new in matches:
            try:
                code_list.append((int(original), int(new)))
            except (ValueError, TypeError):
                print(f"忽略无效值对: [{original}, {new}]")
        
        if code_list:
            print(f"方法2: 从配置文件中解析 {len(code_list)} 条修改指令")
            return code_list
        
        print("错误: 在配置文件中未找到有效的修改指令")
        return None
        
    except UnicodeDecodeError:
        print("错误: 配置文件编码不兼容 (请使用UTF-8编码)")
        return None
    except Exception as e:
        print(f"读取配置文件时发生未知错误: {str(e)}")
        return None

def get_modified_files(original_hashes, folder_path):
    """获取被修改的文件列表"""
    modified_files = []
    for filename, original_hash in original_hashes.items():
        file_path = os.path.join(folder_path, filename)
        current_hash = calculate_md5(file_path)
        if current_hash != original_hash:
            modified_files.append(filename)
    return modified_files

def create_zip_file(modified_files, output_folder, source_folder):
    """创建修改文件的压缩包"""
    # 确保输出目录存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # 创建时间戳
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"modified_uexp_{timestamp}.zip"
    zip_path = os.path.join(output_folder, zip_filename)
    
    # 创建ZIP文件
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename in modified_files:
                file_path = os.path.join(source_folder, filename)
                if os.path.exists(file_path):
                    arcname = os.path.join("uexp_files", filename)
                    zipf.write(file_path, arcname=arcname)
        return zip_path
    except Exception as e:
        print(f"创建压缩文件时出错: {str(e)}")
        return None

def main():
    print("=" * 50)
    print("UE Asset UEXP 文件批量修改工具 (高级版)")
    print("=" * 50) 
    # 固定路径
    uexp_folder = "/storage/emulated/0/幻穗制作区/uexp打包/"
    output_folder = "/storage/emulated/0/幻穗制作区/幻穗自动美化存放区/"
    
    # 用户输入配置文件路径
    config_file = input("\n请输入配置文件路径: ").strip()
    
    # 提取修改指令
    code_list = extract_code_list(config_file)
    if not code_list:
        print("未找到有效的修改指令，程序终止")
        return
    
    # 显示提取的修改指令
    print("\n修改指令列表:")
    for i, (original, new) in enumerate(code_list, 1):
        print(f"{i}. [{original}] → [{new}]")
    
    # 记录每个文件的原始哈希值
    print("\n正在收集文件原始哈希值...")
    original_hashes = {}
    for filename in os.listdir(uexp_folder):
        if filename.lower().endswith('.uexp') and not filename.startswith('.'):
            file_path = os.path.join(uexp_folder, filename)
            file_hash = calculate_md5(file_path)
            original_hashes[filename] = file_hash
            print(f"{filename}: {file_hash}")
    
    if not original_hashes:
        print("未找到任何uexp文件，程序终止")
        return
    
    # 创建临时文件
    temp_path = tempfile.mktemp(suffix='.uexptmp')
    print(f"\n创建临时文件: {temp_path}")
    
    try:
        # 1. 合并所有uexp文件
        print("\n[步骤1] 合并uexp文件...")
        file_sizes = merge_uexp_files(uexp_folder, temp_path)
        if not file_sizes:
            print("错误: 文件合并失败，程序终止")
            return
        
        # 2. 应用所有修改指令
        print("\n[步骤2] 应用修改指令...")
        for original, new in code_list:
            hex_original = DEC_to_HEX(original)
            hex_new = DEC_to_HEX(new)
            
            if hex_original and hex_new:
                print(f"\n正在处理: {original} → {new}")
                if modify_file_hex(temp_path, hex_original, hex_new):
                    print("修改成功")
                else:
                    print("修改失败，请检查日志")
            else:
                print(f"跳过无效的修改指令: {original} → {new}")
        
        # 3. 拆分为原始文件
        print("\n[步骤3] 拆分文件到原始位置...")
        if not split_uexp_files(temp_path, file_sizes, uexp_folder):
            print("错误: 文件拆分失败")
            return        
        # 4. 检测修改的文件
        print("\n[步骤4] 检测被修改的文件...")
        modified_files = get_modified_files(original_hashes, uexp_folder)
        
        if not modified_files:
            print("\n没有文件被修改")
            return
        
        print("\n修改过的文件:")
        for filename in modified_files:
            print(f"- {filename}")
        
        # 5. 创建修改文件的压缩包
        print("\n[步骤5] 创建压缩文件包...")
        zip_path = create_zip_file(modified_files, output_folder, uexp_folder)
        
        if zip_path:
            print(f"\n成功创建压缩包: {zip_path}")
        else:
            print("\n压缩包创建失败")
        
        print("\n所有文件处理完成!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n处理过程中发生错误: {str(e)}")
    finally:
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"已清理临时文件: {temp_path}")
    
    print("\n程序结束。感谢使用!")

if __name__ == "__main__":
    main()

