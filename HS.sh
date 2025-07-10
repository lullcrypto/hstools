#!/bin/bash
# 微验网络验证部分保持不变
echo -e "\n欢迎使用微验网络验证\n微验官网：llua.cn\n加载中...\n"

# 按照您的要求，将路径放在/storage/emulated/0/幻穗制作区
TMP_DIR="/storage/emulated/0/幻穗制作区/hstool"

# 确保临时目录存在
echo "创建目录: $TMP_DIR"
mkdir -p "$TMP_DIR" || {
    echo "错误：无法创建目录 $TMP_DIR，请确保Termux有存储权限"
    echo "请运行: termux-setup-storage 并允许存储访问"
    exit 1
}

# 检查并下载rc4工具
if ! [ -e "$TMP_DIR/rc4" ]; then
    echo "下载 rc4 工具到 $TMP_DIR..."
    download_url="https://raw.githubusercontent.com/lullcrypto/hstools/main/rc4"
    
    # 使用curl或wget下载
    if command -v curl &> /dev/null; then
        curl -sL "$download_url" -o "$TMP_DIR/rc4" || {
            echo "错误：curl下载失败"
            exit 1
        }
    elif command -v wget &> /dev/null; then
        wget -q "$download_url" -O "$TMP_DIR/rc4" || {
            echo "错误：wget下载失败"
            exit 1
        }
    else
        echo "错误：没有找到curl或wget，请安装其中一个"
        exit 1
    fi
    
    # 检查下载是否成功
    if [ ! -f "$TMP_DIR/rc4" ]; then
        echo "错误：无法下载rc4工具，请检查网络连接"
        echo "备用方案：请手动下载rc4并放在 $TMP_DIR/"
        echo "下载链接: $download_url"
        exit 1
    fi
    
    # 添加执行权限
    chmod +x "$TMP_DIR/rc4" || {
        echo "错误：无法设置执行权限"
        exit 1
    }
    echo "rc4工具已下载并设置权限"
fi

# 配置区
wfb5cfb05da0f55843e5dbd28554a92e1_wyUrl="http://wy.llua.cn/api/" 
wfb5cfb05da0f55843e5dbd28554a92e1_wyAppid="27025"
wfb5cfb05da0f55843e5dbd28554a92e1_wyAppkey="0XmTQutIhmtSF5L"
wfb5cfb05da0f55843e5dbd28554a92e1_wyRc4key="51800d31466e15c0b077fc64ee0504a0"

# 函数区
parse_json() {
  json=$1
  query=$2
  value=$(echo "$json" | grep -o "\"$query\":[^ }]*" | sed 's/"[^"]*":\([^,}]*\).*/\1/' | head -n 1)
  value="${value#\"}"
  value="${value%\"}"
  echo "$value"
}

# 公告区 - 使用rc4
echo "获取系统公告..."
notice=$(curl -s "${wfb5cfb05da0f55843e5dbd28554a92e1_wyUrl}?id=notice&app=${wfb5cfb05da0f55843e5dbd28554a92e1_wyAppid}")
deNotice=$("$TMP_DIR/rc4" "$notice" "$wfb5cfb05da0f55843e5dbd28554a92e1_wyRc4key" "de")
Notices=$(parse_json "$deNotice" "app_gg")
echo -e "系统公告:\n${Notices}\n"

# 验证区 - 使用rc4
echo "请输入卡密："
read kami
timer=$(date +%s)
android_id=$(settings get secure android_id)
fingerprint=$(getprop ro.build.fingerprint)
imei=$(echo -n "${android_id}.${fingerprint}" | md5sum | awk '{print $1}')
value="$RANDOM${timer}"
sign=$(echo -n "kami=${kami}&markcode=${imei}&t=${timer}&${wfb5cfb05da0f55843e5dbd28554a92e1_wyAppkey}" | md5sum | awk '{print $1}')
data=$("$TMP_DIR/rc4" "kami=${kami}&markcode=${imei}&t=${timer}&sign=${sign}&value=${value}&${wfb5cfb05da0f55843e5dbd28554a92e1_wyAppkey}" "$wfb5cfb05da0f55843e5dbd28554a92e1_wyRc4key" "en")
logon=$(curl -s "${wfb5cfb05da0f55843e5dbd28554a92e1_wyUrl}?id=kmlogin&app=${wfb5cfb05da0f55843e5dbd28554a92e1_wyAppid}&data=${data}")
deLogon=$("$TMP_DIR/rc4" "$logon" "$wfb5cfb05da0f55843e5dbd28554a92e1_wyRc4key" "de")
wfb5cfb05da0f55843e5dbd28554a92e1_wy_Code=$(parse_json "$deLogon" "w5d07995fdb2bec61115db96b0ce4ca60")

