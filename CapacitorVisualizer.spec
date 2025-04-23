# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['capacitor_visualizer_app.py'],
    pathex=[],
    binaries=[],
    datas=[('README.md', '.')],
    hiddenimports=['numpy', 'pandas', 'matplotlib', 'scipy', 'matplotlib.backends.backend_tkagg', 'tkinter'],
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
    name='CapacitorVisualizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
app = BUNDLE(
    exe,
    name='CapacitorVisualizer.app',
    icon=None,
    bundle_identifier=None,
)
