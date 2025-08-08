# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['screen_selector.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('CARDS', 'CARDS'),  # Kart görselleri
        ('CROPPEDCARDS', 'CROPPEDCARDS'),  # Kırpılmış kart görselleri
    ],
    hiddenimports=[
        'PIL._tkinter_finder',
        'cv2',
        'mss',
        'psutil',
        'numpy',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'json',
        'os',
        'time',
        'threading',
        'multiprocessing',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='KartSayici',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI uygulaması olduğu için console=False
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # İkon eklemek isterseniz: icon='icon.ico'
) 