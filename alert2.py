import sys
import numpy as np
import pyautogui
import time
from joblib import load
from cnocr import CnOcr
import cv2
import os
import pynput
from datetime import datetime

# 内部程序调用
from say import speak
from utils import scollscreen, capture_screen_area, predict_icon_status, load_model_and_scaler, find_icon, load_location_name, find_txt_ocr, find_txt_ocr2, find_txt_ocr3
from model_config import models, templates, screen_regions

from pydub import AudioSegment
from pydub.playback import play

from pynput import keyboard


class IconNotFoundException(Exception):
    """Exception raised when an icon is not found."""
    pass

class GoodsNotFoundException(Exception):
    """Exception raised when the specified goods are not found."""
    pass

# 加载并播放音频
def play_sound_wav(file_path):
    sound = AudioSegment.from_file(file_path, format="wav")
    play(sound)

def emergency_evasion(reason):
    """
    紧急规避函数
    reason: 触发紧急规避的原因（字符串）
    """
    ctr = pynput.keyboard.Controller()
    with ctr.pressed(pynput.keyboard.Key.ctrl, 's'):
        print(f"[警报] {reason},紧急规避")
        speak(f"{reason},紧急规避")
        time.sleep(0.1)
        pass
    sys.exit(1)

# 全局变量，用于控制程序是否继续运行
running = True

# 记录 Ctrl 键是否被按下
ctrl_pressed = False

# 调试模式：是否保存误识别截图
DEBUG_MODE = False
DEBUG_SAVE_DIR = "debug_icons"
# 警告阈值：匹配值超过此值但未通过验证时显示警告（0.7表示70%相似度）
WARNING_THRESHOLD = 0.75

def on_press(key):
    global running, ctrl_pressed
    try:
        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            ctrl_pressed = True
        if key == keyboard.Key.f12 and ctrl_pressed:
            running = False
            print("Ctrl+F12 pressed, stopping the program.")
            return False  # Stop the listener
    except AttributeError:
        pass

def on_release(key):
    global ctrl_pressed
    if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
        ctrl_pressed = False

def find_icon_count(icon_name, template, width, height, clf, scaler, max_attempts=1, offset_x=0, offset_y=0, region=None, match_threshold=0.8):
    """
    统计检测到的图标数量（包括同一类型的多个实例）
    返回: (count, details_list)
    count: 检测到的图标数量
    details_list: 每个检测到的图标的详细信息列表
    """
    if region is None:
        fx, fy = pyautogui.size()
        region = (0, 0, fx, fy)

    attempts = 0
    while attempts < max_attempts:
        screen = capture_screen_area(region)
        res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        
        # 找到所有超过阈值的匹配位置
        locations = np.where(res >= match_threshold)
        found_count = 0
        details_list = []
        
        # 对每个匹配位置进行验证
        for pt in zip(*locations[::-1]):  # Switch x and y coordinates
            match_val = res[pt[1], pt[0]]
            
            # 提取图标区域
            icon_image = screen[pt[1]:pt[1] + height, pt[0]:pt[0] + width]
            
            # 检查图标区域是否有效
            if icon_image.shape[0] != height or icon_image.shape[1] != width:
                continue
            
            # 使用模型验证
            model_result = predict_icon_status(icon_image, clf, scaler)
            
            if model_result:
                x = pt[0] + region[0] + width // 2 + offset_x
                y = pt[1] + region[1] + height // 2 + offset_y
                
                details = {
                    'icon_name': icon_name,
                    'match_val': match_val,
                    'model_prediction': model_result,
                    'position': (x, y)
                }
                details_list.append(details)
                found_count += 1
                
                # 如果启用调试模式，保存检测到的图标截图
                if DEBUG_MODE:
                    save_debug_image(icon_name, icon_image, match_val, model_result, True)
            else:
                # 模板匹配成功但模型验证失败，可能是误识别
                if DEBUG_MODE:
                    save_debug_image(icon_name, icon_image, match_val, model_result, False)
        
        if found_count > 0:
            return found_count, details_list
            
        attempts += 1
        time.sleep(0.2)
    
    return 0, []

