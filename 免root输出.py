import re
import os
import sys
import mmap
from collections import OrderedDict
from tqdm import tqdm

# 配置文件类型特征码和偏移量
FILE_CONFIG = {
    "载具": {
        "signature": b'\x0B\x27\x06\x00',
        "start_offset": 21,
        "end_offset": 65
    },
    "称号": {
        "signature": b'\x25\x57\x2F\x00',
        "start_offset": 271,
        "end_offset": 295
    },
    "地铁": {
        "signature": bytes.fromhex("E483803A"),
        "start_offset": 161,
        "end_offset": 191
    },
    "头像框": {
        "signature": bytes.fromhex("518C1E00"),
        "start_offset": -59,
        "end_offset": -11
    },
    "伪实体特殊": {
        "signature": b'\x9D\xA4\x95\x00',
        "start_offset": 21,
        "end_offset": 65,
        "validation": b'\x0B\x27\x06\x00'
    }
}

# 需要删除的特殊字符
SPECIAL_CHARS_TO_DELETE = [' ', '娀', '樀', '攀', '豰', '豣', '搀', '漀', "戀"]

# 优化的正则表达式，保留更多常见符号
TEXT_FILTER_REGEX = re.compile(
    r'[^\u4e00-\u9fa5'      # 中文
    r'a-zA-Z0-9'             # 字母和数字
    r'\u00A0-\u00FF'         # 拉丁字母补充
    r'\u2000-\u206F'         # 常用标点
    r'\u3000-\u303F'         # CJK标点
    r'\uFF00-\uFFEF'         # 全角符号
    r'()\[\]{}<>%$#@&*_+=/\.,;:!?^|~-]'  # 其他符号
)

def detect_file_type(data):
    """智能检测文件类型，带优先级和验证"""
    # 优先检测伪实体特殊类型
    if FILE_CONFIG["伪实体特殊"]["signature"] in data:
        if FILE_CONFIG["伪实体特殊"].get("validation") and FILE_CONFIG["伪实体特殊"]["validation"] in data:
            return "伪实体"
        return "伪实体特殊"
    
    # 检测其他类型
    for file_type, config in FILE_CONFIG.items():
        if file_type == "伪实体特殊":
            continue
        if config["signature"] in data:
            return file_type
    
    return None

def find_safe_substring(data, start, end):
    """安全提取子字符串，处理边界情况"""
    length = len(data)
    safe_start = max(0, min(start, length))
    safe_end = max(0, min(end, length))
    if safe_start >= safe_end:
        return b''
    return data[safe_start:safe_end]

def extract_and_decode(data, file_type, feature_codes, output_file):
    """核心提取和解码逻辑"""
    feature_code_1_bytes, feature_code_2_bytes, feature_code_3_bytes = feature_codes
    
    # 获取文件类型的配置
    config = FILE_CONFIG.get(file_type, {})
    if not config:
        print(f"⚠️ 未找到 {file_type} 类型的配置")
        return 0
    
    index = 0
    data_length = len(data)
    extracted_count = 0
    
    # 创建进度条
    with tqdm(total=data_length, desc="解析进度", unit="B", unit_scale=True) as pbar:
        while index < data_length:
            # 查找第一个特征码
            index = data.find(feature_code_1_bytes, index)
            if index == -1:
                break
            
            index += 6
            pbar.update(index - pbar.n)
            
            # 查找第二个特征码
            index_0400 = data.find(feature_code_2_bytes, index)
            if index_0400 == -1:
                index += 1
                continue
            
            # 检查偏移距离是否合理
            if index_0400 - index > 100:  # 放宽偏移限制
                index = index_0400
                continue
            
            # 查找第三个特征码
            index_67f5 = data.find(feature_code_3_bytes, index_0400)
            if index_67f5 == -1:
                index = index_0400 + 1
                continue
            
            # 提取数值数据
            extract_start_index = index_67f5 - 4
            if extract_start_index < 0:
                break
                
            extracted_data = find_safe_substring(data, extract_start_index, index_67f5)
            if len(extracted_data) < 4:
                index = index_67f5 + 1
                continue
                
            try:
                little_endian_int = int.from_bytes(extracted_data, byteorder='little', signed=False)
            except Exception:
                index = index_67f5 + 1
                continue
            
            # 计算文本提取位置
            start_pos = extract_start_index + config["start_offset"]
            end_pos = index_67f5 + config["end_offset"]
            
            # 处理负偏移
            if config["start_offset"] < 0:
                start_pos = max(0, extract_start_index + config["start_offset"])
            if config["end_offset"] < 0:
                end_pos = max(0, index_67f5 + config["end_offset"])
            
            # 提取文本数据
            text_data = find_safe_substring(data, start_pos, end_pos)
            
            # 文本解码和处理
            decoded_text = ""
            try:
                # 尝试UTF-16LE解码
                decoded_text = text_data.decode('utf-16le', errors='ignore')
                
                # 删除特殊字符
                for char in SPECIAL_CHARS_TO_DELETE:
                    decoded_text = decoded_text.replace(char, '')
                
                # 应用优化的正则过滤
                decoded_text = TEXT_FILTER_REGEX.sub('', decoded_text)
                
                # 清理多余空格
                decoded_text = re.sub(r'\s{2,}', ' ', decoded_text).strip()
                
                # 如果文本为空则跳过
                if not decoded_text.strip():
                    decoded_text = "[空文本]"
                    
            except Exception as e:
                decoded_text = f"[解码错误: {str(e)}]"
            
            # 写入输出文件
            output_file.write(f"{little_endian_int}--{little_endian_int * 100}--[{decoded_text}]\n")
            extracted_count += 1
            
            index = index_67f5 + 1
            pbar.update(index - pbar.n)
    
    return extracted_count

