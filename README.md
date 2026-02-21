## 项目名称

EVE本地预警

## 项目目的

监控本地玩家列表,当出现中立,糟糕,不良玩家,进行声音,微信等方式预警;

## 项目架构



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



## 误检处理

打开debug   line 41:
DEBUG_MODE = True

执行alert2.py, 当触发误检后,误检图片会放到debug_icons下

将误检图片 移到 负样本目录中,如  traindata\jisha-0

执行重命名文件

```
python rename.py  jish-0
```

使用train2stat.py 训练模型:

```
python train2stat.py jisha
```

