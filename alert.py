import numpy as np
import pyautogui
import time
from joblib import load
from cnocr import CnOcr

# 内部程序调用
from say import speak
from utils import scollscreen, capture_screen_area, predict_icon_status, load_model_and_scaler, find_icon, load_location_name, find_txt_ocr, find_txt_ocr2
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

# 全局变量，用于控制程序是否继续运行
running = True

# 记录 Ctrl 键是否被按下
ctrl_pressed = False

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

def main():
    global running

    # 开始监听键盘事件
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    while running:
        time.sleep(2)
        
        # 加载"中立声望"模型和模板
        clf_zhongli, scaler_zhongli = models['zhongli']
        template_zhongli, w_zhongli, h_zhongli = templates['zhongli']

        # 加载"嫌犯声望"模型和模板
        clf_xianfan, scaler_xianfan = models['xianfan']
        template_xianfan, w_xianfan, h_xianfan = templates['xianfan']

        # 设置需要捕获的屏幕区域
        fx, fy = pyautogui.size()
        
        # 左侧面板
        left_panel = screen_regions['left_panel']
        # 中间面板
        center_panel = screen_regions['center_panel']
        # 右侧面板
        right_panel = screen_regions['right_panel']

        # 1. 准备开始
        
        # 查找[中立声望]或[嫌犯声望]
        try: 
            if (find_icon(template_zhongli, w_zhongli, h_zhongli, clf_zhongli, scaler_zhongli, 1, 0, 0, right_panel) or 
                find_icon(template_xianfan, w_xianfan, h_xianfan, clf_xianfan, scaler_xianfan, 1, 0, 0, right_panel)):  
                print("发现中立声望或嫌犯声望")
                play_sound_wav('soundlow.wav')  # 播放声音文件('sound.wav')  
                # speak("本地有白名")
                # speak("滴滴")
                # pyautogui.press('v')
                time.sleep(2)
        except IconNotFoundException as e:
            print(e)

    listener.join()  # 等待监听器结束
    
if __name__ == "__main__":
    main()
v