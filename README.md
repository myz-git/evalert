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
```

## 训练模型