def extract_hex_data_and_decode(input_file, output_file):
    """主处理函数"""
    try:
        # 检查文件大小
        file_size = os.path.getsize(input_file)
        if file_size > 100 * 1024 * 1024:  # 100MB
            print(f"⚠️ 警告: 文件较大 ({file_size/1024/1024:.2f}MB), 处理可能需要时间...")
        
        # 读取文件内容 - 使用大文件优化方式
        with open(input_file, 'rb') as infile:
            # 对于小文件直接读取内存
            if file_size < 10 * 1024 * 1024:  # 小于10MB
                data = infile.read()
            else:
                # 使用内存映射处理大文件
                with mmap.mmap(infile.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    data = mm.read()
        
        # 检测文件类型
        file_type = detect_file_type(data)
        if file_type is None:
            print("❌ 无法识别的文件类型")
            return False
        
        # 伪实体特殊处理
        if file_type == "伪实体特殊":
            if b'\x0B\x27\x06\x00' not in data:
                print("❌ 这不是有效的伪实体dat文件")
                return False
            file_type = "伪实体"
            print("✅ 检测到有效的伪实体文件")
        
        print(f"🔍 识别文件类型: {file_type}")
        
        # 定位特征码
        config = FILE_CONFIG.get(file_type, FILE_CONFIG["载具"])
        fixed_hex = config["signature"]
        fixed_hex_index = data.find(fixed_hex)
        
        if fixed_hex_index == -1:
            print(f"❌ 这不是有效的{file_type}文件，特征码缺失")
            return False
        
        # 提取三个特征码（增加边界检查）
        feature_code_3_bytes = find_safe_substring(data, fixed_hex_index + 4, fixed_hex_index + 6)
        feature_code_2_bytes = find_safe_substring(data, fixed_hex_index - 9, fixed_hex_index - 7)
        feature_code_1_bytes = find_safe_substring(data, fixed_hex_index - 17, fixed_hex_index - 15)
        
        # 验证特征码长度
        if len(feature_code_1_bytes) < 2 or len(feature_code_2_bytes) < 2 or len(feature_code_3_bytes) < 2:
            print("⚠️ 警告: 特征码提取不完整，尝试使用备用特征码...")
            # 备用特征码策略（根据文件类型调整）
            if file_type == "头像框":
                feature_code_1_bytes = b'\xAA\xBB'  # 示例备用值
            else:
                feature_code_1_bytes = b'\xCC\xDD'  # 通用备用值
        
        print("\n" + "="*80)
        print(f"自动识别特征码:")
        print(f"  第一个特征码: {feature_code_1_bytes.hex().upper()}")
        print(f"  第二个特征码: {feature_code_2_bytes.hex().upper()}")
        print(f"  第三个特征码: {feature_code_3_bytes.hex().upper()}")
        print("="*80 + "\n")
        
        # 处理输出文件
        with open(output_file, 'w', encoding='utf-8') as outfile:
            extracted_count = extract_and_decode(
                data, 
                file_type,
                (feature_code_1_bytes, feature_code_2_bytes, feature_code_3_bytes),
                outfile
            )
        
        print("\n" + "="*80)
        if extracted_count > 0:
            print(f"✅ 输出完成! 共提取 {extracted_count} 条记录")
            print(f"✅ 结果已保存到: {output_file}")
            return True
        else:
            print("❌ 未提取到任何有效记录，可能原因:")
            print("   - 文件类型不匹配")
            print("   - 游戏版本更新导致格式变化")
            print("   - 文件已损坏")
            return False
        
    except FileNotFoundError:
        print(f"❌ 文件未找到: {input_file}")
    except PermissionError:
        print(f"❌ 权限不足，无法访问文件: {input_file}")
    except Exception as e:
        print(f"❌ 发生未预期错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return False

def main():
    """命令行交互界面"""
    print("="*80)
    print("和平精英 DAT 文件解析工具 v2.1")
    print("专用于PAK解包的.dat文件文本提取")
    print("="*80)
    
    # 支持拖拽文件
    input_file = input("请输入dat文件路径(或拖拽文件到这里): ").strip('"').strip()
    
    if not input_file:
        print("❌ 未提供输入文件路径")
        return
    
    # 检查文件是否存在
    if not os.path.exists(input_file):
        print(f"❌ 文件不存在: {input_file}")
        return
    
    # 自动生成输出路径
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = f"{base_name}_extracted.txt"
    print(f"⚙️ 将自动输出到: {output_file}")
    
    # 确认操作
    confirm = input(f"是否开始处理? (Y/n): ").strip()
    if confirm.lower() in ('', 'y', 'yes'):
        print("⏳ 开始处理，请稍候...")
        success = extract_hex_data_and_decode(input_file, output_file)
        
        if success and os.path.exists(output_file):
            print("✅ 处理完成!")
            # 尝试打开输出文件
            if sys.platform == 'win32':
                try:
                    os.startfile(os.path.dirname(os.path.abspath(output_file)))
                except:
                    pass
            elif sys.platform == 'darwin':  # macOS
                try:
                    import subprocess
                    subprocess.call(['open', os.path.dirname(os.path.abspath(output_file))])
                except:
                    pass
            else:  # Linux/Android
                try:
                    import subprocess
                    subprocess.call(['xdg-open', os.path.dirname(os.path.abspath(output_file))])
                except:
                    pass
    else:
        print("🚫 操作已取消")

if __name__ == "__main__":
    main()