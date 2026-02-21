# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['mon.py','autologin.py','model_config.py','speech.py','utils.py'],
    pathex=[],
    binaries=[],
    datas=[('static/dll/Microsoft.CognitiveServices.Speech.core.dll', '.'),
    ('static/dll/Microsoft.CognitiveServices.Speech.extension.audio.sys.dll', '.'),
    ('static/dll/Microsoft.CognitiveServices.Speech.extension.codec.dll', '.'),
    ('static/dll/Microsoft.CognitiveServices.Speech.extension.kws.dll', '.'),
    ('static/dll/Microsoft.CognitiveServices.Speech.extension.lu.dll','.')],
    hiddenimports=['scipy.special._cdflib','sklearn','sklearn.pipeline','sklearn.ensemble._forest','sklearn.utils._typedefs','sklearn.utils._heap','sklearn.utils._sorting','sklearn.utils._vector_sentinel','sklearn.neighbors._partition_nodes'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Athena',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='D:\\Workspace\\git\\Athena\\ico.png'
)
