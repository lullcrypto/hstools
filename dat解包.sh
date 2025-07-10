#!/bin/bash
# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
NC='\033[0m' # 无颜色

# 创建必要目录
base_dir="/storage/emulated/0/幻穗制作区"
echo -e "${YELLOW}正在创建工作区...${NC}"
mkdir -p "$base_dir"
mkdir -p "$base_dir/dat解包"
echo -e "${GREEN}工作区创建完成: $base_dir${NC}"

# 主解包功能
echo -e "${YELLOW}╔══════════════════════════════╗${NC}"
echo -e "${YELLOW}│        DAT解包工具           │${NC}"
echo -e "${YELLOW}╚══════════════════════════════╝${NC}"

echo -e "${BLUE}请选择要解包的PAK文件：${NC}"
select file in $(find /storage/emulated/0/幻穗制作区/pak -name "*.pak"); do
    if [[ $REPLY -eq 0 ]]; then
        echo -e "${GREEN}操作已取消${NC}"
        exit 0
    elif [[ -n "$file" ]]; then
        echo -e "${YELLOW}正在解包: $(basename "$file")${NC}"
        
        # 执行解包操作
        if qemu-i386 HS/quickbms HS/解包.bms "$file" "$base_dir/dat解包"; then
            echo -e "${GREEN}解包成功！文件保存在: $base_dir/dat解包${NC}"
        else
            echo -e "${RED}解包失败！请检查文件路径和权限${NC}"
        fi
        exit 0
    else
        echo -e "${RED}无效选择，请重新输入${NC}"
    fi
done
