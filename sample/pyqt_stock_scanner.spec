# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec: pyqt_stock_scanner.py → macOS .app / Windows exe

from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

hiddenimports = [
    'korbacktest',
    'FinanceDataReader',
    'pandas_ta',
    'numba',
    'yfinance',
    'dotenv',
    'matplotlib.backends.backend_qt5agg',
]
hiddenimports += collect_submodules('FinanceDataReader')

datas = []
for pkg in ('FinanceDataReader', 'pandas_ta'):
    try:
        tmp = collect_all(pkg)
        datas += tmp[0]
        hiddenimports += tmp[1]
    except Exception:
        pass

a = Analysis(
    ['pyqt_stock_scanner.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['streamlit', 'altair', 'pydeck'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='StockScanner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='StockScanner',
)

app = BUNDLE(
    coll,
    name='StockScanner.app',
    icon=None,
    bundle_identifier='com.local.stockscanner',
)