# 检查验证码
if [ -n "$wfb5cfb05da0f55843e5dbd28554a92e1_wy_Code" ] && [ "$wfb5cfb05da0f55843e5dbd28554a92e1_wy_Code" -eq 20683 ]; then
    kamid=$(parse_json "$deLogon" "s62a623d09194343be26a248765f08e5d")
    timec=$(parse_json "$deLogon" "i7c24630fc3c306390b8e7982a913da12")
    check=$(echo -n  "${timec}${wfb5cfb05da0f55843e5dbd28554a92e1_wyAppkey}${value}20683${kamid}${sign}" | md5sum | awk '{print $1}')
    checks=$(parse_json "$deLogon" "tf641c34cebe5ace4585236ad3457a425")
    if [ "$check" == "$checks" ]; then
        vip=$(parse_json "$deLogon" "r1d6d67aea92b2fbd5174d82cff89140e")
        if [ -n "$vip" ]; then
            # 日期转换兼容不同系统
            if date --version >/dev/null 2>&1; then
                vips=$(date -d "@$vip" +"%Y-%m-%d %H:%M:%S")
            else
                vips=$(date -r "$vip" +"%Y-%m-%d %H:%M:%S")
            fi
            clear
            echo "登录成功，到期时间：${vips}"
        else
            echo "登录成功，但无法获取到期时间"
        fi
    else
        echo "校验失败"
        exit 1
    fi
else
    error_msg=$(parse_json "$deLogon" "vf8c449deeaa257c7bddfdfa8d67dadf8")
    echo "验证失败: ${error_msg}"
    exit 1
fi

echo "验证成功后程序开始执行..."

# ... 以下部分保持不变 ...


#!/bin/bash
# HSTOOL - 幻穗多功能工具
# 作者：幻穗
# 快手号：Luisner866x
# TG：HSMH886L

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
MAGENTA='\033[1;35m'
LIGHT_BLUE='\033[1;34m'
LIGHT_CYAN='\033[1;36m'
NC='\033[0m'  # 重置颜色

# 边框颜色函数 - 创建渐变效果
border_color() {
    colors=("$LIGHT_BLUE" "$LIGHT_CYAN" "$CYAN" "$BLUE")
    local index=$((RANDOM % 4))
    echo -e "${colors[$index]}"
}