def find_icon_detailed(icon_name, template, width, height, clf, scaler, max_attempts=1, offset_x=0, offset_y=0, region=None):
    """
    详细检测图标，返回检测结果和详细信息（保留用于兼容性）
    返回: (found, details)
    details包含: match_val, model_prediction, position等
    """
    count, details_list = find_icon_count(icon_name, template, width, height, clf, scaler, max_attempts, offset_x, offset_y, region)
    if count > 0:
        return True, details_list[0]  # 返回第一个检测到的图标信息
    else:
        return False, {'icon_name': icon_name, 'match_val': 0, 'model_prediction': False, 'position': None, 'found': False}

def save_debug_image(icon_name, icon_image, match_val, model_prediction, is_correct):
    """保存调试截图"""
    if not os.path.exists(DEBUG_SAVE_DIR):
        os.makedirs(DEBUG_SAVE_DIR)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    status = "correct" if is_correct else "false_positive"
    filename = f"{icon_name}_{status}_match{match_val:.3f}_model{model_prediction}_{timestamp}.png"
    filepath = os.path.join(DEBUG_SAVE_DIR, filename)
    cv2.imwrite(filepath, icon_image)
    print(f"[调试] 已保存截图: {filepath}")

def find_txt_ocr3_debug(txt, max_attempts=1, region=None):
    """
    带调试功能的OCR文字识别
    返回: (found, all_ocr_texts)
    """
    from cnocr import CnOcr
    
    if region is None:
        fx, fy = pyautogui.size()
        region = (0, 0, fx, fy)

    attempts = 0
    all_ocr_texts = []
    
    while attempts < max_attempts:        
        # 初始化OCR工具
        ocr = CnOcr(rec_model_name='scene-densenet_lite_246-gru_base')
        screen_image = pyautogui.screenshot(region=region)
        res = ocr.ocr(screen_image)  # 使用 ocr 方法处理整个图像
        
        # 收集所有识别到的文字
        current_texts = []
        for line in res:
            text = line['text']
            current_texts.append(text)
            all_ocr_texts.append(text)
            
            # 检查是否包含目标文字
            if txt in text:
                x = region[0] + line['position'][0][0] + (line['position'][1][0] - line['position'][0][0]) // 2
                y = region[1] + line['position'][0][1] + (line['position'][2][1] - line['position'][0][1]) // 2
                pyautogui.moveTo(x, y)
                print(f"[OCR] 找到文字 {txt} 在位置 ({x}, {y})")
                return True, ' | '.join(all_ocr_texts)
        
        attempts += 1
        time.sleep(0.5)
    
    # 返回所有识别到的文字，用 | 分隔
    return False, ' | '.join(all_ocr_texts) if all_ocr_texts else ''

