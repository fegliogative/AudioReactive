"""
Image-to-Video Processor
Creates dynamic video from a single image and audio file
Applies all audio-reactive effects to the image based on music frequencies
"""

import cv2
import numpy as np
from typing import Dict, Optional, Tuple
from video_processor import VideoProcessor
import librosa


class ImageToVideoProcessor:
    """
    Creates video from a single image by applying audio-reactive effects
    The image becomes a dynamic canvas that reacts to music frequencies
    """
    
    def __init__(self, image_path: str, audio_path: str, fps: float = 30.0, 
                 width: Optional[int] = None, height: Optional[int] = None):
        """
        Initialize image-to-video processor
        
        Args:
            image_path: Path to input image file
            audio_path: Path to audio file (MP3, WAV, etc.)
            fps: Output video frame rate (default: 30.0)
            width: Output video width (None = use image width)
            height: Output video height (None = use image height)
        """
        self.image_path = image_path
        self.audio_path = audio_path
        self.fps = fps
        
        # Load image
        self.base_image = cv2.imread(image_path)
        if self.base_image is None:
            raise ValueError(f"Could not load image from {image_path}")
        
        # Get image dimensions
        img_h, img_w = self.base_image.shape[:2]
        
        # Set output dimensions
        if width is None:
            width = img_w
        if height is None:
            height = img_h
        
        self.width = width
        self.height = height
        
        # Resize image if needed
        if width != img_w or height != img_h:
            self.base_image = cv2.resize(self.base_image, (width, height), 
                                        interpolation=cv2.INTER_LANCZOS4)
        
        # Get audio duration
        y, sr = librosa.load(audio_path, sr=None)
        self.audio_duration = len(y) / sr
        self.total_frames = int(self.audio_duration * fps)
        
        print(f"Image loaded: {img_w}x{img_h} (output: {width}x{height})")
        print(f"Audio loaded: {self.audio_duration:.2f}s @ {sr} Hz")
        print(f"Video will have {self.total_frames} frames @ {self.fps} FPS")
        
        # Create a dummy VideoProcessor instance to reuse effect methods
        # We'll create a temporary video file for initialization
        self.effect_processor = VideoProcessor.__new__(VideoProcessor)
        self.effect_processor.fps = fps
        self.effect_processor.width = width
        self.effect_processor.height = height
        self.effect_processor.duration = self.audio_duration
        self.effect_processor.total_frames = self.total_frames
    
    def process_image_to_video(
        self,
        output_path: str,
        energy_curves: Dict[str, np.ndarray],
        frame_times: np.ndarray,
        bass_beat_frames: Optional[np.ndarray] = None,
        snare_hit_frames: Optional[np.ndarray] = None,
        # Effect parameters
        zoom_factor: float = 1.3,
        rotation_angle: float = 5.0,
        # Band contributions
        sub_bass_zoom: float = 0.2,
        bass_zoom: float = 1.0,
        treble_rotation: float = 1.0,
        high_treble_rotation: float = 0.5,
        mid_hue_shift: float = 30.0,
        # Advanced effects
        enable_color_grading: bool = True,
        enable_blur: bool = True,
        enable_brightness: bool = True,
        enable_glitch: bool = False,
        enable_artifacts: bool = False,
        # New artistic effects
        enable_pixel_sort: bool = False,
        enable_kaleidoscope: bool = False,
        enable_wave_distortion: bool = False,
        enable_vhs: bool = False,
        enable_posterization: bool = False,
        enable_edge_detection: bool = False,
        enable_data_corruption: bool = False,
        enable_scan_lines: bool = False,
        # Beat-triggered effects
        beat_triggered_zoom: bool = True,
        beat_window: float = 0.2,
        snare_triggered_flash: bool = True,
        snare_window: float = 0.15,
        # Reactivity
        intensity_sensitivity: float = 0.7,
        smoothness: float = 0.8
    ):
        """
        Process image into video with audio-reactive effects
        
        Args:
            output_path: Path to output video file
            energy_curves: Dictionary mapping band names to normalized energy curves
            frame_times: Time values for each spectrogram frame
            bass_beat_frames: Frame indices for bass beats
            snare_hit_frames: Frame indices for snare hits
            zoom_factor: Maximum zoom factor
            rotation_angle: Maximum rotation angle in degrees
            sub_bass_zoom: Sub-bass contribution to zoom
            bass_zoom: Bass contribution to zoom
            treble_rotation: Treble contribution to rotation
            high_treble_rotation: High-treble contribution to rotation
            mid_hue_shift: Maximum hue shift in degrees
            enable_color_grading: Enable color grading
            enable_blur: Enable motion blur
            enable_brightness: Enable brightness pulsing
            enable_glitch: Enable glitch effects
            enable_artifacts: Enable digital artifacts
            enable_pixel_sort: Enable pixel sorting (glitch art)
            enable_kaleidoscope: Enable kaleidoscope/mirroring
            enable_wave_distortion: Enable wave distortion
            enable_vhs: Enable VHS/analog degradation
            enable_posterization: Enable posterization
            enable_edge_detection: Enable edge detection overlay
            enable_data_corruption: Enable data corruption/moshing
            enable_scan_lines: Enable CRT scan lines
            beat_triggered_zoom: Enable beat-triggered zoom
            beat_window: Time window around beats
            snare_triggered_flash: Enable snare-triggered flash
            snare_window: Time window around snares
            intensity_sensitivity: Intensity sensitivity (0.0-1.0)
            smoothness: Smoothness factor (0.0-1.0)
        """
        print(f"Processing image to video with audio-reactive effects...")
        print(f"  Zoom factor: {zoom_factor}x")
        print(f"  Rotation angle: {rotation_angle}°")
        print(f"  Intensity sensitivity: {intensity_sensitivity:.2f}")
        print(f"  Smoothness: {smoothness:.2f}")
        print(f"  Color grading: {'ON' if enable_color_grading else 'OFF'}")
        print(f"  Blur: {'ON' if enable_blur else 'OFF'}")
        print(f"  Brightness: {'ON' if enable_brightness else 'OFF'}")
        print(f"  Glitch: {'ON' if enable_glitch else 'OFF'}")
        print(f"  Artifacts: {'ON' if enable_artifacts else 'OFF'}")
        print(f"  Pixel Sort: {'ON' if enable_pixel_sort else 'OFF'}")
        print(f"  Kaleidoscope: {'ON' if enable_kaleidoscope else 'OFF'}")
        print(f"  Wave Distortion: {'ON' if enable_wave_distortion else 'OFF'}")
        print(f"  VHS: {'ON' if enable_vhs else 'OFF'}")
        print(f"  Posterization: {'ON' if enable_posterization else 'OFF'}")
        print(f"  Edge Detection: {'ON' if enable_edge_detection else 'OFF'}")
        print(f"  Data Corruption: {'ON' if enable_data_corruption else 'OFF'}")
        print(f"  Scan Lines: {'ON' if enable_scan_lines else 'OFF'}")
        print(f"  Beat-triggered zoom: {'ON' if beat_triggered_zoom else 'OFF'}")
        print(f"  Snare-triggered flash: {'ON' if snare_triggered_flash else 'OFF'}")
        
        # Get energy curves
        sub_bass_energy = energy_curves.get('sub_bass', np.zeros(len(frame_times)))
        bass_energy = energy_curves.get('bass', np.zeros(len(frame_times)))
        mid_energy = energy_curves.get('mid', np.zeros(len(frame_times)))
        treble_energy = energy_curves.get('treble', np.zeros(len(frame_times)))
        high_treble_energy = energy_curves.get('high_treble', np.zeros(len(frame_times)))
        
        # Interpolate energy curves to video frame rate
        video_frame_times = np.linspace(0, self.audio_duration, self.total_frames)
        
        sub_bass_interp = np.interp(video_frame_times, frame_times, sub_bass_energy)
        bass_interp = np.interp(video_frame_times, frame_times, bass_energy)
        mid_interp = np.interp(video_frame_times, frame_times, mid_energy)
        treble_interp = np.interp(video_frame_times, frame_times, treble_energy)
        high_treble_interp = np.interp(video_frame_times, frame_times, high_treble_energy)
        
        # Apply smoothing
        if smoothness > 0.0:
            window_size = max(1, int(smoothness * 5))
            if window_size > 1:
                kernel = np.ones(window_size) / window_size
                sub_bass_interp = np.convolve(sub_bass_interp, kernel, mode='same')
                bass_interp = np.convolve(bass_interp, kernel, mode='same')
                mid_interp = np.convolve(mid_interp, kernel, mode='same')
                treble_interp = np.convolve(treble_interp, kernel, mode='same')
                high_treble_interp = np.convolve(high_treble_interp, kernel, mode='same')
        
        # Get beat information
        if bass_beat_frames is not None and len(bass_beat_frames) > 0:
            bass_beat_times = frame_times[bass_beat_frames]
        else:
            bass_beat_times = np.array([])
        
        if snare_hit_frames is not None and len(snare_hit_frames) > 0:
            snare_hit_times = frame_times[snare_hit_frames]
        else:
            snare_hit_times = np.array([])
        
        # Setup video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, self.fps, (self.width, self.height))
        
        # Process each frame
        for frame_idx in range(self.total_frames):
            # Get current time
            current_time = frame_idx / self.fps
            
            # Get energy values for this frame
            sub_bass_val = sub_bass_interp[frame_idx]
            bass_val = bass_interp[frame_idx]
            mid_val = mid_interp[frame_idx]
            treble_val = treble_interp[frame_idx]
            high_treble_val = high_treble_interp[frame_idx]
            
            # Start with base image
            frame = self.base_image.copy()
            
            # Calculate zoom (beat-triggered or continuous)
            if beat_triggered_zoom and len(bass_beat_times) > 0:
                time_distances = np.abs(bass_beat_times - current_time)
                nearest_beat_distance = np.min(time_distances) if len(time_distances) > 0 else float('inf')
                
                if nearest_beat_distance <= beat_window:
                    beat_proximity = 1.0 - (nearest_beat_distance / beat_window)
                    beat_proximity = np.clip(beat_proximity, 0.0, 1.0)
                    
                    bass_intensity = (sub_bass_val * sub_bass_zoom + bass_val * bass_zoom) / (sub_bass_zoom + bass_zoom + 1e-8)
                    bass_intensity = np.clip(bass_intensity, 0.0, 1.0)
                    
                    zoom_intensity = beat_proximity * 0.7 + bass_intensity * 0.3
                    zoom_intensity = (1.0 - intensity_sensitivity) + (intensity_sensitivity * zoom_intensity)
                    zoom = 1.0 + (zoom_factor - 1.0) * zoom_intensity
                else:
                    zoom = 1.0
            else:
                zoom_intensity = (sub_bass_val * sub_bass_zoom + bass_val * bass_zoom) / (sub_bass_zoom + bass_zoom + 1e-8)
                zoom_intensity = np.clip(zoom_intensity, 0.0, 1.0)
                zoom_intensity = (1.0 - intensity_sensitivity) + (intensity_sensitivity * zoom_intensity)
                zoom = 1.0 + (zoom_factor - 1.0) * zoom_intensity
            
            # Calculate rotation
            rotation_intensity = (treble_val * treble_rotation + high_treble_val * high_treble_rotation) / (treble_rotation + high_treble_rotation + 1e-8)
            rotation_intensity = np.clip(rotation_intensity, 0.0, 1.0)
            rotation_intensity = (1.0 - intensity_sensitivity) + (intensity_sensitivity * rotation_intensity)
            rotation = rotation_angle * rotation_intensity
            
            # Color grading
            hue_shift = 0.0
            saturation = 1.0
            brightness = 1.0
            
            if enable_color_grading:
                hue_shift = mid_val * mid_hue_shift
                saturation = 1.0 + treble_val * 0.3
            
            # Brightness pulse
            if enable_brightness:
                brightness = 1.0 + (bass_val + mid_val) * 0.3
            
            # Snare-triggered brightness flash
            if snare_triggered_flash and len(snare_hit_times) > 0:
                snare_time_distances = np.abs(snare_hit_times - current_time)
                nearest_snare_distance = np.min(snare_time_distances) if len(snare_time_distances) > 0 else float('inf')
                
                if nearest_snare_distance <= snare_window:
                    snare_proximity = 1.0 - (nearest_snare_distance / snare_window)
                    snare_proximity = np.clip(snare_proximity, 0.0, 1.0)
                    flash_intensity = snare_proximity * 0.8
                    brightness = brightness + flash_intensity
                    brightness = np.clip(brightness, 1.0, 2.0)
            
            # Blur
            blur_intensity = 0.0
            if enable_blur:
                blur_intensity = bass_val * 0.5
            
            # Glitch
            glitch_intensity = 0.0
            if enable_glitch:
                base_intensity = (treble_val * 0.6 + high_treble_val * 0.4)
                glitch_intensity = base_intensity * (0.5 + intensity_sensitivity * 0.5)
                glitch_intensity = np.clip(glitch_intensity, 0.0, 1.0)
            
            # Artifacts
            artifacts_intensity = 0.0
            if enable_artifacts:
                base_intensity = (treble_val * 0.5 + high_treble_val * 0.5)
                artifacts_intensity = base_intensity * (0.5 + intensity_sensitivity * 0.5)
                artifacts_intensity = np.clip(artifacts_intensity, 0.0, 1.0)
            
            # New artistic effects - mapped to different frequency bands for dynamic reactivity
            pixel_sort_intensity = 0.0
            if enable_pixel_sort:
                # Pixel sorting reacts to mid frequencies (artistic, flowing)
                base_intensity = mid_val * 0.7 + treble_val * 0.3
                pixel_sort_intensity = base_intensity * (0.5 + intensity_sensitivity * 0.5)
                pixel_sort_intensity = np.clip(pixel_sort_intensity, 0.0, 1.0)
            
            kaleidoscope_intensity = 0.0
            if enable_kaleidoscope:
                # Kaleidoscope reacts to treble (symmetrical patterns on bright sounds)
                base_intensity = (treble_val * 0.5 + high_treble_val * 0.5)
                kaleidoscope_intensity = base_intensity * (0.5 + intensity_sensitivity * 0.5)
                kaleidoscope_intensity = np.clip(kaleidoscope_intensity, 0.0, 1.0)
            
            wave_distortion_intensity = 0.0
            if enable_wave_distortion:
                # Wave distortion reacts to bass (flowing, organic)
                base_intensity = (sub_bass_val * 0.3 + bass_val * 0.7)
                wave_distortion_intensity = base_intensity * (0.5 + intensity_sensitivity * 0.5)
                wave_distortion_intensity = np.clip(wave_distortion_intensity, 0.0, 1.0)
            
            vhs_intensity = 0.0
            if enable_vhs:
                # VHS degradation reacts to overall energy (retro aesthetic)
                base_intensity = (bass_val * 0.3 + mid_val * 0.3 + treble_val * 0.4)
                vhs_intensity = base_intensity * (0.5 + intensity_sensitivity * 0.5)
                vhs_intensity = np.clip(vhs_intensity, 0.0, 1.0)
            
            posterization_intensity = 0.0
            if enable_posterization:
                # Posterization reacts to mid frequencies (graphic art)
                base_intensity = mid_val * 0.8 + treble_val * 0.2
                posterization_intensity = base_intensity * (0.5 + intensity_sensitivity * 0.5)
                posterization_intensity = np.clip(posterization_intensity, 0.0, 1.0)
            
            edge_detection_intensity = 0.0
            if enable_edge_detection:
                # Edge detection reacts to high frequencies (sharp, graphic)
                base_intensity = (treble_val * 0.4 + high_treble_val * 0.6)
                edge_detection_intensity = base_intensity * (0.5 + intensity_sensitivity * 0.5)
                edge_detection_intensity = np.clip(edge_detection_intensity, 0.0, 1.0)
            
            data_corruption_intensity = 0.0
            if enable_data_corruption:
                # Data corruption reacts to high frequencies (digital divide aesthetic)
                base_intensity = (treble_val * 0.5 + high_treble_val * 0.5)
                data_corruption_intensity = base_intensity * (0.5 + intensity_sensitivity * 0.5)
                data_corruption_intensity = np.clip(data_corruption_intensity, 0.0, 1.0)
            
            scan_lines_intensity = 0.0
            if enable_scan_lines:
                # Scan lines react to overall energy (CRT aesthetic)
                base_intensity = (bass_val * 0.2 + mid_val * 0.3 + treble_val * 0.5)
                scan_lines_intensity = base_intensity * (0.5 + intensity_sensitivity * 0.5)
                scan_lines_intensity = np.clip(scan_lines_intensity, 0.0, 1.0)
            
            # Apply effects to frame
            if (zoom != 1.0 or rotation != 0.0 or hue_shift != 0.0 or saturation != 1.0 or 
                brightness != 1.0 or blur_intensity > 0.0 or glitch_intensity > 0.0 or 
                artifacts_intensity > 0.0 or pixel_sort_intensity > 0.0 or 
                kaleidoscope_intensity > 0.0 or wave_distortion_intensity > 0.0 or
                vhs_intensity > 0.0 or posterization_intensity > 0.0 or 
                edge_detection_intensity > 0.0 or data_corruption_intensity > 0.0 or
                scan_lines_intensity > 0.0):
                frame = self.effect_processor.apply_effects(
                    frame,
                    zoom=zoom,
                    rotation=rotation,
                    hue_shift=hue_shift,
                    saturation=saturation,
                    brightness=brightness,
                    blur_intensity=blur_intensity,
                    glitch_intensity=glitch_intensity,
                    artifacts_intensity=artifacts_intensity,
                    pixel_sort_intensity=pixel_sort_intensity,
                    kaleidoscope_intensity=kaleidoscope_intensity,
                    wave_distortion_intensity=wave_distortion_intensity,
                    vhs_intensity=vhs_intensity,
                    posterization_intensity=posterization_intensity,
                    edge_detection_intensity=edge_detection_intensity,
                    data_corruption_intensity=data_corruption_intensity,
                    scan_lines_intensity=scan_lines_intensity,
                    effect_mode="direct",  # Default for CLI usage
                    blend_mode="normal",
                    layer_opacity=1.0
                )
            
            # Write frame
            out.write(frame)
            
            # Progress indicator
            if (frame_idx + 1) % 30 == 0:
                progress = (frame_idx + 1) / self.total_frames * 100
                print(f"  Processing: {progress:.1f}% ({frame_idx + 1}/{self.total_frames})")
        
        out.release()
        print(f"Image-to-video processing complete! Output saved to {output_path}")

