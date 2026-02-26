# Artistic Effects Guide

## Overview

This guide describes the new artistic effects added to the SoundReactive application, designed to create dynamic, surprising, and visually stunning results - perfect for modern art installations, digital divide aesthetics, and corrupt data visualizations.

---

## 🎨 New Artistic Effects

### 1. **Pixel Sorting** (Glitch Art)
- **Description**: Classic glitch art technique that sorts pixels by brightness to create flowing, organic distortions
- **Frequency Mapping**: Reacts to **mid frequencies** (70%) and **treble** (30%)
- **Best For**: Abstract art, glitch aesthetics, flowing distortions
- **Visual Style**: Creates smooth, wave-like distortions that flow across the image

### 2. **Kaleidoscope**
- **Description**: Creates symmetrical, mesmerizing patterns by mirroring segments of the image
- **Frequency Mapping**: Reacts to **treble** (50%) and **high-treble** (50%)
- **Best For**: Modern art installations, psychedelic visuals, symmetrical patterns
- **Visual Style**: Creates radial symmetry with 2-8 segments based on intensity

### 3. **Wave Distortion**
- **Description**: Applies sine/cosine wave warping to create flowing, organic distortions
- **Frequency Mapping**: Reacts to **sub-bass** (30%) and **bass** (70%)
- **Best For**: Organic, flowing movements, water-like effects
- **Visual Style**: Creates smooth wave patterns that ripple across the image

### 4. **VHS Degradation**
- **Description**: Simulates VHS/analog tape artifacts - scan lines, color bleeding, tape noise
- **Frequency Mapping**: Reacts to **bass** (30%), **mid** (30%), and **treble** (40%)
- **Best For**: Retro aesthetics, digital divide, nostalgic visuals
- **Visual Style**: Adds horizontal scan lines, color channel bleeding, and analog noise

### 5. **Posterization**
- **Description**: Reduces color depth artistically to create bold, graphic art aesthetic
- **Frequency Mapping**: Reacts to **mid frequencies** (80%) and **treble** (20%)
- **Best For**: Graphic design, bold visuals, artistic color quantization
- **Visual Style**: Reduces colors to 2-256 levels based on intensity, creating bold color blocks

### 6. **Edge Detection Overlay**
- **Description**: Applies Canny edge detection to create outline/contour effects
- **Frequency Mapping**: Reacts to **treble** (40%) and **high-treble** (60%)
- **Best For**: Graphic design, modern aesthetics, outline effects
- **Visual Style**: Overlays white edges on the image, creating a graphic design look

### 7. **Data Corruption**
- **Description**: Aggressive data corruption/moshing effect simulating corrupted files, digital errors
- **Frequency Mapping**: Reacts to **treble** (50%) and **high-treble** (50%)
- **Best For**: Digital divide aesthetics, error art, corrupt data visualization
- **Visual Style**: Random block corruption, shifted data blocks, channel swaps

### 8. **CRT Scan Lines**
- **Description**: Simulates old CRT monitor scan lines and subtle screen curvature
- **Frequency Mapping**: Reacts to **bass** (20%), **mid** (30%), and **treble** (50%)
- **Best For**: Retro aesthetics, digital divide, nostalgic visuals
- **Visual Style**: Horizontal scan lines with subtle barrel distortion

---

## 🎵 Frequency Band Mapping

Each effect is mapped to specific frequency bands to create dynamic, reactive visuals:

| Effect | Primary Band | Secondary Band | Tertiary Band |
|--------|-------------|----------------|---------------|
| Pixel Sorting | Mid (70%) | Treble (30%) | - |
| Kaleidoscope | Treble (50%) | High-Treble (50%) | - |
| Wave Distortion | Bass (70%) | Sub-Bass (30%) | - |
| VHS | Treble (40%) | Bass (30%) | Mid (30%) |
| Posterization | Mid (80%) | Treble (20%) | - |
| Edge Detection | High-Treble (60%) | Treble (40%) | - |
| Data Corruption | Treble (50%) | High-Treble (50%) | - |
| Scan Lines | Treble (50%) | Mid (30%) | Bass (20%) |

---

## 🎬 Effect Application Order

Effects are applied in an optimal order to preserve visual quality:

1. **Geometric Transforms** (Zoom, Rotation)
2. **Color Adjustments** (Hue, Saturation, Brightness)
3. **Artistic Effects** (Pixel Sort, Kaleidoscope, Wave Distortion)
4. **Corruption Effects** (Glitch, Data Corruption, Artifacts)
5. **Stylization** (Posterization, Edge Detection)
6. **Retro Effects** (VHS, Scan Lines)
7. **Blur** (Applied last to smooth everything)

