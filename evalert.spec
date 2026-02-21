# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['alert.py', 'model_config.py', 'say.py', 'utils.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('icon', 'icon'),
        ('model', 'model'),
        ('soundlow.wav', '.'),
    ],
    hiddenimports=[
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
    ],
    hookspath=['.'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

# onedir 模式：EXE 里一般 exclude_binaries=True，然后用 COLLECT 收集 dll/pyd/datas
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
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name='evalert',
)