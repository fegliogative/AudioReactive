# -*- mode: python ; coding: utf-8 -*-
# SoundReactive.spec
# PyInstaller spec file — privacy keys are baked directly into Info.plist
# so macOS TCC grants camera/microphone access without crashing.

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('SoundReactive_Logo_Transparent_BG.png', '.'),
        ('SoundReactive.icns', '.'),
    ],
    hiddenimports=[
        'librosa',
        'soundfile',
        'numba',
        'PyQt5.QtMultimedia',
        'PyQt5.QtMultimediaWidgets',
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
    [],
    exclude_binaries=True,
    name='SoundReactive',
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
    icon='SoundReactive.icns',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SoundReactive',
)

app = BUNDLE(
    coll,
    name='SoundReactive.app',
    icon='SoundReactive.icns',
    bundle_identifier='com.soundreactive.app',
    # ── Privacy usage descriptions ────────────────────────────────────────
    # These keys are REQUIRED by macOS TCC. Without them the OS kills the
    # process with SIGABRT the moment cv2.VideoCapture() tries to open the
    # camera, regardless of whether the user has previously granted access.
    info_plist={
        'CFBundleName': 'SoundReactive',
        'CFBundleDisplayName': 'SoundReactive',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSHighResolutionCapable': True,
        'NSCameraUsageDescription': (
            'SoundReactive uses your camera to apply real-time '
            'audio-reactive visual effects to your webcam feed.'
        ),
        'NSMicrophoneUsageDescription': (
            'SoundReactive may access the microphone for live audio '
            'analysis during webcam recording.'
        ),
    },
)
