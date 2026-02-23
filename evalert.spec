# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 1) 先定义 datas，并追加第三方包的数据文件（yaml/模型等）
datas = [
    ('icon', 'icon'),
    ('model', 'model'),
    ('soundlow.wav', '.'),
    ('soundhigh.wav', '.'),
    ('soundmid.wav', '.'),
]

# ✅ 关键：把 rapidocr/cnocr/cnstd 的非代码资源一起收进来
#datas += collect_data_files('rapidocr')
datas += collect_data_files('cnocr')
datas += collect_data_files('cnstd')

# 2) 先定义 hiddenimports，并追加第三方包的子模块（防止动态 import 漏包）
hiddenimports = [
    'scipy.special._cdflib',
    'sklearn',
    'sklearn.pipeline',
    'sklearn.ensemble._forest',
    'sklearn.utils._typedefs',
    'sklearn.utils._heap',
    'sklearn.utils._sorting',
    'sklearn.utils._vector_sentinel',
    'sklearn.neighbors._partition_nodes',

    'cnocr',
    'pydub',
    'pydub.playback',
    'simpleaudio',
    'pynput',
    'pynput.keyboard',
    'pyautogui',
    'cv2',
    'joblib',
    'numpy',
]

# hiddenimports += collect_submodules('rapidocr')
hiddenimports += collect_submodules('cnocr')
#hiddenimports += collect_submodules('cnstd')

a = Analysis(
    ['alert.py', 'model_config.py', 'say.py', 'utils.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=['.'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pkg_resources', 'setuptools','paddle', 'paddleocr', 'paddlepaddle'],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='evalert',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    icon=r'D:\Workspace\git\evalert\icon\ico.png',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name='evalert',
)