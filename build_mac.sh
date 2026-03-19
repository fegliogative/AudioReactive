#!/bin/bash
# build_mac.sh
# Automates the creation of a macOS .app bundle and .dmg installer for SoundReactive.

set -e

echo "🎵 Building SoundReactive for macOS..."

# 1. Check for required tools
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller not found. Installing..."
    pip3 install pyinstaller
fi

if ! command -v create-dmg &> /dev/null; then
    echo "❌ create-dmg not found. Please install it via Homebrew:"
    echo "   brew install create-dmg"
    exit 1
fi

# 2. Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ SoundReactive.dmg

# 3. Build the .app bundle with PyInstaller
echo "📦 Running PyInstaller..."
pyinstaller --name "SoundReactive" \
            --windowed \
            --icon "SoundReactive.icns" \
            --add-data "SoundReactive_Logo_Transparent_BG.png:." \
            --add-data "SoundReactive.icns:." \
            --hidden-import "librosa" \
            --hidden-import "soundfile" \
            --hidden-import "numba" \
            --hidden-import "PyQt5.QtMultimedia" \
            --hidden-import "PyQt5.QtMultimediaWidgets" \
            app.py

# 4. Inject macOS privacy usage descriptions into Info.plist
#    Without these keys macOS TCC kills the process the moment it
#    tries to access the camera or microphone.
echo "🔑 Adding privacy usage descriptions to Info.plist..."
INFO_PLIST="dist/SoundReactive.app/Contents/Info.plist"

/usr/libexec/PlistBuddy -c \
  "Add :NSCameraUsageDescription string 'SoundReactive uses your camera to apply real-time audio-reactive visual effects to your webcam feed.'" \
  "$INFO_PLIST" 2>/dev/null || \
/usr/libexec/PlistBuddy -c \
  "Set :NSCameraUsageDescription 'SoundReactive uses your camera to apply real-time audio-reactive visual effects to your webcam feed.'" \
  "$INFO_PLIST"

/usr/libexec/PlistBuddy -c \
  "Add :NSMicrophoneUsageDescription string 'SoundReactive may access the microphone for live audio analysis during webcam recording.'" \
  "$INFO_PLIST" 2>/dev/null || \
/usr/libexec/PlistBuddy -c \
  "Set :NSMicrophoneUsageDescription 'SoundReactive may access the microphone for live audio analysis during webcam recording.'" \
  "$INFO_PLIST"

echo "✅ Privacy descriptions added."

# 5. Create the DMG
echo "💿 Creating DMG installer..."
create-dmg \
  --volname "SoundReactive" \
  --volicon "SoundReactive.icns" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --icon "SoundReactive.app" 175 190 \
  --hide-extension "SoundReactive.app" \
  --app-drop-link 425 190 \
  "SoundReactive.dmg" \
  "dist/"

echo "✅ Build complete! You can find your installer at: SoundReactive.dmg"
