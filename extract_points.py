#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从GeoGebra .ggb文件中提取点的名称、x坐标和y坐标，并保存到CSV文件
"""

import zipfile
import xml.etree.ElementTree as ET
import csv
import sys
import os
from pathlib import Path


def extract_points_from_ggb(ggb_file_path, output_csv_path=None):
    """
    从.ggb文件中提取所有点的信息
    
    参数:
        ggb_file_path: .ggb文件路径
        output_csv_path: 输出CSV文件路径（可选，默认为输入文件名_points.csv）
    
    返回:
        点的列表，每个点是一个字典，包含'点名称'、'x'、'y'
    """
    # 检查文件是否存在
    if not os.path.exists(ggb_file_path):
        raise FileNotFoundError(f"文件不存在: {ggb_file_path}")
    
    # 如果没有指定输出路径，使用默认名称
    if output_csv_path is None:
        base_name = Path(ggb_file_path).stem
        output_csv_path = os.path.join(
            os.path.dirname(ggb_file_path),
            f"{base_name}_points.csv"
        )
    
    points = []
    
    try:
        # 打开.ggb文件（实际上是一个ZIP文件）
        with zipfile.ZipFile(ggb_file_path, 'r') as zip_ref:
            # 读取geogebra.xml文件
            xml_content = zip_ref.read('geogebra.xml')
            
            # 解析XML
            root = ET.fromstring(xml_content)
            
            # 查找所有type="point"的元素
            # 使用命名空间（如果有的话）
            namespace = {'': ''}  # GeoGebra XML通常没有命名空间前缀
            point_elements = root.findall(".//element[@type='point']")
            
            for point_element in point_elements:
                # 获取点的标签（名称）
                label = point_element.get('label', '')
                
                # 查找coords元素
                coords = point_element.find('coords')
                if coords is not None:
                    x = coords.get('x', '')
                    y = coords.get('y', '')
                    
                    # 只添加有有效坐标的点
                    if x != '' and y != '':
                        try:
                            # 转换为浮点数以确保格式正确
                            x_float = float(x)
                            y_float = float(y)
                            points.append({
                                '点名称': label,
                                'x': x_float,
                                'y': y_float
                            })
                        except ValueError:
                            # 如果坐标无法转换为数字，跳过
                            print(f"警告: 点 '{label}' 的坐标无法转换为数字 (x={x}, y={y})")
                            continue
    
    except zipfile.BadZipFile:
        raise ValueError(f"文件不是有效的ZIP文件: {ggb_file_path}")
    except ET.ParseError as e:
        raise ValueError(f"XML解析错误: {e}")
    except KeyError:
        raise ValueError("ZIP文件中找不到geogebra.xml文件")
    
    # 保存到CSV文件
    if points:
        with open(output_csv_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            fieldnames = ['点名称', 'x', 'y']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for point in points:
                writer.writerow(point)
        
        print(f"成功提取 {len(points)} 个点，已保存到: {output_csv_path}")
    else:
        print("警告: 未找到任何点")
    
    return points


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python extract_points.py <ggb文件路径> [输出CSV文件路径]")
        print("示例: python extract_points.py calculus🌟.ggb")
        print("示例: python extract_points.py calculus🌟.ggb output.csv")
        sys.exit(1)
    
    ggb_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        points = extract_points_from_ggb(ggb_file, output_file)
        print(f"\n提取的点列表:")
        for point in points[:10]:  # 只显示前10个点
            print(f"  {point['点名称']}: ({point['x']}, {point['y']})")
        if len(points) > 10:
            print(f"  ... 还有 {len(points) - 10} 个点")
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