---

## 💡 Usage Tips

### For Modern Art Installations
- Combine **Kaleidoscope** + **Pixel Sorting** + **Wave Distortion**
- Use **Posterization** for bold, graphic aesthetics
- Enable **Edge Detection** for clean, modern outlines

### For Digital Divide Aesthetics
- Combine **VHS** + **Data Corruption** + **Scan Lines**
- Use **Artifacts** for compression-like effects
- Enable **Glitch** for RGB channel separation

### For Surprising, Dynamic Results
- Enable multiple effects simultaneously
- Adjust **Intensity Sensitivity** to control reactivity
- Use **Smoothness** to control effect transitions

### Recommended Combinations

**Abstract Art**:
- Pixel Sorting + Kaleidoscope + Wave Distortion

**Retro/Digital Divide**:
- VHS + Scan Lines + Data Corruption

**Graphic Design**:
- Posterization + Edge Detection + Color Grading

**Maximum Chaos**:
- All effects enabled with high intensity sensitivity

---

## 🎛️ GUI Controls

All artistic effects can be toggled in the GUI under the "Artistic Effects" section:

- ✅ **Pixel Sorting (Glitch Art)**
- ✅ **Kaleidoscope**
- ✅ **Wave Distortion**
- ✅ **VHS Degradation**
- ✅ **Posterization**
- ✅ **Edge Detection**
- ✅ **Data Corruption**
- ✅ **CRT Scan Lines**

Each effect automatically reacts to its mapped frequency bands based on the audio analysis.

### ⚡ Real-Time Effect Tweaking

**The app responds instantly!** You can:
- **Toggle effects on/off** - See results immediately in the preview
- **Adjust frequency mixing** - Fine-tune how each effect responds to different frequency bands
- **Change intensity sensitivity** - Control overall reactivity in real-time
- **Modify effect smoothing** - Adjust transition smoothness instantly
- **Combine multiple effects** - Enable/disable effects and see combinations update live

**No need to wait for processing** - just move sliders, toggle checkboxes, and watch the preview update in near real-time. Experiment freely to find the perfect settings before rendering your final video!

---

## 🔧 Technical Details

### Intensity Calculation
All effects use the same intensity calculation formula:
```python
base_intensity = (frequency_band_contributions)
effect_intensity = base_intensity * (0.5 + intensity_sensitivity * 0.5)
effect_intensity = np.clip(effect_intensity, 0.0, 1.0)
```

This ensures:
- Effects scale smoothly with frequency energy
- Intensity sensitivity controls reactivity (0.0 = always on, 1.0 = fully reactive)
- Effects are clamped to valid range (0.0-1.0)

### Performance
- All effects are optimized for real-time preview
- Effects can be combined without significant performance impact
- Processing order optimized for visual quality

---

## 🎨 Visual Examples

### Pixel Sorting
Creates flowing, wave-like distortions that sort pixels by brightness, creating organic glitch art patterns.

### Kaleidoscope
Generates symmetrical patterns with 2-8 segments, creating mesmerizing radial symmetry effects.

### Wave Distortion
Applies smooth sine/cosine wave warping, creating flowing, water-like distortions.

### VHS Degradation
Adds horizontal scan lines, color bleeding, and analog noise for retro aesthetics.

### Posterization
Reduces color depth to create bold, graphic art with distinct color blocks.

### Edge Detection
Overlays white edge outlines, creating a modern graphic design aesthetic.

### Data Corruption
Simulates file corruption with random block shifts, noise, and channel swaps.

### CRT Scan Lines
Adds horizontal scan lines and subtle screen curvature for retro monitor aesthetics.

---

## 🚀 Getting Started

1. **Load an image** and **audio file** in the GUI
2. **Enable artistic effects** you want to use
3. **Adjust Intensity Sensitivity** to control reactivity
4. **Preview** a single frame or sequence
5. **Process** the full video when satisfied

The effects will automatically react to the audio frequencies, creating dynamic, surprising, and artistic results!

---

## 📝 Notes

- Effects can be combined for maximum visual impact
- Each effect is mapped to specific frequency bands for optimal reactivity
- Intensity sensitivity controls how strongly effects react to audio
- Smoothness controls how quickly effects transition between frames
- All effects are designed to work together harmoniously

---

Enjoy creating stunning, dynamic, and surprising audio-reactive visuals! 🎨🎵

