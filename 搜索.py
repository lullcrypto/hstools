import os

def search_hex_in_file(file_path, hex_pattern):
    # 将十六进制字符串转换为字节序列
    try:
        pattern_bytes = bytes.fromhex(hex_pattern)
    except ValueError:
        print("错误：提供的十六进制格式无效")
        return
    
    print(f"搜索模式: {hex_pattern} (长度: {len(pattern_bytes)} 字节)")
    
    if not os.path.exists(file_path):
        print(f"错误：文件 '{file_path}' 不存在")
        return
    
    try:
        with open(file_path, 'rb') as file:
            file_content = file.read()
            
            # 在文件中搜索字节序列
            offset = file_content.find(pattern_bytes)
            
            if offset != -1:
                print(f"✅ 找到匹配项！位置: 0x{offset:08X} (字节偏移 {offset})")
            else:
                print("❌ 未找到匹配项")
                
    except Exception as e:
        print(f"处理文件时出错: {str(e)}")

if __name__ == "__main__":
    # 要搜索的固定十六进制序列
    hex_pattern = "F3810A5CD191999F16595759"
    
    # 获取用户输入的文件路径
    file_path = input("请输入.dat文件路径: ").strip()
    
    # 执行搜索
    search_hex_in_file(file_path, hex_pattern)