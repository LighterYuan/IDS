#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脚本用于自动捕获正常网络流量
使用tshark（WireShark的命令行版本）进行流量捕获
"""

import os
import sys
import time
import argparse
import subprocess
from datetime import datetime

def parse_args():
    parser = argparse.ArgumentParser(description='捕获正常网络流量')
    parser.add_argument('-i', '--interface', required=True, help='网络接口名称')
    parser.add_argument('-c', '--count', type=int, default=200000, help='捕获的数据包数量（默认：200,000）')
    parser.add_argument('-o', '--output', default='../data/normal/', help='输出目录')
    
    return parser.parse_args()

def capture_traffic(interface, count, output_dir):
    """使用tshark捕获网络流量"""
    
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 生成输出文件名，包含时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"normal_traffic_{timestamp}.pcap")
    
    print(f"开始捕获流量，接口：{interface}，目标数据包数：{count}")
    print(f"输出文件：{output_file}")
    
    try:
        # 使用tshark命令捕获流量
        cmd = [
            "tshark", 
            "-i", interface,
            "-c", str(count),
            "-w", output_file
        ]
        
        process = subprocess.Popen(cmd)
        
        # 等待捕获完成
        process.wait()
        
        if process.returncode == 0:
            print(f"成功捕获流量，已保存至: {output_file}")
            print(f"捕获的数据包数量: {count}")
            return output_file
        else:
            print(f"流量捕获失败，返回码: {process.returncode}")
            return None
    
    except Exception as e:
        print(f"捕获过程中出错: {str(e)}")
        return None

def convert_to_features(pcap_file):
    """使用CICFlowMeter将pcap文件转换为特征"""
    if not pcap_file or not os.path.exists(pcap_file):
        print("PCAP文件不存在，无法转换特征")
        return False
    
    # CICFlowMeter的路径需要根据实际安装位置调整
    cicflowmeter_path = "../tools/CICFlowMeter/bin/CICFlowMeter"
    
    output_dir = os.path.dirname(pcap_file)
    
    try:
        # 调用CICFlowMeter进行特征提取
        cmd = [
            cicflowmeter_path,
            pcap_file,
            output_dir
        ]
        
        print(f"开始转换特征，输入文件：{pcap_file}")
        
        process = subprocess.Popen(cmd)
        process.wait()
        
        if process.returncode == 0:
            print(f"特征转换成功，输出目录：{output_dir}")
            return True
        else:
            print(f"特征转换失败，返回码：{process.returncode}")
            return False
    
    except Exception as e:
        print(f"特征转换过程中出错: {str(e)}")
        return False

def main():
    args = parse_args()
    
    # 捕获流量
    pcap_file = capture_traffic(args.interface, args.count, args.output)
    
    # 转换特征
    if pcap_file:
        convert_to_features(pcap_file)

if __name__ == "__main__":
    main() 