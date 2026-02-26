# SoundReactive - Audio-Reactive Video Generator 🎵🎬

Transform your videos, images, and live webcam feeds into dynamic, music-reactive experiences! This powerful Python application analyzes audio frequencies and automatically applies synchronized visual effects in **real-time**, allowing you to see and adjust effects instantly as you tweak the controls.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)

## ✨ Key Features

### 🎯 Real-Time Effect Tweaking
**The app responds instantly!** Adjust any slider, toggle any effect, or change any setting and see the results update in near real-time. No need to wait for processing - experiment freely and find the perfect settings before rendering your final video.

### 🎬 Multiple Input Modes
- **Video Mode**: Enhance existing videos with audio-reactive effects
- **Image + Audio Mode**: Transform static images into dynamic music videos
- **Folder of Images + Audio**: Create videos from multiple images with smooth crossfades
- **Webcam + Audio (Live)**: Apply effects to live webcam feed and record with audio playback

### 🎨 Comprehensive Visual Effects
- **Basic Effects**: Zoom, rotation, frame navigation
- **Advanced Effects**: Intensity sensitivity, smoothness, color grading, blur, brightness, hue shift
- **8 Artistic Effects**: Pixel sorting, kaleidoscope, wave distortion, VHS degradation, posterization, edge detection, data corruption, CRT scan lines
- **Frequency Mixing**: Fine-tune how each artistic effect responds to different frequency bands
- **Layer Blending**: Multiple blend modes (Direct, Multiply, Screen, Overlay, Soft Light) with opacity control

### 🎵 Advanced Audio Analysis
- **5 Frequency Bands**: Sub-bass, bass, mid, treble, high-treble
- **Beat Detection**: Automatic bass beat and snare hit detection
- **Energy Curves**: Smooth, continuous reactivity based on frequency energy
- **Real-Time Audio Playback**: For webcam recording with synchronized effects

### 🖥️ Interactive GUI
- **Live Preview**: See effects applied instantly as you adjust settings
- **Frame Navigation**: Jump to any frame to test effects at specific moments
- **Preview Modes**: Original, Processed, or Side-by-Side comparison
- **Progress Tracking**: Real-time progress bars with informative status messages
- **Frame-by-Frame Visualization**: Watch effects being applied during processing

## 🚀 Quick Start

### 1. Installation

```bash
# Install FFmpeg (if not already installed)
brew install ffmpeg

# Create virtual environment
python3 -m venv venv

# Activate environment
source venv/bin/activate

# Install dependencies
pip install librosa numpy scipy opencv-python soundfile imageio imageio-ffmpeg PyQt5 pillow
```

### 2. Launch the GUI

```bash
source venv/bin/activate
python3 gui_preview_pyqt5.py
```

### 3. Basic Workflow

1. **Select Mode**: Choose Video, Image + Audio, Folder of Images, or Webcam
2. **Load Files**: Load your video/image(s) and audio file
3. **Wait for Analysis**: Audio analysis runs automatically (shows progress)
4. **Tweak Effects**: Adjust sliders and toggles - see results **instantly**!
5. **Preview**: Use frame slider to test different moments
6. **Process**: When satisfied, process the full video

## 📖 Documentation

- **[USER_GUIDE.md](USER_GUIDE.md)** - Comprehensive usage guide for all features
- **[ARTISTIC_EFFECTS_GUIDE.md](ARTISTIC_EFFECTS_GUIDE.md)** - Detailed guide to all artistic effects
- **[IMAGE_TO_VIDEO_GUIDE.md](IMAGE_TO_VIDEO_GUIDE.md)** - Guide for creating videos from images

## 🎯 Use Cases

- **Music Videos**: Enhance music videos with synchronized visual effects
- **Social Media Content**: Create eye-catching videos for TikTok, Instagram, YouTube
- **Live Performances**: Record yourself with real-time audio-reactive effects
- **Art Installations**: Create dynamic, modern art pieces
- **Lyric Videos**: Transform static images into engaging lyric videos
- **Event Recordings**: Add visual interest to conference talks or presentations

## 🎛️ Real-Time Controls

All controls update the preview **instantly**:

