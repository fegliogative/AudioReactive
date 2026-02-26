# Image-to-Video Feature Guide

## 🎨 Transform Static Images into Dynamic Music Videos!

Create stunning audio-reactive videos from a single image and an MP3 file. Your image becomes a dynamic canvas that reacts to every beat, frequency, and rhythm in your music!

---

## ✨ What It Does

Takes a **single image** and an **MP3 file**, then creates a **full video** where:
- The image zooms on bass beats
- The image flashes bright on snare hits
- The image rotates with high frequencies
- Colors shift with mid-range frequencies
- Glitch and artifacts appear on treble
- All effects are synchronized to the music

**Result**: A professional music video from just one image!

---

## 🚀 Quick Start

### CLI Usage

```bash
# Basic image-to-video
python3 audio_reactive_video.py image.jpg output.mp4 --audio song.mp3 --image-mode

# With enhanced effects
python3 audio_reactive_video.py image.jpg output.mp4 --audio song.mp3 --image-mode \
  --enhanced --zoom 1.5 --rotation 8 --enable-color-grading --enable-blur

# Custom resolution and frame rate
python3 audio_reactive_video.py image.jpg output.mp4 --audio song.mp3 --image-mode \
  --width 1920 --height 1080 --fps 30
```

### GUI Usage

1. Launch GUI: `python3 gui_preview.py`
2. Select **"Image + Audio"** mode (radio button)
3. Click **"Load Image"** → Select your image
4. Click **"Load Audio"** → Select your MP3
5. Wait for audio analysis to complete
6. Adjust effects using sliders
7. Preview different frames using the slider
8. Click **"Process Image to Video"** when ready

---

## 📋 Supported Formats

### Images
- PNG, JPG/JPEG, BMP, TIFF, WEBP
- Any resolution (will be resized if needed)

### Audio
- MP3, WAV, M4A, AAC, FLAC
- Any sample rate (automatically handled)

### Output
- MP4 video with original audio

---

## 🎛️ Parameters

### Image Mode Specific
- `--image-mode`: Enable image-to-video mode
- `--audio`: Path to audio file (required in image mode)
- `--fps`: Output video frame rate (default: 30.0)
- `--width`: Output video width (default: image width)
- `--height`: Output video height (default: image height)

### Effect Parameters (Same as Video Mode)
- `--zoom`: Zoom factor (1.0-2.0+)
- `--rotation`: Rotation angle (0-15°+)
- `--enable-color-grading`: Color shifts
- `--enable-blur`: Motion blur
- `--enable-brightness`: Brightness pulsing
- `--enable-glitch`: Glitch effects
- `--enable-artifacts`: Digital artifacts
- `--intensity-sensitivity`: Reactivity (0.0-1.0)
- `--smoothness`: Smoothness (0.0-1.0)

---

## 🎬 How It Works

### Process Flow

```
1. Load Image
   ↓
2. Load Audio
   ↓
3. Analyze Audio Frequencies
   - Detect bass beats
   - Detect snare hits
   - Analyze 5 frequency bands
   ↓
4. Generate Video Frames
   - For each frame in audio duration:
     - Start with base image
     - Apply effects based on audio at that moment
     - Zoom on bass beats
     - Flash on snare hits
     - Rotate with treble
     - Color shift with mid-range
     - Glitch/artifacts on high frequencies
   ↓
5. Merge with Audio
   ↓
6. Output Video
```

### Frame Generation

Each video frame is created by:
1. Starting with the original image
2. Calculating audio energy at that moment
3. Applying all enabled effects
4. Writing the processed frame

The image is **never modified** - effects are applied per-frame, creating dynamic movement!

---

## 🎨 Use Cases

### 1. **Album Artwork Videos**
- Use album cover as image
- Create dynamic music video
- Perfect for streaming platforms

### 2. **Lyric Videos**
- Use text/image as base
- Add audio-reactive effects
- Create engaging lyric videos

### 3. **Social Media Content**
- Single image + song
- Create eye-catching videos
- Perfect for Instagram, TikTok, YouTube Shorts

### 4. **Art Showcases**
- Showcase artwork with music
- Create gallery-style videos
- Add dynamic movement to static art

### 5. **Logo Animations**
- Company logo + music
- Create branded content
- Professional presentations

---

## 💡 Tips for Best Results

### Image Selection
- **High Resolution**: Use high-res images for best quality
- **Centered Subject**: Works best with centered compositions
- **Good Contrast**: High contrast images show effects better
- **Avoid Text**: Text can become hard to read with effects

### Audio Selection
- **Clear Beats**: Works best with clear bass and snare
- **Good Mix**: Balanced frequency content
- **Strong Rhythm**: Clear rhythmic structure

### Effect Settings
- **Moderate Zoom**: 1.3-1.6 for subtle, 1.6-2.0 for dramatic
- **Subtle Rotation**: 3-8° for professional look
- **Enable Color Grading**: Adds depth and interest
- **Test First**: Use GUI to preview before full processing

---

## 🎵 Example Commands

### Electronic/EDM
```bash
python3 audio_reactive_video.py cover.jpg output.mp4 --audio track.mp3 --image-mode \
  --enhanced --zoom 1.6 --rotation 10 --enable-color-grading --enable-glitch \
  --intensity-sensitivity 0.8
```

