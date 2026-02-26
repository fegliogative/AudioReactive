"""
Video Processing Module
Applies zoom, rotation, and advanced visual effects to video frames based on audio analysis
Enhanced with intensity-based effects, color grading, blur, and smooth interpolation
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict, Optional


class VideoProcessor:
    """
    Processes video frames with dynamic effects based on audio frequency analysis
    Supports multiple frequency bands, intensity-based scaling, and advanced visual effects
    """
    
    def __init__(self, video_path: str):
        """
        Initialize video processor
        
        Args:
            video_path: Path to input video file
        """
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        
        # Get video properties
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.total_frames / self.fps
        
        print(f"Video loaded: {self.width}x{self.height} @ {self.fps} FPS")
        print(f"Total frames: {self.total_frames}, Duration: {self.duration:.2f}s")
    
    def time_to_frame(self, time_seconds: float) -> int:
        """Convert time in seconds to frame index"""
        return int(time_seconds * self.fps)
    
    def frame_to_time(self, frame_idx: int) -> float:
        """Convert frame index to time in seconds"""
        return frame_idx / self.fps
    
    # ==================== Smooth Interpolation Functions ====================
    
    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        """
        Smooth S-curve interpolation (ease-in-out cubic)
        Creates natural acceleration and deceleration
        
        Args:
            t: Progress value (0.0 to 1.0)
            
        Returns:
            Interpolated value (0.0 to 1.0)
        """
        if t < 0.0:
            return 0.0
        if t > 1.0:
            return 1.0
        return t * t * (3.0 - 2.0 * t)
    
    @staticmethod
    def ease_out_cubic(t: float) -> float:
        """
        Fast start, slow end (ease-out cubic)
        Good for quick reactions that fade smoothly
        
        Args:
            t: Progress value (0.0 to 1.0)
            
        Returns:
            Interpolated value (0.0 to 1.0)
        """
        if t < 0.0:
            return 0.0
        if t > 1.0:
            return 1.0
        return 1.0 - pow(1.0 - t, 3)
    
    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        """
        Gentle quadratic interpolation
        Smoother than linear, less dramatic than cubic
        
        Args:
            t: Progress value (0.0 to 1.0)
            
        Returns:
            Interpolated value (0.0 to 1.0)
        """
        if t < 0.0:
            return 0.0
        if t > 1.0:
            return 1.0
        if t < 0.5:
            return 2 * t * t
        return 1 - pow(-2 * t + 2, 2) / 2
    
    # ==================== Basic Effects ====================
    
    def zoom_frame(self, frame: np.ndarray, zoom_factor: float) -> np.ndarray:
        """
        Apply zoom effect to a frame
        
        Args:
            frame: Input frame
            zoom_factor: Zoom factor (1.0 = no zoom, 1.5 = 50% zoom in)
            
        Returns:
            Zoomed frame
        """
        if zoom_factor <= 1.0:
            return frame
        
        h, w = frame.shape[:2]
        
        # Calculate crop region
        crop_h = int(h / zoom_factor)
        crop_w = int(w / zoom_factor)
        
        # Center crop
        start_y = (h - crop_h) // 2
        start_x = (w - crop_w) // 2
        
        cropped = frame[start_y:start_y + crop_h, start_x:start_x + crop_w]
        
        # Resize back to original dimensions
        zoomed = cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)
        
        return zoomed
    
    def rotate_frame(self, frame: np.ndarray, angle_degrees: float) -> np.ndarray:
        """
        Apply rotation effect to a frame
        
        Args:
            frame: Input frame
            angle_degrees: Rotation angle in degrees
            
        Returns:
            Rotated frame
        """
        if abs(angle_degrees) < 0.01:
            return frame
        
        h, w = frame.shape[:2]
        center = (w // 2, h // 2)
        
        # Get rotation matrix
        rotation_matrix = cv2.getRotationMatrix2D(center, angle_degrees, 1.0)
        
        # Apply rotation
        rotated = cv2.warpAffine(
            frame, rotation_matrix, (w, h),
            borderMode=cv2.BORDER_REFLECT,
            flags=cv2.INTER_LINEAR
        )
        
        return rotated
    
    # ==================== Advanced Visual Effects ====================
    
    def apply_color_grade(
        self,
        frame: np.ndarray,
        hue_shift: float = 0.0,
        saturation_mult: float = 1.0,
        brightness_mult: float = 1.0
    ) -> np.ndarray:
        """
        Apply color grading effects (hue shift, saturation, brightness)
        
        Args:
            frame: Input frame (BGR format)
            hue_shift: Hue shift in degrees (0-180, wraps around)
            saturation_mult: Saturation multiplier (1.0 = no change, >1.0 = more saturated)
            brightness_mult: Brightness multiplier (1.0 = no change, >1.0 = brighter)
            
        Returns:
            Color-graded frame
        """
        if hue_shift == 0.0 and saturation_mult == 1.0 and brightness_mult == 1.0:
            return frame
        
        # Convert BGR to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
        
        # Shift hue (OpenCV uses 0-179 for hue)
        if hue_shift != 0.0:
            hsv[:, :, 0] = (hsv[:, :, 0] + hue_shift) % 180
        
        # Adjust saturation
        if saturation_mult != 1.0:
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * saturation_mult, 0, 255)
        
        # Adjust brightness (value channel)
        if brightness_mult != 1.0:
            hsv[:, :, 2] = np.clip(hsv[:, :, 2] * brightness_mult, 0, 255)
        
        # Convert back to BGR
        hsv = hsv.astype(np.uint8)
        graded = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        return graded
    
    def apply_motion_blur(self, frame: np.ndarray, intensity: float) -> np.ndarray:
        """
        Apply motion blur effect based on intensity
        
        Args:
            frame: Input frame
            intensity: Blur intensity (0.0 = no blur, 1.0 = maximum blur)
            
        Returns:
            Blurred frame
        """
        if intensity <= 0.0:
            return frame
        
        # Calculate kernel size (must be odd)
        kernel_size = int(1 + intensity * 15)
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        if kernel_size <= 1:
            return frame
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)
        
        return blurred
    
    def apply_brightness_pulse(self, frame: np.ndarray, intensity: float) -> np.ndarray:
        """
        Apply brightness pulsing effect
        
        Args:
            frame: Input frame
            intensity: Pulse intensity (0.0 = no change, 1.0 = maximum brightness)
            
        Returns:
            Brightened frame
        """
        if intensity <= 0.0:
            return frame
        
        # Brightness multiplier (1.0 to 1.5 for subtle to strong pulse)
        brightness_mult = 1.0 + intensity * 0.5
        
        return self.apply_color_grade(frame, brightness_mult=brightness_mult)
    
    def apply_glitch_effect(self, frame: np.ndarray, intensity: float) -> np.ndarray:
        """
        Apply glitch effect - digital artifacts and distortions for high frequencies
        
        Args:
            frame: Input frame
            intensity: Glitch intensity (0.0 = no glitch, 1.0 = maximum glitch)
            
        Returns:
            Glitched frame
        """
        if intensity <= 0.0:
            return frame
        
        h, w = frame.shape[:2]
        glitched = frame.copy()
        
        # Random horizontal shifts (RGB channel separation)
        if intensity > 0.3:
            shift_amount = int(intensity * 20)
            # Shift red channel
            red_channel = glitched[:, :, 2].copy()
            shift_x = np.random.randint(-shift_amount, shift_amount + 1)
            if shift_x != 0:
                M = np.float32([[1, 0, shift_x], [0, 1, 0]])
                shifted_red = cv2.warpAffine(red_channel, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
                glitched[:, :, 2] = shifted_red
        
        # Random vertical slices (data corruption effect)
        if intensity > 0.5:
            num_slices = int(intensity * 10)
            for _ in range(num_slices):
                slice_y = np.random.randint(0, h)
                slice_height = np.random.randint(1, int(intensity * 20) + 1)
                slice_x = np.random.randint(0, max(1, w - 50))
                slice_width = np.random.randint(10, 50)
                
                # Randomly shift or duplicate slice
                if np.random.random() > 0.5:
                    # Shift slice
                    shift = np.random.randint(-20, 21)
                    if 0 <= slice_x + shift < w - slice_width:
                        glitched[slice_y:slice_y+slice_height, slice_x:slice_x+slice_width] = \
                            glitched[slice_y:slice_y+slice_height, slice_x+shift:slice_x+shift+slice_width]
                else:
                    # Duplicate slice
                    glitched[slice_y:slice_y+slice_height, slice_x:slice_x+slice_width] = \
                        glitched[slice_y:slice_y+slice_height, slice_x:slice_x+slice_width]
        
        # Chromatic aberration (color separation)
        if intensity > 0.4:
            aberration = int(intensity * 5)
            # Shift channels slightly
            b, g, r = cv2.split(glitched)
            
            # Shift green channel
            M_g = np.float32([[1, 0, -aberration], [0, 1, 0]])
            g_shifted = cv2.warpAffine(g, M_g, (w, h), borderMode=cv2.BORDER_REPLICATE)
            
            # Shift blue channel
            M_b = np.float32([[1, 0, aberration], [0, 1, 0]])
            b_shifted = cv2.warpAffine(b, M_b, (w, h), borderMode=cv2.BORDER_REPLICATE)
            
            glitched = cv2.merge([b_shifted, g_shifted, r])
        
        return glitched
    
    def apply_artifacts_effect(self, frame: np.ndarray, intensity: float) -> np.ndarray:
        """
        Apply digital artifacts effect - compression artifacts and noise for high frequencies
        
        Args:
            frame: Input frame
            intensity: Artifacts intensity (0.0 = no artifacts, 1.0 = maximum artifacts)
            
        Returns:
            Frame with artifacts
        """
        if intensity <= 0.0:
            return frame
        
        h, w = frame.shape[:2]
        artifacted = frame.copy().astype(np.float32)
        
        # Compression-like block artifacts (JPEG-like quantization)
        if intensity > 0.2:
            # Block size increases with intensity (more compression = larger blocks)
            block_size = int(4 + intensity * 12)  # 4-16 pixel blocks
            # Probability of affecting a block increases with intensity
            block_probability = 0.2 + intensity * 0.6  # 20% to 80% of blocks
            
            for y in range(0, h, block_size):
                for x in range(0, w, block_size):
                    if np.random.random() < block_probability:
                        # Get block bounds
                        end_y = min(y + block_size, h)
                        end_x = min(x + block_size, w)
                        block = artifacted[y:end_y, x:end_x]
                        
                        # Quantize colors (reduce color depth)
                        # Higher intensity = more quantization (fewer color levels)
                        quantize_levels = max(2, int(256 / (1 + intensity * 15)))  # 256 to ~16 levels
                        quantize_step = 256 / quantize_levels
                        
                        # Quantize each channel
                        quantized = (block / quantize_step).astype(np.int32) * quantize_step
                        quantized = np.clip(quantized, 0, 255)
                        artifacted[y:end_y, x:end_x] = quantized
        
        # Add digital noise (compression artifacts)
        if intensity > 0.15:
            # Noise intensity scales with effect intensity
            noise_amount = intensity * 25  # 0 to 25 pixel value variation
            noise = np.random.normal(0, noise_amount, (h, w, 3))
            artifacted = artifacted + noise
            artifacted = np.clip(artifacted, 0, 255)
        
        # Scan lines (horizontal compression artifacts)
        if intensity > 0.3:
            num_lines = int(2 + intensity * 8)  # 2-10 lines
            for _ in range(num_lines):
                line_y = np.random.randint(0, max(1, h - 3))
                line_height = np.random.randint(1, 4)
                # Create horizontal banding (compression artifact)
                if np.random.random() > 0.5:
                    # Darken line (data loss)
                    artifacted[line_y:line_y+line_height, :] *= 0.7
                else:
                    # Brighten line (quantization error)
                    artifacted[line_y:line_y+line_height, :] = np.clip(artifacted[line_y:line_y+line_height, :] * 1.3, 0, 255)
        
        # Color banding (reduced color depth artifact)
        if intensity > 0.4:
            # Reduce color depth globally
            color_levels = max(8, int(256 / (1 + intensity * 8)))  # 256 to ~32 levels
            color_step = 256 / color_levels
            artifacted = (artifacted / color_step).astype(np.int32) * color_step
        
        # Convert back to uint8
        artifacted = np.clip(artifacted, 0, 255).astype(np.uint8)
        
        # Subtle pixelation (only at very high intensity)
        if intensity > 0.7:
            pixel_size = int(2 + (intensity - 0.7) * 2)  # 2-3 pixels at max
            if pixel_size > 1:
                small_w = max(1, w // pixel_size)
                small_h = max(1, h // pixel_size)
                small = cv2.resize(artifacted, (small_w, small_h), interpolation=cv2.INTER_NEAREST)
                artifacted = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
        
        return artifacted
    
    # ==================== Artistic Effects ====================
    
    def apply_pixel_sorting(self, frame: np.ndarray, intensity: float) -> np.ndarray:
        """
        Apply pixel sorting effect - classic glitch art technique
        Sorts pixels by brightness/color to create flowing, organic distortions
        
        Args:
            frame: Input frame
            intensity: Sorting intensity (0.0 = no sorting, 1.0 = maximum sorting)
            
        Returns:
            Pixel-sorted frame
        """
        if intensity <= 0.0:
            return frame
        
        h, w = frame.shape[:2]
        sorted_frame = frame.copy()
        
        # Convert to HSV for better brightness-based sorting
        hsv = cv2.cvtColor(sorted_frame, cv2.COLOR_BGR2HSV)
        
        # Number of rows/columns to sort based on intensity
        # Scale more gradually: 0.0 = 0 strips, 0.1 = 1 strip, 1.0 = 15 strips
        num_strips = max(1, int(intensity * 15))  # 0-15 strips, minimum 1 if intensity > 0
        
        # At very low intensity, reduce the number of strips even more
        if intensity < 0.3:
            num_strips = max(1, int(intensity * 5))  # 0.1 = 1 strip, 0.2 = 1 strip, 0.3 = 1 strip
        
        # Randomly choose horizontal or vertical sorting
        if np.random.random() > 0.5:
            # Horizontal pixel sorting (sort rows)
            strip_height = h // max(1, num_strips)
            for i in range(num_strips):
                y_start = i * strip_height
                y_end = min((i + 1) * strip_height, h)
                
                if y_end - y_start < 2:
                    continue
                
                # Get strip
                strip = sorted_frame[y_start:y_end, :].copy()
                strip_hsv = hsv[y_start:y_end, :].copy()
                
                # Sort pixels by brightness (V channel) within each column
                # At lower intensity, only sort a percentage of columns
                columns_to_sort = max(1, int(w * min(1.0, intensity * 3.0)))  # Scale columns with intensity
                if columns_to_sort < w:
                    column_indices = np.random.choice(w, columns_to_sort, replace=False)
                else:
                    column_indices = range(w)
                
                for x in column_indices:
                    column = strip[:, x]
                    column_hsv = strip_hsv[:, x]
                    
                    # Get brightness values
                    brightness = column_hsv[:, 2]
                    
                    # Create sorting indices based on brightness
                    sort_indices = np.argsort(brightness)
                    
                    # Apply sorting
                    sorted_column = column[sort_indices]
                    sorted_frame[y_start:y_end, x] = sorted_column
        else:
            # Vertical pixel sorting (sort columns)
            strip_width = w // max(1, num_strips)
            for i in range(num_strips):
                x_start = i * strip_width
                x_end = min((i + 1) * strip_width, w)
                
                if x_end - x_start < 2:
                    continue
                
                # Get strip
                strip = sorted_frame[:, x_start:x_end].copy()
                strip_hsv = hsv[:, x_start:x_end].copy()
                
                # Sort pixels by brightness within each row
                # At lower intensity, only sort a percentage of rows
                rows_to_sort = max(1, int(h * min(1.0, intensity * 3.0)))  # Scale rows with intensity
                if rows_to_sort < h:
                    row_indices = np.random.choice(h, rows_to_sort, replace=False)
                else:
                    row_indices = range(h)
                
                for y in row_indices:
                    row = strip[y, :]
                    row_hsv = strip_hsv[y, :]
                    
                    # Get brightness values
                    brightness = row_hsv[:, 2]
                    
                    # Create sorting indices
                    sort_indices = np.argsort(brightness)
                    
                    # Apply sorting
                    sorted_row = row[sort_indices]
                    sorted_frame[y, x_start:x_end] = sorted_row
        
        return sorted_frame
    
    def apply_kaleidoscope(self, frame: np.ndarray, intensity: float) -> np.ndarray:
        """
        Apply kaleidoscope/mirroring effect - creates symmetrical, mesmerizing patterns
        Perfect for modern art installation aesthetics
        
        Args:
            frame: Input frame
            intensity: Kaleidoscope intensity (0.0 = no effect, 1.0 = full mirroring)
            
        Returns:
            Kaleidoscoped frame
        """
        if intensity <= 0.0:
            return frame
        
        h, w = frame.shape[:2]
        center_x, center_y = w // 2, h // 2
        
        # Number of segments (2-8 segments based on intensity)
        num_segments = int(2 + intensity * 6)
        
        # Create output frame
        kaleidoscope = np.zeros_like(frame)
        
        # Get one segment (slice of the image)
        segment_angle = 360.0 / num_segments
        
        # Create a mask for the segment
        for i in range(num_segments):
            angle = i * segment_angle
            
            # Create rotation matrix
            M = cv2.getRotationMatrix2D((center_x, center_y), angle, 1.0)
            
            # Rotate the original frame
            rotated = cv2.warpAffine(frame, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
            
            # Create mask for this segment
            mask = np.zeros((h, w), dtype=np.uint8)
            points = np.array([
                [center_x, center_y],
                [center_x + w, center_y],
                [center_x + int(w * np.cos(np.radians(angle + segment_angle))), 
                 center_y + int(w * np.sin(np.radians(angle + segment_angle)))]
            ], dtype=np.int32)
            cv2.fillPoly(mask, [points], 255)
            
            # Apply segment to output
            for c in range(3):
                kaleidoscope[:, :, c] = np.where(mask > 0, rotated[:, :, c], kaleidoscope[:, :, c])
        
        # Blend with original based on intensity
        blend_factor = intensity * 0.7  # Max 70% kaleidoscope, 30% original
        result = cv2.addWeighted(frame, 1.0 - blend_factor, kaleidoscope, blend_factor, 0)
        
        return result
    
    def apply_wave_distortion(self, frame: np.ndarray, intensity: float) -> np.ndarray:
        """
        Apply wave distortion effect - sine/cosine wave warping
        Creates flowing, organic distortions
        
        Args:
            frame: Input frame
            intensity: Wave intensity (0.0 = no distortion, 1.0 = maximum distortion)
            
        Returns:
            Wave-distorted frame
        """
        if intensity <= 0.0:
            return frame
        
        h, w = frame.shape[:2]
        
        # Create coordinate grids
        x = np.arange(w, dtype=np.float32)
        y = np.arange(h, dtype=np.float32)
        X, Y = np.meshgrid(x, y)
        
        # Wave parameters based on intensity
        wave_amplitude = intensity * 30  # Max 30 pixels displacement
        wave_frequency = 0.02 + intensity * 0.05  # Wave frequency
        
        # Create wave distortions
        # Horizontal waves
        wave_x = X + wave_amplitude * np.sin(Y * wave_frequency + np.random.random() * np.pi)
        wave_y = Y + wave_amplitude * 0.5 * np.cos(X * wave_frequency + np.random.random() * np.pi)
        
        # Remap image using wave distortion
        map_x = wave_x.astype(np.float32)
        map_y = wave_y.astype(np.float32)
        
        distorted = cv2.remap(frame, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        
        return distorted
    
    def apply_vhs_degradation(self, frame: np.ndarray, intensity: float) -> np.ndarray:
        """
        Apply VHS/analog degradation effect - scan lines, color bleeding, tape artifacts
        Perfect for retro/digital divide aesthetics
        
        Args:
            frame: Input frame
            intensity: VHS intensity (0.0 = no effect, 1.0 = maximum degradation)
            
        Returns:
            VHS-degraded frame
        """
        if intensity <= 0.0:
            return frame
        
        h, w = frame.shape[:2]
        vhs_frame = frame.copy().astype(np.float32)
        
        # Scan lines (horizontal lines)
        if intensity > 0.2:
            num_lines = int(2 + intensity * 15)  # 2-17 lines
            line_spacing = h // (num_lines + 1)
            
            for i in range(1, num_lines + 1):
                line_y = i * line_spacing
                line_height = max(1, int(intensity * 3))
                
                # Darken scan lines
                vhs_frame[line_y:line_y+line_height, :] *= 0.6
        
        # Color bleeding (chromatic aberration)
        if intensity > 0.3:
            bleed_amount = int(intensity * 8)
            b, g, r = cv2.split(vhs_frame)
            
            # Shift channels to create color bleeding
            M_r = np.float32([[1, 0, bleed_amount], [0, 1, 0]])
            M_b = np.float32([[1, 0, -bleed_amount], [0, 1, 0]])
            
            r_shifted = cv2.warpAffine(r, M_r, (w, h), borderMode=cv2.BORDER_REPLICATE)
            b_shifted = cv2.warpAffine(b, M_b, (w, h), borderMode=cv2.BORDER_REPLICATE)
            
            vhs_frame = cv2.merge([b_shifted, g, r_shifted])
        
        # Tape noise (random noise)
        if intensity > 0.4:
            noise_amount = intensity * 20
            noise = np.random.normal(0, noise_amount, (h, w, 3))
            vhs_frame = vhs_frame + noise
        
        # Color saturation reduction (VHS color loss)
        if intensity > 0.5:
            hsv = cv2.cvtColor(vhs_frame.astype(np.uint8), cv2.COLOR_BGR2HSV)
            hsv[:, :, 1] = hsv[:, :, 1] * (1.0 - intensity * 0.3)  # Reduce saturation
            vhs_frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR).astype(np.float32)
        
        # Convert back to uint8
        vhs_frame = np.clip(vhs_frame, 0, 255).astype(np.uint8)
        
        return vhs_frame
    
    def apply_posterization(self, frame: np.ndarray, intensity: float) -> np.ndarray:
        """
        Apply posterization effect - reduce color depth artistically
        Creates bold, graphic art aesthetic
        
        Args:
            frame: Input frame
            intensity: Posterization intensity (0.0 = no effect, 1.0 = maximum quantization)
            
        Returns:
            Posterized frame
        """
        if intensity <= 0.0:
            return frame
        
        # Number of color levels (fewer levels = more posterization)
        # High intensity = fewer levels (more artistic)
        num_levels = max(2, int(256 / (1 + intensity * 20)))  # 256 to ~12 levels
        
        # Quantize each channel
        posterized = frame.copy()
        
        for c in range(3):
            channel = posterized[:, :, c]
            # Create quantization levels
            step = 256 / num_levels
            quantized = (channel / step).astype(np.uint8) * step
            quantized = np.clip(quantized, 0, 255)
            posterized[:, :, c] = quantized
        
        return posterized
    
    def apply_edge_detection_overlay(self, frame: np.ndarray, intensity: float) -> np.ndarray:
        """
        Apply edge detection overlay - creates outline/contour effects
        Modern, graphic design aesthetic
        
        Args:
            frame: Input frame
            intensity: Edge detection intensity (0.0 = no overlay, 1.0 = full overlay)
            
        Returns:
            Frame with edge detection overlay
        """
        if intensity <= 0.0:
            return frame
        
        # Convert to grayscale for edge detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Canny edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Convert edges to BGR
        edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        # Invert edges (white edges on black background)
        edges_bgr = 255 - edges_bgr
        
        # Blend with original
        blend_factor = intensity * 0.4  # Max 40% overlay
        result = cv2.addWeighted(frame, 1.0 - blend_factor, edges_bgr, blend_factor, 0)
        
        return result
    
    def apply_data_corruption(self, frame: np.ndarray, intensity: float) -> np.ndarray:
        """
        Apply aggressive data corruption/moshing effect
        Simulates corrupted data, file errors, digital divide
        
        Args:
            frame: Input frame
            intensity: Corruption intensity (0.0 = no corruption, 1.0 = maximum corruption)
            
        Returns:
            Corrupted frame
        """
        if intensity <= 0.0:
            return frame
        
        h, w = frame.shape[:2]
        corrupted = frame.copy()
        
        # Random block corruption
        if intensity > 0.1:
            # Scale more gradually: 0.1 = 1-2 blocks, 1.0 = 20 blocks
            num_blocks = max(1, int(intensity * 20))  # 1-20 blocks
            
            for _ in range(num_blocks):
                block_size = int(10 + intensity * 40)  # 10-50 pixels
                x = np.random.randint(0, max(1, w - block_size))
                y = np.random.randint(0, max(1, h - block_size))
                
                # Random corruption type
                corruption_type = np.random.random()
                
                if corruption_type < 0.3:
                    # Random noise block
                    noise = np.random.randint(0, 256, (block_size, block_size, 3), dtype=np.uint8)
                    corrupted[y:y+block_size, x:x+block_size] = noise
                elif corruption_type < 0.6:
                    # Shifted block (data misalignment)
                    shift_x = np.random.randint(-block_size, block_size)
                    shift_y = np.random.randint(-block_size, block_size)
                    src_x = np.clip(x + shift_x, 0, w - block_size)
                    src_y = np.clip(y + shift_y, 0, h - block_size)
                    corrupted[y:y+block_size, x:x+block_size] = \
                        corrupted[src_y:src_y+block_size, src_x:src_x+block_size]
                else:
                    # Color channel swap
                    block = corrupted[y:y+block_size, x:x+block_size].copy()
                    b, g, r = cv2.split(block)
                    # Random channel swap
                    channels = [b, g, r]
                    np.random.shuffle(channels)
                    corrupted[y:y+block_size, x:x+block_size] = cv2.merge(channels)
        
        # Horizontal data corruption lines
        if intensity > 0.4:
            num_lines = int(2 + intensity * 8)
            for _ in range(num_lines):
                line_y = np.random.randint(0, h)
                line_height = max(1, int(intensity * 15))
                line_width = np.random.randint(w // 4, w)
                line_x = np.random.randint(0, max(1, w - line_width))
                
                # Corrupt line with shifted data
                shift = np.random.randint(-50, 51)
                src_x = np.clip(line_x + shift, 0, w - line_width)
                corrupted[line_y:line_y+line_height, line_x:line_x+line_width] = \
                    corrupted[line_y:line_y+line_height, src_x:src_x+line_width]
        
        return corrupted
    
    def apply_scan_lines_crt(self, frame: np.ndarray, intensity: float) -> np.ndarray:
        """
        Apply CRT monitor scan lines effect
        Retro digital divide aesthetic
        
        Args:
            frame: Input frame
            intensity: Scan line intensity (0.0 = no effect, 1.0 = maximum effect)
            
        Returns:
            Frame with CRT scan lines
        """
        if intensity <= 0.0:
            return frame
        
        h, w = frame.shape[:2]
        crt_frame = frame.copy().astype(np.float32)
        
        # Create scan line pattern (every other line darker)
        scan_line_spacing = max(2, int(3 - intensity * 2))  # 3-1 pixel spacing
        
        for y in range(0, h, scan_line_spacing * 2):
            line_end = min(y + scan_line_spacing, h)
            # Darken scan lines
            crt_frame[y:line_end, :] *= (0.7 - intensity * 0.3)  # 0.7 to 0.4 brightness
        
        # Add slight curvature (CRT screen curve)
        if intensity > 0.5:
            # Subtle barrel distortion
            center_x, center_y = w / 2, h / 2
            x = np.arange(w, dtype=np.float32) - center_x
            y = np.arange(h, dtype=np.float32) - center_y
            X, Y = np.meshgrid(x, y)
            
            # Barrel distortion
            r = np.sqrt(X**2 + Y**2)
            max_r = np.sqrt(center_x**2 + center_y**2)
            distortion = 1.0 + intensity * 0.1 * (r / max_r)**2
            
            map_x = (X / distortion + center_x).astype(np.float32)
            map_y = (Y / distortion + center_y).astype(np.float32)
            
            crt_frame = cv2.remap(crt_frame.astype(np.uint8), map_x, map_y, 
                                 cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE).astype(np.float32)
        
        # Convert back to uint8
        crt_frame = np.clip(crt_frame, 0, 255).astype(np.uint8)
        
        return crt_frame
    
    # ==================== Layer Blending ====================
    
    def blend_layers(self, base: np.ndarray, overlay: np.ndarray, mode: str = "normal", opacity: float = 1.0) -> np.ndarray:
        """
        Blend two layers using various blending modes
        
        Args:
            base: Base layer (original image)
            overlay: Overlay layer (effects layer)
            mode: Blending mode (normal, multiply, screen, overlay, soft_light, hard_light, etc.)
            opacity: Opacity of overlay layer (0.0-1.0)
            
        Returns:
            Blended result
        """
        if opacity <= 0.0:
            return base
        
        # Convert to float for calculations
        base_f = base.astype(np.float32) / 255.0
        overlay_f = overlay.astype(np.float32) / 255.0
        
        if mode == "normal":
            result = overlay_f * opacity + base_f * (1.0 - opacity)
        elif mode == "multiply":
            result = base_f * overlay_f * opacity + base_f * (1.0 - opacity)
        elif mode == "screen":
            result = (1.0 - (1.0 - base_f) * (1.0 - overlay_f)) * opacity + base_f * (1.0 - opacity)
        elif mode == "overlay":
            mask = base_f < 0.5
            result = np.where(mask, 
                            2.0 * base_f * overlay_f,
                            1.0 - 2.0 * (1.0 - base_f) * (1.0 - overlay_f))
            result = result * opacity + base_f * (1.0 - opacity)
        elif mode == "soft_light":
            result = np.where(base_f < 0.5,
                            base_f - (1.0 - 2.0 * overlay_f) * base_f * (1.0 - base_f),
                            base_f + (2.0 * overlay_f - 1.0) * (np.sqrt(base_f) - base_f))
            result = result * opacity + base_f * (1.0 - opacity)
        elif mode == "hard_light":
            mask = overlay_f < 0.5
            result = np.where(mask,
                            2.0 * base_f * overlay_f,
                            1.0 - 2.0 * (1.0 - base_f) * (1.0 - overlay_f))
            result = result * opacity + base_f * (1.0 - opacity)
        elif mode == "color_dodge":
            result = np.minimum(1.0, base_f / (1.0 - overlay_f + 1e-8))
            result = result * opacity + base_f * (1.0 - opacity)
        elif mode == "color_burn":
            result = 1.0 - np.minimum(1.0, (1.0 - base_f) / (overlay_f + 1e-8))
            result = result * opacity + base_f * (1.0 - opacity)
        elif mode == "darken":
            result = np.minimum(base_f, overlay_f) * opacity + base_f * (1.0 - opacity)
        elif mode == "lighten":
            result = np.maximum(base_f, overlay_f) * opacity + base_f * (1.0 - opacity)
        elif mode == "difference":
            result = np.abs(base_f - overlay_f) * opacity + base_f * (1.0 - opacity)
        elif mode == "exclusion":
            result = (base_f + overlay_f - 2.0 * base_f * overlay_f) * opacity + base_f * (1.0 - opacity)
        else:
            # Default to normal
            result = overlay_f * opacity + base_f * (1.0 - opacity)
        
        # Convert back to uint8
        result = np.clip(result * 255.0, 0, 255).astype(np.uint8)
        return result
    
    # ==================== Combined Effects ====================
    
    def apply_effects(
        self,
        frame: np.ndarray,
        zoom: float = 1.0,
        rotation: float = 0.0,
        hue_shift: float = 0.0,
        saturation: float = 1.0,
        brightness: float = 1.0,
        blur_intensity: float = 0.0,
        glitch_intensity: float = 0.0,
        artifacts_intensity: float = 0.0,
        # New artistic effects
        pixel_sort_intensity: float = 0.0,
        kaleidoscope_intensity: float = 0.0,
        wave_distortion_intensity: float = 0.0,
        vhs_intensity: float = 0.0,
        posterization_intensity: float = 0.0,
        edge_detection_intensity: float = 0.0,
        data_corruption_intensity: float = 0.0,
        scan_lines_intensity: float = 0.0,
        # Layer blending parameters
        effect_mode: str = "direct",
        blend_mode: str = "normal",
        layer_opacity: float = 1.0
    ) -> np.ndarray:
        """
        Apply all effects to a frame in optimal order
        
        Args:
            frame: Input frame
            zoom: Zoom factor
            rotation: Rotation angle in degrees
            hue_shift: Hue shift in degrees
            saturation: Saturation multiplier
            brightness: Brightness multiplier
            blur_intensity: Blur intensity (0.0-1.0)
            glitch_intensity: Glitch effect intensity (0.0-1.0)
            artifacts_intensity: Artifacts effect intensity (0.0-1.0)
            pixel_sort_intensity: Pixel sorting intensity (0.0-1.0)
            kaleidoscope_intensity: Kaleidoscope intensity (0.0-1.0)
            wave_distortion_intensity: Wave distortion intensity (0.0-1.0)
            vhs_intensity: VHS degradation intensity (0.0-1.0)
            posterization_intensity: Posterization intensity (0.0-1.0)
            edge_detection_intensity: Edge detection overlay intensity (0.0-1.0)
            data_corruption_intensity: Data corruption intensity (0.0-1.0)
            scan_lines_intensity: CRT scan lines intensity (0.0-1.0)
            effect_mode: "direct" to apply effects directly, "layer" to apply as overlay layer
            blend_mode: Blending mode for layer mode (normal, multiply, screen, overlay, etc.)
            layer_opacity: Opacity of effects layer (0.0-1.0)
            
        Returns:
            Processed frame
        """
        # Store original for layer blending BEFORE any transforms
        original_frame = frame.copy() if effect_mode == "layer" else None
        
        # Optimal effect order for best visual results:
        # 1. Geometric transforms (zoom, rotation)
        # 2. Color adjustments (hue, saturation, brightness)
        # 3. Artistic effects (pixel sort, kaleidoscope, wave distortion)
        # 4. Corruption effects (glitch, data corruption, artifacts)
        # 5. Stylization (posterization, edge detection)
        # 6. Retro effects (VHS, scan lines)
        # 7. Blur (last, to smooth everything)
        
        # Apply geometric transforms to both original (for blending) and effect frame
        if effect_mode == "layer" and original_frame is not None:
            # Transform original frame for proper alignment
            original_transformed = self.zoom_frame(original_frame, zoom)
            original_transformed = self.rotate_frame(original_transformed, rotation)
        else:
            original_transformed = None
        
        frame = self.zoom_frame(frame, zoom)
        frame = self.rotate_frame(frame, rotation)
        frame = self.apply_color_grade(frame, hue_shift, saturation, brightness)
        
        # Artistic effects (applied early to preserve detail)
        if pixel_sort_intensity > 0.0:
            frame = self.apply_pixel_sorting(frame, pixel_sort_intensity)
        
        if kaleidoscope_intensity > 0.0:
            frame = self.apply_kaleidoscope(frame, kaleidoscope_intensity)
        
        if wave_distortion_intensity > 0.0:
            frame = self.apply_wave_distortion(frame, wave_distortion_intensity)
        
        # Corruption effects
        if glitch_intensity > 0.0:
            frame = self.apply_glitch_effect(frame, glitch_intensity)
        
        if data_corruption_intensity > 0.0:
            frame = self.apply_data_corruption(frame, data_corruption_intensity)
        
        if artifacts_intensity > 0.0:
            frame = self.apply_artifacts_effect(frame, artifacts_intensity)
        
        # Stylization
        if posterization_intensity > 0.0:
            frame = self.apply_posterization(frame, posterization_intensity)
        
        if edge_detection_intensity > 0.0:
            frame = self.apply_edge_detection_overlay(frame, edge_detection_intensity)
        
        # Retro effects
        if vhs_intensity > 0.0:
            frame = self.apply_vhs_degradation(frame, vhs_intensity)
        
        if scan_lines_intensity > 0.0:
            frame = self.apply_scan_lines_crt(frame, scan_lines_intensity)
        
        # Blur last
        if blur_intensity > 0.0:
            frame = self.apply_motion_blur(frame, blur_intensity)
        
        # Apply layer blending if in layer mode
        if effect_mode == "layer" and original_transformed is not None:
            frame = self.blend_layers(original_transformed, frame, blend_mode, layer_opacity)
        
        return frame
    
    # ==================== Legacy Processing (Backward Compatible) ====================
    
    def process_video(
        self,
        output_path: str,
        bass_frames: List[int],
        treble_frames: List[int],
        frame_times: np.ndarray,
        zoom_factor: float = 1.3,
        rotation_angle: float = 5.0,
        effect_duration: float = 0.5
    ):
        """
        Process video with effects based on audio analysis (legacy method)
        
        Args:
            output_path: Path to output video
            bass_frames: Frame indices for bass drum hits (in spectrogram frames)
            treble_frames: Frame indices for treble peaks (in spectrogram frames)
            frame_times: Time values for each spectrogram frame
            zoom_factor: Zoom factor for bass effects
            rotation_angle: Rotation angle in degrees for treble effects
            effect_duration: Duration of each effect in seconds
        """
        print(f"Processing video with effects...")
        print(f"  Zoom factor: {zoom_factor}x")
        print(f"  Rotation angle: {rotation_angle}°")
        print(f"  Effect duration: {effect_duration}s")
        
        # Convert spectrogram frames to video frames and times
        bass_times = frame_times[bass_frames]
        treble_times = frame_times[treble_frames]
        
        effect_frames = int(effect_duration * self.fps)
        
        # Create effect map for each video frame
        effect_map = {}  # frame_idx -> (zoom, rotation)
        
        # Map bass effects (zoom)
        for bass_time in bass_times:
            start_frame = self.time_to_frame(bass_time)
            for i in range(effect_frames):
                frame_idx = start_frame + i
                if frame_idx < self.total_frames:
                    # Interpolate zoom with smooth curve
                    progress = i / effect_frames
                    eased_progress = self.ease_in_out_cubic(progress)
                    
                    if progress < 0.5:
                        zoom = 1.0 + (zoom_factor - 1.0) * (eased_progress * 2)
                    else:
                        zoom = zoom_factor + (1.0 - zoom_factor) * ((eased_progress - 0.5) * 2)
                    
                    if frame_idx not in effect_map:
                        effect_map[frame_idx] = (zoom, 0.0)
                    else:
                        current_zoom, current_rotation = effect_map[frame_idx]
                        effect_map[frame_idx] = (max(zoom, current_zoom), current_rotation)
        
        # Map treble effects (rotation)
        for treble_time in treble_times:
            start_frame = self.time_to_frame(treble_time)
            for i in range(effect_frames):
                frame_idx = start_frame + i
                if frame_idx < self.total_frames:
                    # Interpolate rotation with smooth curve
                    progress = i / effect_frames
                    eased_progress = self.ease_in_out_cubic(progress)
                    
                    if progress < 0.5:
                        rotation = rotation_angle * (eased_progress * 2)
                    else:
                        rotation = rotation_angle * ((1 - eased_progress) * 2)
                    
                    if frame_idx not in effect_map:
                        effect_map[frame_idx] = (1.0, rotation)
                    else:
                        current_zoom, current_rotation = effect_map[frame_idx]
                        effect_map[frame_idx] = (current_zoom, current_rotation + rotation)
        
        # Setup video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, self.fps, (self.width, self.height))
        
        # Process frames
        frame_idx = 0
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Get effects for this frame
            zoom, rotation = effect_map.get(frame_idx, (1.0, 0.0))
            
            # Apply effects
            if zoom != 1.0 or rotation != 0.0:
                frame = self.apply_effects(frame, zoom=zoom, rotation=rotation)
            
            # Write frame
            out.write(frame)
            
            # Progress indicator
            if (frame_idx + 1) % 30 == 0:
                progress = (frame_idx + 1) / self.total_frames * 100
                print(f"  Processing: {progress:.1f}% ({frame_idx + 1}/{self.total_frames})")
            
            frame_idx += 1
        
        self.cap.release()
        out.release()
        print(f"Video processing complete! Output saved to {output_path}")
    
    # ==================== Enhanced Processing (New Method) ====================
    
    def process_video_enhanced(
        self,
        output_path: str,
        energy_curves: Dict[str, np.ndarray],
        frame_times: np.ndarray,
        bass_beat_frames: Optional[np.ndarray] = None,
        snare_hit_frames: Optional[np.ndarray] = None,
        # Effect parameters
        zoom_factor: float = 1.3,
        rotation_angle: float = 5.0,
        # Band contributions (how much each band affects effects)
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
        # Beat-triggered effects
        beat_triggered_zoom: bool = True,
        beat_window: float = 0.2,  # Seconds around beat to trigger zoom
        snare_triggered_flash: bool = True,
        snare_window: float = 0.15,  # Seconds around snare to trigger flash
        # Intensity sensitivity (how much to scale effects by intensity)
        intensity_sensitivity: float = 0.7,
        # Smoothness (interpolation curve strength)
        smoothness: float = 0.8
    ):
        """
        Enhanced video processing with continuous frequency reactivity
        
        Args:
            output_path: Path to output video
            energy_curves: Dictionary mapping band names to normalized energy curves (0.0-1.0)
            frame_times: Time values for each spectrogram frame
            zoom_factor: Maximum zoom factor for bass effects
            rotation_angle: Maximum rotation angle in degrees for treble effects
            sub_bass_zoom: Contribution of sub-bass to zoom (0.0-1.0)
            bass_zoom: Contribution of bass to zoom (0.0-1.0)
            treble_rotation: Contribution of treble to rotation (0.0-1.0)
            high_treble_rotation: Contribution of high-treble to rotation (0.0-1.0)
            mid_hue_shift: Maximum hue shift in degrees for mid-range
            enable_color_grading: Enable frequency-based color grading
            enable_blur: Enable motion blur on bass
            enable_brightness: Enable brightness pulsing
            enable_glitch: Enable glitch effects on high frequencies
            enable_artifacts: Enable digital artifacts on high frequencies
            beat_triggered_zoom: If True, zoom only triggers on detected beats (bass peaks)
            beat_window: Time window around beats to trigger zoom (seconds)
            snare_triggered_flash: If True, brightness flash triggers on detected snare hits
            snare_window: Time window around snares to trigger flash (seconds)
            intensity_sensitivity: How sensitive effects are to intensity (0.0-1.0)
            smoothness: Interpolation smoothness (0.0=linear, 1.0=very smooth)
        """
        print(f"Processing video with enhanced effects...")
        print(f"  Zoom factor: {zoom_factor}x")
        print(f"  Rotation angle: {rotation_angle}°")
        print(f"  Intensity sensitivity: {intensity_sensitivity:.2f}")
        print(f"  Smoothness: {smoothness:.2f}")
        print(f"  Color grading: {'ON' if enable_color_grading else 'OFF'}")
        print(f"  Blur: {'ON' if enable_blur else 'OFF'}")
        print(f"  Brightness: {'ON' if enable_brightness else 'OFF'}")
        print(f"  Glitch: {'ON' if enable_glitch else 'OFF'}")
        print(f"  Artifacts: {'ON' if enable_artifacts else 'OFF'}")
        print(f"  Beat-triggered zoom: {'ON' if beat_triggered_zoom else 'OFF'}")
        print(f"  Snare-triggered flash: {'ON' if snare_triggered_flash else 'OFF'}")
        
        # Get beat information if available
        if bass_beat_frames is not None and len(bass_beat_frames) > 0:
            bass_beat_times = frame_times[bass_beat_frames]
        else:
            bass_beat_times = np.array([])
        
        # Get snare information if available
        if snare_hit_frames is not None and len(snare_hit_frames) > 0:
            snare_hit_times = frame_times[snare_hit_frames]
        else:
            snare_hit_times = np.array([])
        
        # Get energy curves for each band
        sub_bass_energy = energy_curves.get('sub_bass', np.zeros(len(frame_times)))
        bass_energy = energy_curves.get('bass', np.zeros(len(frame_times)))
        mid_energy = energy_curves.get('mid', np.zeros(len(frame_times)))
        treble_energy = energy_curves.get('treble', np.zeros(len(frame_times)))
        high_treble_energy = energy_curves.get('high_treble', np.zeros(len(frame_times)))
        
        # Interpolate energy curves to video frame rate
        # (spectrogram frames may not match video frames exactly)
        video_frame_times = np.linspace(0, self.duration, self.total_frames)
        
        # Interpolate each energy curve to video frame times
        sub_bass_interp = np.interp(video_frame_times, frame_times, sub_bass_energy)
        bass_interp = np.interp(video_frame_times, frame_times, bass_energy)
        mid_interp = np.interp(video_frame_times, frame_times, mid_energy)
        treble_interp = np.interp(video_frame_times, frame_times, treble_energy)
        high_treble_interp = np.interp(video_frame_times, frame_times, high_treble_energy)
        
        # Apply smoothing to energy curves for more natural transitions
        if smoothness > 0.0:
            # Simple moving average for smoothing
            window_size = max(1, int(smoothness * 5))
            if window_size > 1:
                kernel = np.ones(window_size) / window_size
                sub_bass_interp = np.convolve(sub_bass_interp, kernel, mode='same')
                bass_interp = np.convolve(bass_interp, kernel, mode='same')
                mid_interp = np.convolve(mid_interp, kernel, mode='same')
                treble_interp = np.convolve(treble_interp, kernel, mode='same')
                high_treble_interp = np.convolve(high_treble_interp, kernel, mode='same')
        
        # Setup video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, self.fps, (self.width, self.height))
        
        # Process frames
        frame_idx = 0
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Get energy values for this frame
            sub_bass_val = sub_bass_interp[frame_idx]
            bass_val = bass_interp[frame_idx]
            mid_val = mid_interp[frame_idx]
            treble_val = treble_interp[frame_idx]
            high_treble_val = high_treble_interp[frame_idx]
            
            # Calculate effect intensities (combine bands with contributions)
            # Zoom: beat-triggered or continuous
            current_time = frame_idx / self.fps
            
            if beat_triggered_zoom and len(bass_beat_times) > 0:
                # Beat-triggered zoom: only activate near detected beats
                # Find nearest beat
                time_distances = np.abs(bass_beat_times - current_time)
                nearest_beat_distance = np.min(time_distances) if len(time_distances) > 0 else float('inf')
                
                if nearest_beat_distance <= beat_window:
                    # Within beat window - calculate zoom based on distance from beat
                    # Closer to beat = stronger zoom
                    beat_proximity = 1.0 - (nearest_beat_distance / beat_window)
                    beat_proximity = np.clip(beat_proximity, 0.0, 1.0)
                    
                    # Also scale by bass energy at this moment
                    bass_intensity = (sub_bass_val * sub_bass_zoom + bass_val * bass_zoom) / (sub_bass_zoom + bass_zoom + 1e-8)
                    bass_intensity = np.clip(bass_intensity, 0.0, 1.0)
                    
                    # Combine beat proximity with bass intensity
                    zoom_intensity = beat_proximity * 0.7 + bass_intensity * 0.3
                    zoom_intensity = (1.0 - intensity_sensitivity) + (intensity_sensitivity * zoom_intensity)
                    
                    zoom = 1.0 + (zoom_factor - 1.0) * zoom_intensity
                else:
                    # Not near any beat - no zoom
                    zoom = 1.0
            else:
                # Continuous zoom: scale with bass energy
                zoom_intensity = (sub_bass_val * sub_bass_zoom + bass_val * bass_zoom) / (sub_bass_zoom + bass_zoom + 1e-8)
                zoom_intensity = np.clip(zoom_intensity, 0.0, 1.0)
                
                # Apply intensity sensitivity (blend between full effect and intensity-scaled)
                zoom_intensity = (1.0 - intensity_sensitivity) + (intensity_sensitivity * zoom_intensity)
                
                # Calculate zoom factor (scale from 1.0 to zoom_factor)
                zoom = 1.0 + (zoom_factor - 1.0) * zoom_intensity
            
            # Rotation: combination of treble and high-treble
            rotation_intensity = (treble_val * treble_rotation + high_treble_val * high_treble_rotation) / (treble_rotation + high_treble_rotation + 1e-8)
            rotation_intensity = np.clip(rotation_intensity, 0.0, 1.0)
            rotation_intensity = (1.0 - intensity_sensitivity) + (intensity_sensitivity * rotation_intensity)
            rotation = rotation_angle * rotation_intensity
            
            # Color grading (hue shift based on mid-range)
            hue_shift = 0.0
            saturation = 1.0
            brightness = 1.0
            
            if enable_color_grading:
                # Hue shift: mid-range energy
                hue_shift = mid_val * mid_hue_shift
                
                # Saturation: boost with treble
                saturation = 1.0 + treble_val * 0.3
            
            # Brightness pulse
            if enable_brightness:
                brightness = 1.0 + (bass_val + mid_val) * 0.3
            
            # Snare-triggered brightness flash
            if snare_triggered_flash and len(snare_hit_times) > 0:
                # Find nearest snare
                snare_time_distances = np.abs(snare_hit_times - current_time)
                nearest_snare_distance = np.min(snare_time_distances) if len(snare_time_distances) > 0 else float('inf')
                
                if nearest_snare_distance <= snare_window:
                    # Within snare window - add quick brightness flash
                    snare_proximity = 1.0 - (nearest_snare_distance / snare_window)
                    snare_proximity = np.clip(snare_proximity, 0.0, 1.0)
                    
                    # Quick flash: stronger and faster than regular brightness
                    flash_intensity = snare_proximity * 0.8  # Strong flash
                    brightness = brightness + flash_intensity  # Add to existing brightness
                    brightness = np.clip(brightness, 1.0, 2.0)  # Cap at 2x brightness
            
            # Blur (on strong bass)
            blur_intensity = 0.0
            if enable_blur:
                blur_intensity = bass_val * 0.5  # Moderate blur
            
            # Glitch (on high frequencies - treble and high-treble)
            glitch_intensity = 0.0
            if enable_glitch:
                glitch_intensity = (treble_val * 0.6 + high_treble_val * 0.4) * intensity_sensitivity
            
            # Artifacts (on high frequencies - treble and high-treble)
            artifacts_intensity = 0.0
            if enable_artifacts:
                # Scale artifacts more aggressively for better visibility
                base_intensity = (treble_val * 0.5 + high_treble_val * 0.5)
                # Apply intensity sensitivity but ensure minimum visibility
                artifacts_intensity = base_intensity * (0.5 + intensity_sensitivity * 0.5)  # 50% to 100% of base
                artifacts_intensity = np.clip(artifacts_intensity, 0.0, 1.0)
            
            # Apply effects
            if (zoom != 1.0 or rotation != 0.0 or hue_shift != 0.0 or saturation != 1.0 or 
                brightness != 1.0 or blur_intensity > 0.0 or glitch_intensity > 0.0 or 
                artifacts_intensity > 0.0):
                frame = self.apply_effects(
                    frame,
                    zoom=zoom,
                    rotation=rotation,
                    hue_shift=hue_shift,
                    saturation=saturation,
                    brightness=brightness,
                    blur_intensity=blur_intensity,
                    glitch_intensity=glitch_intensity,
                    artifacts_intensity=artifacts_intensity
                )
            
            # Write frame
            out.write(frame)
            
            # Progress indicator
            if (frame_idx + 1) % 30 == 0:
                progress = (frame_idx + 1) / self.total_frames * 100
                print(f"  Processing: {progress:.1f}% ({frame_idx + 1}/{self.total_frames})")
            
            frame_idx += 1
        
        self.cap.release()
        out.release()
        print(f"Enhanced video processing complete! Output saved to {output_path}")
    
    def close(self):
        """Release video resources"""
        if self.cap.isOpened():
            self.cap.release()