- **Zoom Factor** (1.0-2.0): Adjust zoom intensity
- **Rotation** (0-15°): Control rotation angle
- **Intensity Sensitivity** (0.0-1.0): How reactive effects are to audio
- **Smoothness** (0.0-1.0): Transition smoothness between frames
- **Effect Smoothing** (0.0-1.0): Smoothness of effect intensity changes
- **Hue Shift** (0-60°): Color shift amount
- **Artistic Effects**: Toggle any of 8 effects on/off
- **Frequency Mixing**: Adjust frequency band contributions for each effect
- **Layer Blending**: Change blend mode and opacity

**Just move a slider or toggle a checkbox - the preview updates immediately!**

## 🎨 Artistic Effects

The app includes 8 powerful artistic effects, each mapped to specific frequency bands:

1. **Pixel Sorting** - Glitch art with flowing distortions
2. **Kaleidoscope** - Symmetrical, mesmerizing patterns
3. **Wave Distortion** - Organic, water-like warping
4. **VHS Degradation** - Retro analog tape artifacts
5. **Posterization** - Bold, graphic color quantization
6. **Edge Detection** - Modern outline effects
7. **Data Corruption** - Digital error simulation
8. **CRT Scan Lines** - Retro monitor aesthetics

Each effect can be fine-tuned with frequency mixing controls to adjust how it responds to different parts of the audio spectrum.

## 🎥 Webcam Mode

Record yourself with live audio-reactive effects:

1. Select **"Webcam + Audio (Live)"** mode
2. Load your audio file
3. Wait for audio analysis
4. Click **"Start Webcam"**
5. Click **"Start Recording"** - audio playback begins automatically
6. Watch the audio progress bar to see your position in the track
7. Effects sync perfectly to the audio in real-time
8. Click **"Stop Recording"** - audio is automatically merged with video

## 📋 Requirements

- **Python 3.8+** (Python 3.10+ recommended)
- **FFmpeg** (for audio/video handling)
- **macOS** (tested on Apple Silicon M1/M2/M3/M4 Pro)
- **~2GB free disk space** (for temporary files)

## 💡 Tips for Best Results

1. **Start with defaults** - They work well for most content
2. **Use real-time preview** - Tweak settings and see results instantly
3. **Test different frames** - Use the frame slider to find interesting moments
4. **Combine effects** - Multiple effects can create stunning results
5. **Adjust frequency mixing** - Fine-tune how effects respond to your audio
6. **Preview before processing** - Use "Preview Sequence" to test 1 second first

## 🐛 Troubleshooting

**"ffmpeg not found"**
```bash
brew install ffmpeg
```

**"No module named 'PyQt5'"**
```bash
pip install PyQt5
```

**Effects not visible**
- Increase intensity sensitivity
- Enable more effects
- Check that audio has clear frequencies

**GUI not responding**
- Wait for audio analysis to complete
- Check that video/image file is valid
- Try restarting the GUI

## 📁 Project Structure

```
audio-reactive-video/
├── gui_preview_pyqt5.py          # Main GUI application
├── audio_analysis.py              # Audio frequency analysis
├── video_processor.py             # Video frame processing
├── image_to_video.py             # Image-to-video conversion
├── audio_reactive_video.py       # Command-line interface
├── custom_modals.py              # Custom dialog boxes
├── README.md                      # This file
├── USER_GUIDE.md                  # Comprehensive user guide
├── ARTISTIC_EFFECTS_GUIDE.md     # Artistic effects documentation
└── IMAGE_TO_VIDEO_GUIDE.md       # Image-to-video guide
```

## 🎬 Examples

### Video Mode
Load a video with music, adjust effects in real-time, and create a dynamic music video.

### Image + Audio Mode
Transform a single image into a full music video with all effects synchronized to the audio.

### Folder of Images + Audio
Use multiple images that transition smoothly with crossfades, all reacting to the audio.

### Webcam + Audio (Live)
Record yourself performing with real-time audio-reactive effects and synchronized audio playback.

## 📝 License

Cc-BY-NC 4.0

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Enjoy creating amazing audio-reactive videos! 🎥🎵✨**

For detailed usage instructions, see [USER_GUIDE.md](USER_GUIDE.md).
