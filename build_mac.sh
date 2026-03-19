#!/bin/bash
# build_mac.sh
# Automates the creation of a macOS .app bundle and .dmg installer for SoundReactive.
# Privacy keys (NSCameraUsageDescription, NSMicrophoneUsageDescription) are baked
# into Info.plist via SoundReactive.spec so macOS TCC never kills the process.

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

# 3. Build the .app bundle using the spec file
#    The spec file bakes NSCameraUsageDescription and NSMicrophoneUsageDescription
#    directly into Info.plist at compile time.
echo "📦 Running PyInstaller (using SoundReactive.spec)..."
pyinstaller SoundReactive.spec

# 4. Verify the privacy keys made it into Info.plist
echo "🔍 Verifying Info.plist privacy keys..."
INFO_PLIST="dist/SoundReactive.app/Contents/Info.plist"

if /usr/libexec/PlistBuddy -c "Print :NSCameraUsageDescription" "$INFO_PLIST" &>/dev/null; then
    echo "   ✅ NSCameraUsageDescription found."
else
    echo "   ⚠️  NSCameraUsageDescription missing — injecting manually..."
    /usr/libexec/PlistBuddy -c \
      "Add :NSCameraUsageDescription string 'SoundReactive uses your camera to apply real-time audio-reactive visual effects to your webcam feed.'" \
      "$INFO_PLIST"
fi

if /usr/libexec/PlistBuddy -c "Print :NSMicrophoneUsageDescription" "$INFO_PLIST" &>/dev/null; then
    echo "   ✅ NSMicrophoneUsageDescription found."
else
    echo "   ⚠️  NSMicrophoneUsageDescription missing — injecting manually..."
    /usr/libexec/PlistBuddy -c \
      "Add :NSMicrophoneUsageDescription string 'SoundReactive may access the microphone for live audio analysis during webcam recording.'" \
      "$INFO_PLIST"
fi

# 5. Reset the TCC permission cache for this app so macOS re-evaluates
#    the new Info.plist on next launch (avoids stale "no permission" state).
echo "🔑 Resetting TCC permission cache for SoundReactive..."
tccutil reset Camera com.soundreactive.app 2>/dev/null || true
tccutil reset Microphone com.soundreactive.app 2>/dev/null || true

# 6. Create the DMG
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

echo ""
echo "✅ Build complete!  →  SoundReactive.dmg"
echo ""
echo "📋 After installing the new DMG:"
echo "   1. Delete the old SoundReactive.app from /Applications first."
echo "   2. Open the new DMG and drag SoundReactive to /Applications."
echo "   3. Launch the app — macOS will ask for camera permission once."
