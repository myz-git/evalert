import cv2
import os
from joblib import load

def load_model_and_scaler(base_path, model_name):
    clf = load(os.path.join(base_path, f'trained_model_{model_name}.joblib'))
    scaler = load(os.path.join(base_path, f'scaler_{model_name}.joblib'))
    return clf, scaler

def load_template(icon_path):
    template = cv2.imread(icon_path, cv2.IMREAD_COLOR)
    return template, template.shape[1], template.shape[0]  # width, height

# 定义图标模板和模型路径
base_path = 'model'
icon_base_path = 'icon'

# 模型和模板加载
"""
zhongli 中立声望
xianfan 嫌犯声望
buliang 不良声望
zuifan 罪犯声望
jiaozhan    交战声望
jisha  击杀权限
"""
# model_names = ['zhongli', 'xianfan', 'buliang', 'zuifan', 'jiaozhan']
model_names = ['zhongli', 'xianfan', 'buliang', 'zuifan', 'jisha']
models = {name: load_model_and_scaler(base_path, name) for name in model_names}
templates = {name: load_template(os.path.join(icon_base_path, f'{name}-1.png')) for name in model_names}

# 屏幕区域配置
screen_regions = {
    'left_panel': (30, 30, 300, 800),  # 左侧面板
    'center_panel': (300, 30, 800, 800),  # 中间面板
    'right_panel': (1000, 30, 700, 1000)  # 右侧面板
}
