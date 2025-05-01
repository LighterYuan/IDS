#!/bin/bash
# 用于配置实验网络环境的脚本

# 颜色设置
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 打印带颜色的信息
function print_info() {
    echo -e "${GREEN}[INFO] $1${NC}"
}

function print_warn() {
    echo -e "${YELLOW}[WARN] $1${NC}"
}

function print_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

function check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "请使用root权限运行此脚本"
        exit 1
    fi
}

# 检查所需工具是否安装
function check_requirements() {
    tools=("ip" "brctl" "iptables")
    
    for tool in "${tools[@]}"; do
        if ! command -v $tool &> /dev/null; then
            print_error "未找到命令: $tool，请安装后重试"
            exit 1
        fi
    done
}

# 设置步骤一：单一网段
function setup_single_network() {
    print_info "配置步骤一：单一网段环境"
    
    # 创建网桥（模拟交换机）
    if ! brctl show | grep -q "br0"; then
        print_info "创建网桥 br0..."
        brctl addbr br0
        ip link set dev br0 up
        ip addr add 192.168.1.1/24 dev br0
    else
        print_warn "网桥 br0 已存在"
    fi
    
    print_info "单一网段环境配置完成"
    print_info "网桥IP地址: 192.168.1.1/24"
    print_info "主机应该配置为: 192.168.1.101-104/24"
}

# 设置步骤二：双子网
function setup_dual_subnets() {
    print_info "配置步骤二：双子网环境"
    
    # 清理旧的网桥
    if brctl show | grep -q "br0"; then
        print_info "删除已存在的网桥 br0..."
        ip link set dev br0 down
        brctl delbr br0
    fi
    
    # 创建子网A网桥
    print_info "创建子网A网桥 brA..."
    brctl addbr brA
    ip link set dev brA up
    ip addr add 192.168.10.1/24 dev brA
    
    # 创建子网B网桥
    print_info "创建子网B网桥 brB..."
    brctl addbr brB
    ip link set dev brB up
    ip addr add 192.168.20.1/24 dev brB
    
    # 启用IP转发
    print_info "启用IP转发..."
    echo 1 > /proc/sys/net/ipv4/ip_forward
    
    # 配置NAT
    print_info "配置NAT以便子网间通信..."
    iptables -t nat -A POSTROUTING -s 192.168.10.0/24 -o brB -j MASQUERADE
    iptables -t nat -A POSTROUTING -s 192.168.20.0/24 -o brA -j MASQUERADE
    
    print_info "双子网环境配置完成"
    print_info "子网A: 192.168.10.0/24 (攻击机: 192.168.10.101, 靶机: 192.168.10.102)"
    print_info "子网B: 192.168.20.0/24 (攻击机: 192.168.20.101, 靶机: 192.168.20.102)"
}

# 显示当前网络配置
function show_network_config() {
    print_info "当前网络配置:"
    
    echo "=== 网桥配置 ==="
    brctl show
    
    echo -e "\n=== 网络接口配置 ==="
    ip addr show
    
    echo -e "\n=== 路由表 ==="
    ip route
}

# 清理所有网络配置
function cleanup() {
    print_info "清理网络配置..."
    
    # 删除网桥
    for br in $(brctl show | grep -v "bridge name" | awk '{print $1}' | grep -v "^$"); do
        print_info "删除网桥 $br..."
        ip link set dev $br down
        brctl delbr $br
    done
    
    # 清理iptables规则
    print_info "清理iptables规则..."
    iptables -F
    iptables -t nat -F
    
    print_info "网络配置已清理"
}

# 主函数
function main() {
    check_root
    check_requirements
    
    case "$1" in
        single)
            setup_single_network
            ;;
        dual)
            setup_dual_subnets
            ;;
        show)
            show_network_config
            ;;
        clean)
            cleanup
            ;;
        *)
            echo "用法: $0 {single|dual|show|clean}"
            echo "  single: 配置步骤一的单一网段环境"
            echo "  dual: 配置步骤二的双子网环境"
            echo "  show: 显示当前网络配置"
            echo "  clean: 清理所有网络配置"
            exit 1
            ;;
    esac
    
    exit 0
}

main "$@" 