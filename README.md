## 项目名称

EVE 本地预警（evalert）

## 项目目的

监控本地玩家列表：当出现中立、嫌犯、罪犯、击杀权限或促进级舰船等目标时，进行声音预警；高安模式可在达到条件时自动执行紧急规避（Ctrl+S 并退出）。

## 主要文件

- **alert.py** — 主程序，支持 A（低安）/ B（高安）两种模式
- **model_config.py** — 模型与屏幕区域配置
- **utils.py** — 截屏、图标检测、OCR、模板匹配等
- **say.py** — 语音播报
- **icon/** — 图标模板（如 zhongli-1.png、jisha-1.png）
- **model/** — 训练好的分类模型与 scaler
- **traindata/** — 训练正负样本（如 jisha-1、jisha-0）
- **evalert.spec** — PyInstaller 打包配置

## 环境准备

```
cd D:\Workspace\git\evalert\
##conda remove -n evalert --all
conda create -n evalert python=3.11.7
conda activate evalert

pip install pillow pyautogui opencv-python numpy 
pip install scikit-learn scikit-image
pip install onnxruntime
pip install cnocr
pip install pyttsx3
pip install keyboard

pip install pydub simpleaudio
pip install pynput

pip install pyinstaller
```

## 训练模型

### 1. 准备原始图标

```
icon/zhongli-1.png
```

### 2. 执行snap截取  (traindata)

```
python snap.py zhongli-1.png
```

### 3. 训练生成模型

因为就一种状态,使用train1stat.py (如果是两种状态就用train2stat.py)

```
python train1stat.py zhongli
```

###  4. 得到两个模型:

model/trained_model_zhongli.joblib
model/scaler_zhongli.joblib



类似得到其他模型:

```
--不良
model/trained_model_buliang.joblib
model/scaler_buliang.joblib
--嫌犯
model/trained_model_xianfan.joblib
model/scaler_xianfan.joblib

```



## 主程序

主入口为 **alert.py**。

### 运行方式

```bash
python alert.py        # 默认 A 模式（低安）
python alert.py -a     # A 模式
python alert.py -b     # B 模式（高安）
```

### 两种模式

| 项目       | A 模式（低安）           | B 模式（高安）                 |
|------------|--------------------------|--------------------------------|
| 参数       | 默认或 `-a` / `-A`      | `-b` / `-B`                    |
| 监控项     | 中立、嫌犯、罪犯、击杀（图标） | 嫌犯、罪犯、击杀（图标）+ 文字「促进」 |
| 触发后行为 | 仅声音告警               | 声音告警；危险数 ≥2 时执行紧急规避并退出 |
| 扫描间隔   | 约 5 秒/轮               | 约 5 秒/轮                     |

- **A 模式**：不检测「促进」文字，只做图标检测；任一监控项触发即播放 `soundlow.wav`。
- **B 模式**：图标 + OCR 检测「促进」；当图标与「促进」合计 ≥2 时执行紧急规避（Ctrl+S、语音提示后退出）。

### 快捷键

- **Ctrl + F12**：停止程序。

### 打包后运行

`pyinstaller evalert.spec` 生成 `evalert.exe` 后，运行 exe 等同默认执行 `python alert.py`（A 模式）。若需 B 模式，需通过命令行传入参数（取决于打包是否支持）。

## 误检处理

1. 在 **alert.py** 中打开调试（约第 56 行）：`DEBUG_MODE = True`
2. 运行 alert.py，误检时的截图会保存到 **debug_icons** 目录
3. 将误检截图复制到对应负样本目录，例如 `traindata\jisha-0`
4. 若需重命名：`python rename.py jisha`
5. 使用负样本重新训练：`python train2stat.py jisha`

## 打包

```bash
pyinstaller evalert.spec
```

将生成的 **evalert.exe** 与 `soundlow.wav`、`icon`、`model` 等依赖放在同一目录后运行。详见 spec 内 datas 配置。