### Hip-Hop/Rap
```bash
python3 audio_reactive_video.py artwork.jpg output.mp4 --audio song.mp3 --image-mode \
  --enhanced --zoom 1.5 --rotation 6 --enable-brightness --intensity-sensitivity 0.7
```

### Pop/Rock
```bash
python3 audio_reactive_video.py photo.jpg output.mp4 --audio track.mp3 --image-mode \
  --enhanced --zoom 1.4 --rotation 5 --enable-color-grading --mid-hue-shift 40
```

### Ambient/Chill
```bash
python3 audio_reactive_video.py image.jpg output.mp4 --audio ambient.mp3 --image-mode \
  --enhanced --zoom 1.2 --rotation 3 --smoothness 1.0 --intensity-sensitivity 0.6
```

---

## 📊 Technical Details

### Video Generation
- **Frame Rate**: 30 FPS (configurable)
- **Resolution**: Image resolution (configurable)
- **Duration**: Matches audio duration exactly
- **Quality**: High quality, no compression artifacts

### Effect Application
- **Per-Frame**: Each frame calculated independently
- **Real-Time**: Effects based on audio at that moment
- **Smooth**: Interpolation ensures smooth transitions
- **Synchronized**: Perfect sync with audio

### Performance
- **Processing Time**: ~2-5 minutes per minute of audio
- **Memory Usage**: Minimal (processes frame by frame)
- **Output Size**: Depends on resolution and duration

---

## 🎯 Advantages Over Video Mode

### Image Mode Benefits
- ✅ **No Video Needed**: Just need image + audio
- ✅ **Perfect Sync**: Every frame matches audio exactly
- ✅ **Consistent Quality**: No video compression artifacts
- ✅ **Flexible Resolution**: Choose any output size
- ✅ **Faster Setup**: No video editing required
- ✅ **Creative Freedom**: Any image works

### When to Use Image Mode
- Creating music videos from artwork
- Making lyric videos
- Social media content creation
- Logo animations
- Art showcases

### When to Use Video Mode
- You already have a video
- You want to enhance existing footage
- You need specific video content
- You want to preserve video motion

---

## 🔧 Advanced Usage

### Custom Resolution
```bash
# 4K output
python3 audio_reactive_video.py image.jpg output.mp4 --audio song.mp3 --image-mode \
  --width 3840 --height 2160

# Square format (Instagram)
python3 audio_reactive_video.py image.jpg output.mp4 --audio song.mp3 --image-mode \
  --width 1080 --height 1080

# Vertical format (TikTok, YouTube Shorts)
python3 audio_reactive_video.py image.jpg output.mp4 --audio song.mp3 --image-mode \
  --width 1080 --height 1920
```

### Custom Frame Rate
```bash
# 60 FPS for smooth motion
python3 audio_reactive_video.py image.jpg output.mp4 --audio song.mp3 --image-mode \
  --fps 60

# 24 FPS for cinematic look
python3 audio_reactive_video.py image.jpg output.mp4 --audio song.mp3 --image-mode \
  --fps 24
```

---

## 🎬 Workflow Example

### Creating a Music Video from Album Art

1. **Prepare Files**
   - Album cover image (high resolution)
   - Song MP3 file

2. **Launch GUI**
   ```bash
   python3 gui_preview.py
   ```

3. **Load Files**
   - Select "Image + Audio" mode
   - Load image: `cover.jpg`
   - Load audio: `song.mp3`
   - Wait for analysis

4. **Preview & Adjust**
   - Use frame slider to preview different moments
   - Adjust zoom, rotation, effects
   - Enable color grading, blur, etc.
   - Test with "Preview Frame"

5. **Process**
   - Click "Process Image to Video"
   - Wait for completion
   - Output: `music_video.mp4`

6. **Result**
   - Professional music video
   - Perfect audio sync
   - Dynamic, engaging visuals

---

## 🎨 Creative Ideas

### 1. **Multi-Image Sequences**
- Process multiple images separately
- Combine in video editor
- Create image transitions

### 2. **Text Overlays**
- Add text to image first
- Process with effects
- Text moves with music

### 3. **Layered Effects**
- Process same image multiple times
- Different effect settings
- Layer in video editor

### 4. **Color Variations**
- Process with different hue shifts
- Create color variations
- Use in transitions

---

## ⚡ Performance Tips

1. **Resolution**: Lower resolution = faster processing
2. **Frame Rate**: 30 FPS is usually sufficient
3. **Effects**: Fewer effects = faster processing
4. **Test First**: Use GUI preview before full processing

---

## 🐛 Troubleshooting

### "Audio file not found"
- Ensure `--audio` parameter is provided
- Check file path is correct
- Verify file format is supported

### "Could not load image"
- Check image format is supported
- Verify file is not corrupted
- Try a different image file

### Effects not visible
- Increase intensity sensitivity
- Enable more effects
- Check audio has clear frequencies

### Output video is too large
- Reduce output resolution
- Use lower frame rate
- Compress output separately

---

## 🎉 Summary

The **Image-to-Video** feature transforms the app into a powerful music video generator:

- ✅ **Simple**: Just image + audio
- ✅ **Powerful**: All effects available
- ✅ **Flexible**: Custom resolution, frame rate
- ✅ **Professional**: High-quality output
- ✅ **Creative**: Endless possibilities

**Perfect for creating stunning music videos from any image!** 🎥🎵✨