# 首次运行设置
first_run() {
    echo -e "$(border_color)╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "$(border_color)║${YELLOW}                     首次运行设置中...                      ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)╚══════════════════════════════════════════════════════════════════╝${NC}"
    
    # 授予当前目录权限
    echo -e "${CYAN}▶ 设置目录权限...${NC}"
    chmod -R 777 "$(dirname "$0")"/*
    sleep 0.5
    
    # 创建所有需要的目录
    echo -e "${CYAN}▶ 创建目录结构...${NC}"
    base_dirs=(
        "/storage/emulated/0/幻穗制作区"
        "/storage/emulated/0/幻穗制作区/pak"
        "/storage/emulated/0/幻穗制作区/dat打包"
        "/storage/emulated/0/幻穗制作区/dat解包"
        "/storage/emulated/0/幻穗制作区/uexp打包"
        "/storage/emulated/0/幻穗制作区/uexp解包"
        "/storage/emulated/0/幻穗制作区/地铁写配置"
        "/storage/emulated/0/幻穗制作区/幻穗dat数据存放区"
        "/storage/emulated/0/幻穗制作区/幻穗dat提取结果"
        "/storage/emulated/0/幻穗制作区/幻穗写配料表"
        "/storage/emulated/0/幻穗制作区/幻穗写配置"
        "/storage/emulated/0/幻穗制作区/自动提取dat"
        "/storage/emulated/0/幻穗制作区/自动提取dat/称号dat"
        "/storage/emulated/0/幻穗制作区/自动提取dat/大厅动作dat"
        "/storage/emulated/0/幻穗制作区/自动提取dat/地铁dat"
        "/storage/emulated/0/幻穗制作区/自动提取dat/普通美化dat"
        "/storage/emulated/0/幻穗制作区/自动提取dat/淘汰播报dat"
        "/storage/emulated/0/幻穗制作区/自动提取dat/头像框dat"
        "/storage/emulated/0/幻穗制作区/自动提取dat/伪实体dat"
    )
    
    for dir in "${base_dirs[@]}"; do
        mkdir -p "$dir"
        echo -e "  ${GREEN}✓${NC} 创建目录: $dir"
        sleep 0.1
    done
    
    echo -e "${GREEN}✔ 首次运行设置完成！${NC}"
    touch "/storage/emulated/0/幻穗制作区/.first_run_complete"
    sleep 2
}
# 显示欢迎界面
welcome_screen() {
    clear
    echo -e "$(border_color)╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "$(border_color)║${NC}                                                              $(border_color)║${NC}"
    echo -e "$(border_color)║${YELLOW}    ██╗  ██╗███████╗${WHITE}████████╗ ██████╗  ██████╗ ██╗         ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)║${YELLOW}    ██║  ██║██╔════╝${WHITE}╚══██╔══╝██╔═══██╗██╔═══██╗██║         ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)║${YELLOW}    ███████║███████╗${WHITE}   ██║   ██║   ██║██║   ██║██║         ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)║${YELLOW}    ██╔══██║╚════██║${WHITE}   ██║   ██║   ██║██║   ██║██║         ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)║${YELLOW}    ██║  ██║███████║${WHITE}   ██║   ╚██████╔╝╚██████╔╝███████╗    ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)║${YELLOW}    ╚═╝  ╚═╝╚══════╝${WHITE}   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝    ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)║${NC}                                                              $(border_color)║${NC}"
    echo -e "$(border_color)╠══════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "$(border_color)║${CYAN}                   HSTOOL 多功能工具箱 v1.0                  ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)╚══════════════════════════════════════════════════════════════════╝${NC}"
    sleep 1
}

# 主菜单函数
main_menu() {
    clear
    
    # 显示Logo和头部信息
    echo -e "$(border_color)╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "$(border_color)║${YELLOW}    ██╗  ██╗███████╗${WHITE}████████╗ ██████╗  ██████╗ ██╗         ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)║${YELLOW}    ██║  ██║██╔════╝${WHITE}╚══██╔══╝██╔═══██╗██╔═══██╗██║         ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)║${YELLOW}    ███████║███████╗${WHITE}   ██║   ██║   ██║██║   ██║██║         ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)║${YELLOW}    ██╔══██║╚════██║${WHITE}   ██║   ██║   ██║██║   ██║██║         ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)║${YELLOW}    ██║  ██║███████║${WHITE}   ██║   ╚██████╔╝╚██████╔╝███████╗    ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)║${YELLOW}    ╚═╝  ╚═╝╚══════╝${WHITE}   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝    ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)╠══════════════════════════════════════════════════════════════════╣${NC}"
    
    # 显示当前时间和作者信息
    current_time=$(date +"%Y-%m-%d %H:%M:%S")
    echo -e "$(border_color)║ ${CYAN}运行时间: $current_time${WHITE}                            ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)║ ${GREEN}作者: 幻穗${WHITE}    ${YELLOW}快手号: Luisner866x${WHITE}    ${BLUE}TG: HSMH886L${NC}$(border_color)║${NC}"
    echo -e "$(border_color)╠══════════════════════════════════════════════════════════════════╣${NC}"
    
    # 功能菜单 - 使用更粗的边框和分隔线
    echo -e "$(border_color)║ ${WHITE}[1] DAT解包        ${WHITE}[2] DAT打包                     ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)╠══════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "$(border_color)║ ${WHITE}[3] 限制UEXP解包   ${WHITE}[4] 限制UEXP打包                ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)╠══════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "$(border_color)║ ${WHITE}[5] 无限制UEXP解包 ${WHITE}[6] 无限制UEXP打包              ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)╠══════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "$(border_color)║ ${WHITE}[7] 自动修改手持火焰刀                                    ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)╠══════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "$(border_color)║ ${WHITE}[8] 大厅动作/头像框/播报                                 ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)╠══════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "$(border_color)║ ${WHITE}[9] 幻穗DAT提取(不会看快手)                              ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)╠══════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "$(border_color)║ ${WHITE}[10] 幻穗自动写配料表                                    ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)╠══════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "$(border_color)║ ${WHITE}[11] 写枪械配置(快)                                     ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)╠══════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "$(border_color)║ ${WHITE}[12] 自动局内伪实体                                     ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)╠══════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "$(border_color)║ ${WHITE}[13] 自动地铁原皮                                       ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)╠══════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "$(border_color)║ ${WHITE}[14] 自动查找DAT                                        ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)╠══════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "$(border_color)║ ${WHITE}[15] 写地铁配置                                         ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)╠══════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "$(border_color)║ ${WHITE}[16] 免ROOT输出                                         ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)╠══════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "$(border_color)║ ${WHITE}[17] H格式转换                                          ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)╠══════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "$(border_color)║ ${WHITE}[18] 自动语音包                                         ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)╠══════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "$(border_color)║ ${WHITE}[19] 衣服DAT                                            ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)╠══════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "$(border_color)║ ${WHITE}[20] 仓库品质                                           ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)╠══════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "$(border_color)║ ${WHITE}[21] 大厅水印                                           ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)╠══════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "$(border_color)║ ${WHITE}[22] 局内水印                                           ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)╠══════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "$(border_color)║ ${WHITE}[23] 搜索                                               ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)╠══════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "$(border_color)║ ${WHITE}[24] 伪实体                                               ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)╠══════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "$(border_color)║ ${RED}[0] 退出工具                                             ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)╚══════════════════════════════════════════════════════════════════╝${NC}"
}
# 从云端执行脚本
cloud_exec() {
    script_name=$1
    script_type=$2
    
    # 下载脚本到临时目录
    script_path="$TMP_DIR/$script_name"
    echo -e "${CYAN}▶ 从云端下载: $script_name${NC}"
    curl -sL "$CLOUD_BASE/$script_name" -o "$script_path"
    
    # 设置执行权限
    chmod +x "$script_path"
    
    # 根据类型执行
    case $script_type in
        sh) 
            echo -e "${GREEN}▶ 执行Shell脚本: $script_name${NC}"
            bash "$script_path"
            ;;
        py)
            echo -e "${GREEN}▶ 执行Python脚本: $script_name${NC}"
            python3 "$script_path"
            ;;
        *) 
            echo "未知脚本类型"
            return 1
            ;;
    esac
    
    # 清理临时文件
    rm -f "$script_path"
}

# 功能映射表
declare -A func_map=(
    [1]="dat解包.sh sh"
    [2]="dat打包.sh sh"
    [3]="限制uexp解包 py"
    [4]="限制uexp打包 py"
    [5]="无限制uexp解包 py"
    [6]="无限制uexp打包 py"
    [7]="自动修改手持火焰刀 py"
    [8]="大厅动作.头像框.播报 py"
    [9]="幻穗dat提取（不会看快手） py"
    [10]="幻穗自动写配料表 py"
    [11]="写枪械配置（快） py"
    [12]="自动局内伪实体 py"
    [13]="自动地铁原皮 py"
    [14]="自动查找dat py"
    [15]="写地铁配置 py"
    [16]="免root输出 py"
    [17]="h格式转换 py"
    [18]="自动语音包 py"
    [19]="衣服dat py"
    [20]="仓库品质 py"
    [21]="大厅水印 py"
    [22]="局内水印 py"
    [23]="搜索 py"
    [24]="伪实体 py"
)


# 执行功能
execute_function() {
    choice=$1
    map_entry=${func_map[$choice]}
    
    if [ -z "$map_entry" ]; then
        if [ "$choice" -eq 0 ]; then
            echo -e "$(border_color)╔══════════════════════════════════════════════════════════════════╗${NC}"
            echo -e "$(border_color)║${YELLOW}                  感谢使用HSTOOL，再见！                   ${NC}$(border_color)║${NC}"
            echo -e "$(border_color)╚══════════════════════════════════════════════════════════════════╝${NC}"
            exit 0
        else
            echo -e "$(border_color)╔══════════════════════════════════════════════════════════════════╗${NC}"
            echo -e "$(border_color)║${RED}                    无效选项，请重新输入                    ${NC}$(border_color)║${NC}"
            echo -e "$(border_color)╚══════════════════════════════════════════════════════════════════╝${NC}"
            sleep 1
            return
        fi
    fi

    # 分割映射条目
    IFS=' ' read -r script_name script_type <<< "$map_entry"
    
    echo -e "$(border_color)╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "$(border_color)║${GREEN}                    从云端加载: $script_name                  ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)╚══════════════════════════════════════════════════════════════════╝${NC}"
    
    # 从云端执行
    cloud_exec "$script_name" "$script_type"
    
    echo -e "$(border_color)╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "$(border_color)║${CYAN}                 操作完成，按回车键返回主菜单                  ${NC}$(border_color)║${NC}"
    echo -e "$(border_color)╚══════════════════════════════════════════════════════════════════╝${NC}"
    read -s -n 1
}

# 检查是否首次运行
if [ ! -f "/storage/emulated/0/幻穗制作区/.first_run_complete" ]; then
    welcome_screen
    first_run
fi

# 主循环
while true; do
    main_menu
    echo -ne "${BLUE}▶ 请选择操作: ${NC}"
    read choice
    execute_function "$choice"
done