def main():
    global running

    # 开始监听键盘事件
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    while running:
        # 主循环间隔控制为1秒，结合模板匹配和OCR耗时，整体扫描频率约为3秒一轮
        time.sleep(5)
        
        # # 加载"中立声望"模型和模板
        # clf_zhongli, scaler_zhongli = models['zhongli']
        # template_zhongli, w_zhongli, h_zhongli = templates['zhongli']

        # 加载"嫌犯声望"模型和模板
        clf_xianfan, scaler_xianfan = models['xianfan']
        template_xianfan, w_xianfan, h_xianfan = templates['xianfan']

        # 加载"罪犯声望"模型和模板
        clf_zuifan, scaler_zuifan = models['zuifan']
        template_zuifan, w_zuifan, h_zuifan = templates['zuifan']

        # # 加载"交战声望"模型和模板
        # clf_jiaozhan, scaler_jiaozhan = models['jiaozhan']
        # template_jiaozhan, w_jiaozhan, h_jiaozhan = templates['jiaozhan']

        # 加载"击杀权限"模型和模板
        clf_jisha, scaler_jisha = models['jisha']
        template_jisha, w_jisha, h_jisha = templates['jisha']

        # 设置需要捕获的屏幕区域
        fx, fy = pyautogui.size()
        
        # 左侧面板
        left_panel = screen_regions['left_panel']
        # 中间面板
        center_panel = screen_regions['center_panel']
        # 右侧面板
        right_panel = screen_regions['right_panel']

        # 1. 准备开始
        
        # 分别检测每个图标，记录详细信息用于排查
        try: 
            ctr = pynput.keyboard.Controller()

            # 使用鼠标中键触发雷达扫描：按住0.2秒再松开
            pyautogui.mouseDown(button='middle')
            print("雷达扫描进行中...")
            time.sleep(0.5)
            pyautogui.mouseUp(button='middle')

            # 统计所有检测到的图标数量（包括同一类型的多个实例）
            total_icon_count = 0
            icon_details_summary = []
            
            # 检测"罪犯声望"并统计数量
            zuifan_count, zuifan_details_list = find_icon_count(
                "zuifan", template_zuifan, w_zuifan, h_zuifan, 
                clf_zuifan, scaler_zuifan, 1, 0, 0, right_panel
            )
            if zuifan_count > 0:
                total_icon_count += zuifan_count
                for detail in zuifan_details_list:
                    icon_details_summary.append(("罪犯", detail))
                    print(f"[检测] 罪犯声望 - 匹配值: {detail['match_val']:.3f}, "
                          f"模型预测: {detail['model_prediction']}, "
                          f"位置: {detail['position']}")
            
            # 检测"击杀权限"并统计数量
            jisha_count, jisha_details_list = find_icon_count(
                "jisha", template_jisha, w_jisha, h_jisha, 
                clf_jisha, scaler_jisha, 1, 0, 0, right_panel
            )
            if jisha_count > 0:
                total_icon_count += jisha_count
                for detail in jisha_details_list:
                    icon_details_summary.append(("击杀", detail))
                    print(f"[检测] 击杀权限 - 匹配值: {detail['match_val']:.3f}, "
                          f"模型预测: {detail['model_prediction']}, "
                          f"位置: {detail['position']}")
            
            # 检测"嫌犯声望"并统计数量
            xianfan_count, xianfan_details_list = find_icon_count(
                "xianfan", template_xianfan, w_xianfan, h_xianfan, 
                clf_xianfan, scaler_xianfan, 1, 0, 0, right_panel
            )
            if xianfan_count > 0:
                total_icon_count += xianfan_count
                for detail in xianfan_details_list:
                    icon_details_summary.append(("嫌犯", detail))
                    print(f"[检测] 嫌犯声望 - 匹配值: {detail['match_val']:.3f}, "
                          f"模型预测: {detail['model_prediction']}, "
                          f"位置: {detail['position']}")
            
            icon_found = total_icon_count > 0  # 至少检测到一个图标
            
            # 同时进行文字识别，查找"促进"，返回识别到的个数
            txt_count = find_txt_ocr3("促进", 1, right_panel)
            txt_found = txt_count >= 2  # 当检测到2个及2个以上"促进"时触发
            
            # 统计所有检测到的图标和文字总数
            total_danger_count = total_icon_count + txt_count
            
            # 当识别到"罪犯"或"击杀"或"嫌犯"时触发声音告警
            if icon_found:
                play_sound_wav('soundlow.wav')  # 播放声音文件('sound.wav')
                icon_names = [name for name, _ in icon_details_summary]
                print(f"[警报] 发现图标: {', '.join(icon_names)} (共{total_icon_count}个)")
            
            # 当检测到2个及以上图标或文字时触发紧急规避
            if total_danger_count >= 2:
                danger_items = []
                if total_icon_count > 0:
                    icon_summary = {}
                    for name, _ in icon_details_summary:
                        icon_summary[name] = icon_summary.get(name, 0) + 1
                    icon_str = ', '.join([f"{name}{count}个" if count > 1 else name for name, count in icon_summary.items()])
                    danger_items.append(f"图标{icon_str}(共{total_icon_count}个)")
                if txt_count > 0:
                    danger_items.append(f"促进级舰船{txt_count}个")
                
                reason = f"发现{'、'.join(danger_items)}"
                emergency_evasion(reason)

        except IconNotFoundException as e:
            print(e)

    listener.join()  # 等待监听器结束
    
if __name__ == "__main__":
    main()
