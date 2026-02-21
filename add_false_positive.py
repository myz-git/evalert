"""
将误检的图像添加到负样本训练集中，并重新训练模型
使用方法: python add_false_positive.py <icon_name> <false_positive_image_path>
例如: python add_false_positive.py jisha debug_icons/jisha_correct_match0.817_modelTrue_20260119_113706_775411.png
"""
import os
import shutil
import sys
from datetime import datetime

def add_false_positive(icon_name, false_positive_path):
    """将误检图像添加到负样本训练集"""
    # 创建负样本文件夹（如果不存在）
    negative_folder = f'traindata/{icon_name}-0'
    if not os.path.exists(negative_folder):
        os.makedirs(negative_folder)
        print(f"创建负样本文件夹: {negative_folder}")
    
    # 检查源文件是否存在
    if not os.path.exists(false_positive_path):
        print(f"错误: 文件不存在: {false_positive_path}")
        return False
    
    # 生成目标文件名（使用时间戳避免重复）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = os.path.basename(false_positive_path)
    name, ext = os.path.splitext(filename)
    target_filename = f"{icon_name}-0-{timestamp}{ext}"
    target_path = os.path.join(negative_folder, target_filename)
    
    # 复制文件
    shutil.copy2(false_positive_path, target_path)
    print(f"已添加负样本: {target_path}")
    
    # 统计负样本数量
    negative_count = len([f for f in os.listdir(negative_folder) if f.endswith('.png')])
    print(f"当前负样本数量: {negative_count}")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("使用方法: python add_false_positive.py <icon_name> <false_positive_image_path>")
        print("例如: python add_false_positive.py jisha debug_icons/jisha_correct_match0.817_modelTrue_20260119_113706_775411.png")
        sys.exit(1)
    
    icon_name = sys.argv[1]
    false_positive_path = sys.argv[2]
    
    if add_false_positive(icon_name, false_positive_path):
        print(f"\n下一步: 使用 train2stat.py 重新训练模型")
        print(f"命令: python train2stat.py {icon_name}")

