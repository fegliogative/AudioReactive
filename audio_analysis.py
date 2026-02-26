"""
Audio Analysis Module
Detects bass drum hits and high-pitched frequencies in audio
Enhanced with multi-band analysis and intensity-based reactivity
"""

import numpy as np
import librosa
from scipy import signal
from typing import Dict, Tuple, Optional


class AudioAnalyzer:
    """
    Analyzes audio to detect frequencies across multiple bands
    Returns both peak detections and continuous energy curves for smooth reactivity
    """
    
    def __init__(self, audio_path, sr=22050):
        """
        Initialize audio analyzer
        
        Args:
            audio_path: Path to audio file
            sr: Sample rate (default 22050 Hz)
        """
        self.audio_path = audio_path
        self.sr = sr
        self.y = None
        self.S = None
        self.times = None
        self.hop_length = None
        self.n_fft = None
        
        # Legacy peak detection (for backward compatibility)
        self.bass_frames = None
        self.treble_frames = None
        
        # Enhanced: Energy curves for all frequency bands
        self.energy_curves = {}
        
    def load_audio(self):
        """Load audio file"""
        print(f"Loading audio from {self.audio_path}...")
        self.y, self.sr = librosa.load(self.audio_path, sr=self.sr)
        print(f"Audio loaded: {len(self.y)} samples at {self.sr} Hz")
        
    def compute_spectrogram(self, n_fft=2048, hop_length=512):
        """
        Compute STFT spectrogram
        
        Args:
            n_fft: FFT window size
            hop_length: Number of samples between successive frames
        """
        print("Computing spectrogram...")
        D = librosa.stft(self.y, n_fft=n_fft, hop_length=hop_length)
        self.S = np.abs(D)
        self.hop_length = hop_length
        self.n_fft = n_fft
        self.times = librosa.frames_to_time(
            np.arange(self.S.shape[1]), sr=self.sr, hop_length=hop_length
        )
        print(f"Spectrogram shape: {self.S.shape}")
        
    def extract_frequency_band_energy(self, freq_range: Tuple[float, float]) -> np.ndarray:
        """
        Extract energy for a specific frequency range (FIXED VERSION)
        
        Args:
            freq_range: (min_freq, max_freq) in Hz
            
        Returns:
            Energy curve as 1D array (one value per spectrogram frame)
        """
        fmin, fmax = freq_range
        
        # FIX: Get frequency bins directly in Hz (not mel-scale)
        freqs = librosa.fft_frequencies(sr=self.sr, n_fft=self.n_fft)
        
        # Create mask for frequency range (direct Hz comparison)
        freq_mask = (freqs >= fmin) & (freqs <= fmax)
        
        # Sum energy across frequency bins in this range
        energy = np.sum(self.S[freq_mask, :], axis=0)
        
        return energy
    
    def normalize_energy(self, energy: np.ndarray) -> np.ndarray:
        """
        Normalize energy curve to 0.0-1.0 range
        
        Args:
            energy: Raw energy values
            
        Returns:
            Normalized energy curve
        """
        energy_min = np.min(energy)
        energy_max = np.max(energy)
        energy_range = energy_max - energy_min
        
        if energy_range < 1e-8:
            # If no variation, return zeros
            return np.zeros_like(energy)
        
        # Normalize to 0.0-1.0
        normalized = (energy - energy_min) / energy_range
        
        return normalized
    
    def detect_peaks(self, energy: np.ndarray, threshold_percentile: float = 75, 
                     min_distance: int = 10) -> np.ndarray:
        """
        Detect peaks in energy curve
        
        Args:
            energy: Normalized energy curve
            threshold_percentile: Percentile for peak detection threshold
            min_distance: Minimum distance between peaks (in frames)
            
        Returns:
            Array of frame indices where peaks occur
        """
        threshold = np.percentile(energy, threshold_percentile)
        peaks, _ = signal.find_peaks(energy, height=threshold, distance=min_distance)
        return peaks
    
    def detect_bass_drums(self, bass_freq_range=(40, 100), threshold_percentile=75):
        """
        Detect bass drum hits (low frequency energy) - FIXED VERSION
        
        Args:
            bass_freq_range: Frequency range for bass drums (Hz)
            threshold_percentile: Percentile for peak detection
            
        Returns:
            Array of frame indices with bass drum activity
        """
        print(f"Detecting bass drums in range {bass_freq_range}...")
        
        # Extract energy using fixed method
        bass_energy = self.extract_frequency_band_energy(bass_freq_range)
        
        # Normalize
        bass_energy_normalized = self.normalize_energy(bass_energy)
        
        # Store energy curve for continuous reactivity
        self.energy_curves['bass'] = bass_energy_normalized
        
        # Detect peaks
        peaks = self.detect_peaks(bass_energy_normalized, threshold_percentile, min_distance=10)
        
        self.bass_frames = peaks
        print(f"Found {len(peaks)} bass drum hits")
        return peaks
    
    def detect_treble(self, treble_freq_range=(3000, 8000), threshold_percentile=70):
        """
        Detect high-pitched frequencies - FIXED VERSION
        
        Args:
            treble_freq_range: Frequency range for treble (Hz)
            threshold_percentile: Percentile for peak detection
            
        Returns:
            Array of frame indices with treble activity
        """
        print(f"Detecting treble in range {treble_freq_range}...")
        
        # Extract energy using fixed method
        treble_energy = self.extract_frequency_band_energy(treble_freq_range)
        
        # Normalize
        treble_energy_normalized = self.normalize_energy(treble_energy)
        
        # Store energy curve for continuous reactivity
        self.energy_curves['treble'] = treble_energy_normalized
        
        # Detect peaks
        peaks = self.detect_peaks(treble_energy_normalized, threshold_percentile, min_distance=5)
        
        self.treble_frames = peaks
        print(f"Found {len(peaks)} treble peaks")
        return peaks
    
    def analyze_multiple_bands(
        self,
        sub_bass_range: Tuple[float, float] = (20, 60),
        bass_range: Tuple[float, float] = (60, 250),
        mid_range: Tuple[float, float] = (250, 2000),
        treble_range: Tuple[float, float] = (2000, 6000),
        high_treble_range: Tuple[float, float] = (6000, 12000)
    ) -> Dict[str, np.ndarray]:
        """
        Analyze multiple frequency bands and return continuous energy curves
        
        Args:
            sub_bass_range: Sub-bass frequency range (Hz)
            bass_range: Bass frequency range (Hz)
            mid_range: Mid frequency range (Hz)
            treble_range: Treble frequency range (Hz)
            high_treble_range: High-treble frequency range (Hz)
            
        Returns:
            Dictionary mapping band names to normalized energy curves (0.0-1.0)
        """
        print("Analyzing multiple frequency bands...")
        
        bands = {
            'sub_bass': sub_bass_range,
            'bass': bass_range,
            'mid': mid_range,
            'treble': treble_range,
            'high_treble': high_treble_range
        }
        
        energy_curves = {}
        
        for band_name, freq_range in bands.items():
            print(f"  Processing {band_name} band ({freq_range[0]}-{freq_range[1]} Hz)...")
            
            # Extract energy
            energy = self.extract_frequency_band_energy(freq_range)
            
            # Normalize
            normalized = self.normalize_energy(energy)
            
            # Store
            energy_curves[band_name] = normalized
            
            # Calculate statistics
            mean_energy = np.mean(normalized)
            max_energy = np.max(normalized)
            print(f"    Mean energy: {mean_energy:.3f}, Max energy: {max_energy:.3f}")
        
        # Store for later use
        self.energy_curves.update(energy_curves)
        
        # Detect beats (peaks) in bass energy for beat-triggered effects
        bass_energy = energy_curves.get('bass', np.zeros(len(self.times)))
        bass_peaks = self.detect_peaks(bass_energy, threshold_percentile=75, min_distance=10)
        self.bass_beat_frames = bass_peaks  # Store beat frame indices
        
        # Detect snare hits in mid-range (200-500 Hz is typical snare range)
        # Use a narrower range within mid for better snare detection
        snare_freq_range = (200, 500)
        snare_energy = self.extract_frequency_band_energy(snare_freq_range)
        snare_energy_normalized = self.normalize_energy(snare_energy)
        snare_peaks = self.detect_peaks(snare_energy_normalized, threshold_percentile=70, min_distance=8)
        self.snare_hit_frames = snare_peaks  # Store snare hit frame indices
        
        print(f"Multi-band analysis complete. Energy curves available for: {list(energy_curves.keys())}")
        print(f"Detected {len(bass_peaks)} bass beats")
        print(f"Detected {len(snare_peaks)} snare hits")
        
        return energy_curves
    
    def get_frame_times(self):
        """Get time values for each frame"""
        return self.times
    
    def get_energy_curve(self, band_name: str) -> Optional[np.ndarray]:
        """
        Get stored energy curve for a specific band
        
        Args:
            band_name: Name of frequency band ('bass', 'treble', 'sub_bass', etc.)
            
        Returns:
            Normalized energy curve (0.0-1.0) or None if not found
        """
        return self.energy_curves.get(band_name)
    
    def analyze(self, bass_freq_range=(40, 100), treble_freq_range=(3000, 8000)):
        """
        Run complete audio analysis (legacy method for backward compatibility)
        
        Returns:
            Tuple of (bass_frames, treble_frames, times)
        """
        self.load_audio()
        self.compute_spectrogram()
        bass_frames = self.detect_bass_drums(bass_freq_range=bass_freq_range)
        treble_frames = self.detect_treble(treble_freq_range=treble_freq_range)
        
        return bass_frames, treble_frames, self.times
    
    def analyze_enhanced(
        self,
        sub_bass_range: Tuple[float, float] = (20, 60),
        bass_range: Tuple[float, float] = (60, 250),
        mid_range: Tuple[float, float] = (250, 2000),
        treble_range: Tuple[float, float] = (2000, 6000),
        high_treble_range: Tuple[float, float] = (6000, 12000)
    ) -> Tuple[Dict[str, np.ndarray], np.ndarray]:
        """
        Enhanced analysis with multiple frequency bands and continuous energy curves
        
        Returns:
            Tuple of (energy_curves_dict, frame_times)
            energy_curves_dict: Dictionary with keys: 'sub_bass', 'bass', 'mid', 'treble', 'high_treble'
            Each value is a normalized energy curve (0.0-1.0) with one value per spectrogram frame
        """
        self.load_audio()
        self.compute_spectrogram()
        
        # Analyze all frequency bands
        energy_curves = self.analyze_multiple_bands(
            sub_bass_range=sub_bass_range,
            bass_range=bass_range,
            mid_range=mid_range,
            treble_range=treble_range,
            high_treble_range=high_treble_range
        )
        
        return energy_curves, self.times
