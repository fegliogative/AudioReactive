# SoundReactive - Complete User Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Understanding the Interface](#understanding-the-interface)
3. [Input Modes](#input-modes)
4. [Effect Controls](#effect-controls)
5. [Real-Time Preview](#real-time-preview)
6. [Processing Videos](#processing-videos)
7. [Tips & Best Practices](#tips--best-practices)

---

## Getting Started

### First Time Setup

1. **Install FFmpeg** (if not already installed):
   ```bash
   brew install ffmpeg
   ```

2. **Create and activate virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install librosa numpy scipy opencv-python soundfile imageio imageio-ffmpeg PyQt5 pillow
   ```

4. **Launch the application**:
   ```bash
   python3 gui_preview_pyqt5.py
   ```

### Basic Workflow

1. Select your input mode (Video, Image + Audio, Folder, or Webcam)
2. Load your files (video/image(s) and audio)
3. Wait for audio analysis to complete
4. Adjust effects and see results **instantly**
5. Preview different frames
6. Process the full video when satisfied

---

## Understanding the Interface

### Main Window Layout

The GUI is divided into three main sections:

1. **Left Panel (Controls)**: All effect controls, sliders, and settings
2. **Right Panel (Preview)**: Video/image preview with progress information
3. **Header**: Logo and application title

### Left Panel Sections

- **File Controls**: Mode selection and file loading
- **Basic Effects**: Zoom, rotation, frame navigation
- **Advanced Effects**: Intensity, smoothness, color grading, blur, brightness, hue
- **Layer Blending**: Blend modes and opacity
- **Artistic Effects**: 8 artistic effects with frequency mixing controls
- **Action Buttons**: Preview and process buttons

### Right Panel Sections

- **Preview Mode Selection**: Original, Processed, or Side-by-Side
- **Preview Display**: Shows current frame with effects
- **Progress Bar**: Shows processing progress
- **Audio Progress Bar**: Shows audio position during webcam recording
- **Status Bar**: Current status and information

---

## Input Modes

### 1. Video Mode

**Best for**: Enhancing existing videos with audio-reactive effects

**Steps**:
1. Select "Video" radio button
2. Click "Load Video" and select your MP4 file
3. Audio is automatically extracted and analyzed
4. Wait for "Ready" status
5. Adjust effects and preview
6. Click "Process Full Video"

**Supported Formats**: MP4, AVI, MOV (MP4 recommended)

### 2. Image + Audio Mode

**Best for**: Creating music videos from a single image

**Steps**:
1. Select "Image + Audio" radio button
2. Click "Load Image" and select your image file
3. Click "Load Audio" and select your audio file
4. Wait for audio analysis
5. Adjust effects and preview different frames
6. Click "Process Image to Video"

**Supported Formats**:
- Images: PNG, JPG, JPEG, BMP, TIFF, WEBP
- Audio: MP3, WAV, M4A, AAC, FLAC

### 3. Folder of Images + Audio Mode

**Best for**: Creating videos from multiple images with smooth transitions

**Steps**:
1. Select "Folder of Images + Audio" radio button
2. Click "Load Image Folder" and select a folder containing images
3. Click "Load Audio" and select your audio file
4. Wait for audio analysis
5. Images are automatically resized to consistent size
6. Each image gets proportional duration based on audio length
7. Smooth crossfade transitions between images
8. Adjust effects and preview
9. Click "Process Folder to Video"

**Image Requirements**:
- All images in the folder will be used
- Images are automatically resized to match the first image
- Supported formats: PNG, JPG, JPEG, BMP, TIFF, WEBP

### 4. Webcam + Audio (Live) Mode

**Best for**: Recording yourself with real-time audio-reactive effects

**Steps**:
1. Select "Webcam + Audio (Live)" radio button
2. Click "Load Audio" and select your audio file
3. Wait for audio analysis
4. Click "Start Webcam"
5. Click "Start Recording" - choose output location
6. **Audio playback begins automatically** - you'll hear the track
7. Watch the **audio progress bar** to see your position
8. Effects sync perfectly to the audio in real-time
9. Click "Stop Recording" when done
10. Audio is automatically merged with the video

**Features**:
- Real-time audio playback during recording
- Audio progress bar shows position in track
- Loop indicator shows when audio repeats
- Effects sync to actual audio playback position
- Audio automatically merged with final video

---

## Effect Controls

### ⚡ Real-Time Updates

**All controls update the preview instantly!** Move any slider, toggle any checkbox, and see the results immediately. No need to wait for processing - experiment freely.

### Basic Effects

**Zoom Factor** (1.0 - 2.0)
- Controls how much the image zooms on bass beats
- Default: 1.3 (30% zoom)
- Higher values = more dramatic zoom

**Rotation** (0° - 15°)
- Controls rotation angle for treble frequencies
- Default: 5°
- Higher values = more rotation

**Frame Navigation**
- Use slider to jump to any frame
- Preview updates instantly when you move the slider
- Shows current frame number and time

### Advanced Effects

**Intensity Sensitivity** (0.0 - 1.0)
- Controls how reactive effects are to audio intensity
- Default: 0.7
- Lower (0.3-0.5) = subtle, always-on effects
- Higher (0.8-1.0) = very reactive, only on strong frequencies

**Smoothness** (0.0 - 1.0)
- Controls transition smoothness between frames
- Default: 0.8
- Lower = more responsive, sharper transitions
- Higher = smoother, more gradual transitions

**Effect Smoothing** (0.0 - 1.0)
- Controls smoothness of effect intensity changes
- Default: 0.3
- Prevents jarring effect changes
- Higher = smoother effect transitions

**Color Grading** (Checkbox)
- Enables frequency-based color grading
- Colors shift based on mid-range frequencies
- Toggle on/off to see difference instantly

**Blur** (Checkbox)
- Enables motion blur on strong bass hits
- Adds cinematic motion blur effect
- Toggle on/off to see difference instantly

**Brightness** (Checkbox)
- Enables brightness pulsing with frequency energy
- Image gets brighter with stronger frequencies
- Toggle on/off to see difference instantly

**Hue Shift** (0° - 60°)
- Controls color shift amount
- Default: 0° (no shift)
- Higher values = more color variation

### Layer Blending

**Blend Mode** (Dropdown)
- **Direct**: No blending (default)
- **Multiply**: Darkens image
- **Screen**: Brightens image
- **Overlay**: Combines multiply and screen
- **Soft Light**: Subtle blending effect

**Opacity** (0.0 - 1.0)
- Controls blend opacity
- Only enabled when blend mode is not "Direct"
- Lower = more transparent
- Higher = more opaque

### Artistic Effects

**8 Artistic Effects** (Checkboxes)
Each can be toggled on/off instantly:
- Pixel Sorting (Glitch Art)
- Kaleidoscope
- Wave Distortion
- VHS Degradation
- Posterization
- Edge Detection
- Data Corruption
- CRT Scan Lines

**Frequency Mixing** (Per Effect)
Each artistic effect has 5 sliders to control frequency band contributions:
- **Sub-Bass** (20-60 Hz): Deep bass frequencies
- **Bass** (60-250 Hz): Kick drums, bass guitar
- **Mid** (250-2000 Hz): Vocals, most instruments
- **Treble** (2000-6000 Hz): Cymbals, bright instruments
- **High-Treble** (6000-12000 Hz): High hats, sibilance

**Adjust these sliders to fine-tune how each effect responds to different parts of the audio spectrum!**

---

## Real-Time Preview

### Preview Modes

**Original**: Shows unprocessed frame (no effects)
**Processed**: Shows frame with all effects applied
**Side-by-Side**: Shows both original and processed for comparison

Switch between modes to see the difference instantly!

### Frame Navigation

- Use the frame slider to jump to any moment
- Preview updates immediately when you move the slider
- Shows frame number and time position
- Perfect for testing effects at specific moments

### Instant Updates

**Everything updates in real-time:**
- Move any slider → Preview updates
- Toggle any checkbox → Preview updates
- Change blend mode → Preview updates
- Adjust frequency mixing → Preview updates
- Navigate frames → Preview updates

**No waiting, no processing - just instant feedback!**

---

## Processing Videos

### Preview Options

**Preview Frame**
- Applies current effects to the selected frame
- Updates instantly when you change settings
- Perfect for testing effects

**Preview Sequence (1 sec)**
- Generates a 1-second preview video
- Shows effects over time
- Great for testing before full processing
- Includes progress bar and status messages

**Process Full Video**
- Processes entire video with current settings
- Shows detailed progress with status messages
- Frame-by-frame visualization during processing
- Saves final video with audio merged

### Progress Tracking

During processing, you'll see:
- **Progress Bar**: Percentage complete
- **Status Messages**: Informative and engaging messages about what's happening
- **Frame Preview**: Live frame-by-frame visualization (for image modes)
- **Time Estimates**: Approximate time remaining

### Output Files

- **Video Mode**: Output video with audio merged
- **Image Mode**: Video created from image with audio merged
- **Folder Mode**: Video with crossfaded images and audio merged
- **Webcam Mode**: Recording with audio merged (if audio was loaded)

---

## Tips & Best Practices

### General Tips

1. **Start with defaults** - They work well for most content
2. **Use real-time preview** - Tweak settings and see results instantly
3. **Test different frames** - Use frame slider to find interesting moments
4. **Preview before processing** - Use "Preview Sequence" to test 1 second first
5. **Combine effects** - Multiple effects can create stunning results
6. **Adjust frequency mixing** - Fine-tune how effects respond to your audio

### Effect Combinations

**Abstract Art**:
- Pixel Sorting + Kaleidoscope + Wave Distortion
- High intensity sensitivity (0.8-1.0)

**Retro/Digital Divide**:
- VHS + Scan Lines + Data Corruption
- Moderate intensity (0.6-0.7)

**Graphic Design**:
- Posterization + Edge Detection + Color Grading
- Lower intensity (0.5-0.6)

**Maximum Impact**:
- All effects enabled
- High intensity sensitivity (0.9-1.0)
- Moderate smoothness (0.6-0.8)

### Parameter Guidelines

**Zoom Factor**:
- 1.0: No zoom
- 1.2: Subtle (20% zoom)
- 1.3: Moderate (30% zoom) - **Recommended**
- 1.5: Strong (50% zoom)
- 2.0: Very dramatic (100% zoom)

**Rotation**:
- 0°: No rotation
- 3°: Subtle rotation
- 5°: Moderate rotation - **Recommended**
- 8°: Strong rotation
- 15°+: Very dramatic rotation

**Intensity Sensitivity**:
- 0.3-0.5: Subtle, always-on effects
- 0.6-0.8: Balanced reactivity - **Recommended**
- 0.9-1.0: Very reactive, only on strong frequencies

**Smoothness**:
- 0.0-0.5: More responsive, sharper transitions
- 0.7-1.0: Smoother, more gradual transitions - **Recommended**

### Audio Tips

- **Clear beats work best** - Music with clear bass and snare
- **Good frequency balance** - Music with content across all frequency bands
- **Strong rhythm** - Clear rhythmic structure enhances effects
- **Test different tracks** - Different music styles produce different results

### Image Tips (Image + Audio Mode)

- **High resolution** - Use high-res images for best quality
- **Centered subject** - Works best with centered compositions
- **Good contrast** - High contrast images show effects better
- **Avoid text** - Text can become hard to read with effects

### Webcam Recording Tips

- **Good lighting** - Better lighting = better results
- **Stable position** - Stay relatively still for best effect visibility
- **Watch audio progress** - Use progress bar to know where you are
- **Test first** - Do a short test recording before the full take
- **Audio sync** - Effects sync perfectly to the audio playback

---

## Troubleshooting

### Common Issues

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
- Try different frames (some moments have more audio activity)

**Preview not updating**
- Wait for audio analysis to complete
- Check that files are loaded correctly
- Try restarting the application

**Audio not playing (Webcam mode)**
- Check that audio file is loaded
- Verify audio file format is supported
- Check system audio settings

**Processing is slow**
- Reduce video resolution
- Use lower frame rate
- Process shorter segments
- Close other applications

**Output video has no audio**
- Check that audio file was loaded
- Verify audio file is valid
- Check FFmpeg installation

---

## Advanced Usage

### Frequency Mixing

Each artistic effect has frequency mixing controls. Adjust these to:
- Make effects respond more to bass (lower sliders)
- Make effects respond more to treble (higher sliders)
- Create unique combinations for each effect
- Match effects to your music style

### Layer Blending

Experiment with different blend modes:
- **Multiply**: Great for darkening and adding depth
- **Screen**: Brightens and adds glow effects
- **Overlay**: Combines both for dramatic results
- **Soft Light**: Subtle, professional blending

### Effect Smoothing

Adjust effect smoothing to:
- Prevent jarring effect changes (increase smoothing)
- Make effects more responsive (decrease smoothing)
- Create different visual styles

---

## Keyboard Shortcuts

Currently, the application is primarily mouse-driven. All controls are accessible via the GUI interface.

---

## Getting Help

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all dependencies are installed
3. Ensure FFmpeg is properly installed
4. Check that input files are valid
5. Try with different files to isolate the issue

---

**Enjoy creating amazing audio-reactive videos! 🎥🎵✨**

For more information on artistic effects, see [ARTISTIC_EFFECTS_GUIDE.md](ARTISTIC_EFFECTS_GUIDE.md).
