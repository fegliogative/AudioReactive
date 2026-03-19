#!/usr/bin/env python3
"""
SoundReactive Video Generator - GUI Preview Application
PYQT5 VERSION - Reliable on macOS
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QSpinBox, QDoubleSpinBox, QCheckBox,
    QRadioButton, QButtonGroup, QGroupBox, QFileDialog, QScrollArea,
    QFrame, QComboBox, QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QObject, QUrl
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import cv2
import numpy as np
from PIL import Image
import os
import threading
from pathlib import Path
from audio_analysis import AudioAnalyzer
from video_processor import VideoProcessor
from image_to_video import ImageToVideoProcessor
from custom_modals import CustomMessageBox, CustomQuestion
import tempfile
import subprocess
import random
import time


class ProcessingSignals(QObject):
    """Signals for thread-safe GUI updates"""
    progress_update = pyqtSignal(int, str)  # progress_percent, status_message
    frame_update = pyqtSignal(object)  # frame (numpy array)
    analysis_progress = pyqtSignal(str)  # analysis status message


class SoundReactiveGUI(QMainWindow):
    """Main GUI application using PyQt5"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SoundReactive - Audio-Reactive Video Generator")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)
        
        # Application state
        self.video_path = None
        self.image_path = None
        self.image_folder_path = None
        self.image_list = []  # List of images for folder mode
        self.audio_path = None
        self.video_cap = None
        self.webcam_cap = None
        self.is_recording = False
        self.recording_writer = None
        self.webcam_thread = None
        self.recording_output_path = None
        self.recording_start_time = None
        self.recording_frame_count = 0
        
        # Audio player for webcam mode
        self.audio_player = None
        self.audio_position = 0  # Current audio position in milliseconds
        self.audio_loop_count = 0  # Track how many times audio has looped
        self.current_frame_idx = 0
        self.total_frames = 0
        self.fps = 30.0
        self.current_frame = None
        self.base_image = None
        self.energy_curves = None
        self.frame_times = None
        self.bass_beat_frames = None
        self.snare_hit_frames = None
        self.mode = "video"
        self.logo_photo = None
        self.prev_effect_intensities = {}
        self.effect_smoothing_factor = 0.3
        self.width = None
        self.height = None
        self.audio_duration = None
        
        # Processing signals for thread-safe updates
        self.processing_signals = ProcessingSignals()
        self.processing_signals.progress_update.connect(self._update_progress)
        self.processing_signals.frame_update.connect(self._update_frame_preview)
        self.processing_signals.analysis_progress.connect(self._update_analysis_status)
        
        # ====================================================================
        # STATUS MESSAGES - Add your own custom messages here!
        # ====================================================================
        # These messages are randomly selected during processing to provide
        # engaging feedback. Add your own messages to any category by simply
        # adding them to the list. The more messages, the more variety!
        # ====================================================================
        self.status_messages = {
            'audio_extraction': [
                "Extracting audio from video...",
                "Separating audio track...",
                "Preparing audio for analysis...",
                "Isolating sound frequencies...",
                "Extracting audio from video... gently, so it doesn’t scream.",
                "Separating sound from vision like a very polite divorce.",
                "Convincing the audio track to come out on its own.",
                "Removing sound from pictures, which were clearly very attached.",
                "Liberating audio from its visual obligations.",
                "Peeling off the soundtrack without damaging the spacetime continuum.",
                "Listening very carefully while pretending this is difficult."
            ],
            'audio_analysis': [
                "Analyzing frequency spectrum...",
                "Detecting beats and rhythms...",
                "Mapping audio to visual effects...",
                "Computing energy curves...",
                "Identifying bass drops and snare hits...",
                "Breaking down frequency bands...",
                "Calculating audio reactivity...",
                "Finding the perfect sync points...",
                "Analyzing frequency spectrum like it owes us money.",
                "Listening to the music with a furrowed digital brow.",
                "Detecting beats, rhythms, and questionable artistic decisions.",
                "Mapping sound waves while nodding thoughtfully.",
                "Identifying bass drops and moments of existential crisis.",
                "Breaking audio into frequencies, none of which asked for this.",
                "Calculating audio reactivity using advanced maths and mild optimism.",
                "Searching for sync points where everything briefly makes sense.",
                "Pretending to understand music theory.",
                "Measuring vibes with highly scientific enthusiasm."
            ],
            'processing_start': [
                "Initializing video processing...",
                "Setting up effect pipeline...",
                "Preparing to transform your media...",
                "Loading transformation engine...",
                "Ready to create magic...",
                "Initializing video processing. This may involve drama.",
                "Starting the transformation engine. No refunds.",
                "Preparing to bend reality slightly.",
                "Booting up the creative machinery. Please stand back.",
                "Aligning bits, bytes, and expectations.",
                "Checking if the laws of physics are negotiable today.",
                "Warming up the pixels. They respond better that way.",
                "Everything is ready. Confidence is simulated."
            ],
            'processing_frame': [
                "Applying audio-reactive effects...",
                "Syncing visuals with music...",
                "Creating dynamic transformations...",
                "Morphing frames to the beat...",
                "Blending frequencies into visuals...",
                "Transforming pixels to music...",
                "Making your image dance...",
                "Weaving audio into visuals...",
                "Painting with sound waves...",
                "Bringing static to life...",
                "Channeling the rhythm...",
                "Translating frequencies to motion...",
                "Applying audio-reactive effects with reckless precision.",
                "Syncing visuals to music, because silence is awkward.",
                "Making pixels dance despite their lack of limbs.",
                "Translating sound into motion using questionable logic.",
                "Convincing frames to feel the rhythm.",
                "Blending frequencies into visuals like a confused DJ.",
                "Turning static images into overachievers.",
                "Channeling rhythm through entirely innocent pixels.",
                "Painting with sound, without a license.",
                "Bending frames to the beat. They resist at first.",
                "Creating motion where none was previously agreed upon.",
                "Encouraging visuals to express themselves musically."
            ],
            'merging': [
                "Merging audio and video...",
                "Synchronizing final output...",
                "Combining audio-reactive visuals...",
                "Finalizing your creation...",
                "Putting it all together..."
                "Merging audio and video in holy matrimony.",
                "Reuniting sound and vision after their trial separation.",
                "Synchronizing everything and hoping no one notices the seams.",
                "Combining parts into something greater than their regrets.",
                "Stitching reality back together.",
                "Final assembly underway. Fingers crossed.",
                "Aligning timelines like a responsible time traveller."
            ],
            'complete': [
                "Processing complete!",
                "Your audio-reactive video is ready!",
                "Transformation finished successfully!",
                "Your masterpiece is complete!",
                "Ready to share your creation!",
                "Processing complete. Nobody panicked. Much.",
                "Your audio-reactive video is ready and surprisingly coherent.",
                "Transformation finished. Reality remains intact.",
                "Your masterpiece is complete. Define masterpiece loosely.",
                "All done. We are as surprised as you are.",
                "Finished successfully. Please admire responsibly.",
                "Creation complete. Applause is optional but encouraged."
            ],
            'folder_loading': [
                "Loading images from folder...",
                "Preparing image gallery...",
                "Scanning folder for images...",
                "Organizing your image collection...",
                "Loading images from folder. One by one, patiently.",
                "Scanning folder for images and judging filenames silently.",
                "Preparing image gallery with curatorial confidence.",
                "Organizing images into something resembling order.",
                "Counting images and pretending it matters.",
                "Locating pictures that thought they were hidden.",
                "Opening the folder of many visual possibilities."
            ],
            'webcam_starting': [
                "Starting webcam...",
                "Awakening the camera...",
                "Asking the webcam nicely to cooperate...",
                "Initializing visual capture device...",
                "Preparing to see what you see..."
            ],
            'webcam_recording': [
                "Recording your performance...",
                "Capturing the moment...",
                "Saving frames for posterity...",
                "Documenting reality with effects...",
                "Creating your audio-reactive masterpiece..."
            ]
        }
        
        # Initialize frequency weights (using regular floats, not tk.DoubleVar)
        self.init_frequency_weights()
        
        # Create UI
        self.create_ui()
        
        # Load logo
        self.load_logo()
    
    def init_frequency_weights(self):
        """Initialize frequency weight variables"""
        self.pixel_sort_weights = {
            'sub_bass': 0.0, 'bass': 0.0,
            'mid': 0.7, 'treble': 0.3,
            'high_treble': 0.0
        }
        self.kaleidoscope_weights = {
            'sub_bass': 0.0, 'bass': 0.0,
            'mid': 0.0, 'treble': 0.5,
            'high_treble': 0.5
        }
        self.wave_distortion_weights = {
            'sub_bass': 0.3, 'bass': 0.7,
            'mid': 0.0, 'treble': 0.0,
            'high_treble': 0.0
        }
        self.vhs_weights = {
            'sub_bass': 0.0, 'bass': 0.3,
            'mid': 0.3, 'treble': 0.4,
            'high_treble': 0.0
        }
        self.posterization_weights = {
            'sub_bass': 0.0, 'bass': 0.0,
            'mid': 0.8, 'treble': 0.2,
            'high_treble': 0.0
        }
        self.edge_detection_weights = {
            'sub_bass': 0.0, 'bass': 0.0,
            'mid': 0.0, 'treble': 0.4,
            'high_treble': 0.6
        }
        self.data_corruption_weights = {
            'sub_bass': 0.0, 'bass': 0.0,
            'mid': 0.0, 'treble': 0.5,
            'high_treble': 0.5
        }
        self.scan_lines_weights = {
            'sub_bass': 0.0, 'bass': 0.2,
            'mid': 0.3, 'treble': 0.5,
            'high_treble': 0.0
        }
    
    def create_ui(self):
        """Create the main user interface"""
        print("Creating PyQt5 UI...")
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Content area (horizontal split)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)
        
        # Left panel: Controls (scrollable)
        left_panel = self.create_controls_panel()
        content_layout.addWidget(left_panel, stretch=0)
        
        # Right panel: Preview
        right_panel = self.create_preview_panel()
        content_layout.addWidget(right_panel, stretch=1)
        
        main_layout.addLayout(content_layout, stretch=1)
        
        print("PyQt5 UI created successfully")
    
    def create_header(self):
        """Create header with logo and title"""
        header = QFrame()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 15, 15, 15)
        header_layout.setSpacing(20)
        
        # Logo - made larger
        self.logo_label = QLabel("[Logo]")
        self.logo_label.setFixedSize(400, 160)  # Increased from 200x80
        header_layout.addWidget(self.logo_label)
        
        # Title and subtitle
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(5)
        
        title_label = QLabel("SoundReactive")
        title_font = QFont("Helvetica", 24, QFont.Bold)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Audio-Reactive Video Generator")
        subtitle_font = QFont("Helvetica", 14)
        subtitle_label.setStyleSheet("color: #666;")
        title_layout.addWidget(subtitle_label)
        
        header_layout.addWidget(title_container)
        header_layout.addStretch()
        
        # About/Info button
        about_btn = QPushButton("ℹ About")
        about_btn.setFixedSize(100, 40)
        about_btn.clicked.connect(self.show_about_dialog)
        about_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            QPushButton:pressed {
                background-color: #2E6DA4;
            }
        """)
        header_layout.addWidget(about_btn)
        
        return header
    
    def create_controls_panel(self):
        """Create left panel with all controls"""
        # Scroll area for controls
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedWidth(500)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Container widget for controls
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setSpacing(20)  # Increased from 10 to 20 for better spacing
        controls_layout.setContentsMargins(15, 15, 15, 15)  # Increased margins
        
        # Create all control groups
        self.create_file_controls(controls_layout)
        self.create_basic_controls(controls_layout)
        self.create_advanced_controls(controls_layout)
        self.create_layer_blending_controls(controls_layout)
        self.create_effect_controls(controls_layout)
        self.create_action_buttons(controls_layout)
        
        # Add stretch at end
        controls_layout.addStretch()
        
        scroll_area.setWidget(controls_widget)
        return scroll_area
    
    def create_file_controls(self, parent_layout):
        """Create file selection controls"""
        print("  Creating file controls...")
        group = QGroupBox("Input Files")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        layout = QVBoxLayout()
        layout.setSpacing(12)  # Better spacing
        
        # Mode selector
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:"))
        
        self.mode_group = QButtonGroup()
        self.mode_video_radio = QRadioButton("Video")
        self.mode_video_radio.setChecked(True)
        self.mode_image_radio = QRadioButton("Image + Audio")
        self.mode_folder_radio = QRadioButton("Folder of Images + Audio")
        self.mode_webcam_radio = QRadioButton("Webcam + Audio (Live)")
        self.mode_group.addButton(self.mode_video_radio, 0)
        self.mode_group.addButton(self.mode_image_radio, 1)
        self.mode_group.addButton(self.mode_folder_radio, 2)
        self.mode_group.addButton(self.mode_webcam_radio, 3)
        self.mode_video_radio.toggled.connect(self.on_mode_change)
        self.mode_image_radio.toggled.connect(self.on_mode_change)
        self.mode_folder_radio.toggled.connect(self.on_mode_change)
        self.mode_webcam_radio.toggled.connect(self.on_mode_change)
        
        mode_layout.addWidget(self.mode_video_radio)
        mode_layout.addWidget(self.mode_image_radio)
        mode_layout.addWidget(self.mode_folder_radio)
        mode_layout.addWidget(self.mode_webcam_radio)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)
        
        # File buttons
        button_layout = QHBoxLayout()
        self.load_video_btn = QPushButton("Load Video")
        self.load_video_btn.clicked.connect(self.load_video)
        button_layout.addWidget(self.load_video_btn)
        
        self.load_image_btn = QPushButton("Load Image")
        self.load_image_btn.clicked.connect(self.load_image)
        self.load_image_btn.setEnabled(False)
        button_layout.addWidget(self.load_image_btn)
        
        self.load_folder_btn = QPushButton("Load Image Folder")
        self.load_folder_btn.clicked.connect(self.load_image_folder)
        self.load_folder_btn.setEnabled(False)
        button_layout.addWidget(self.load_folder_btn)
        
        self.load_audio_btn = QPushButton("Load Audio")
        self.load_audio_btn.clicked.connect(self.load_audio)
        self.load_audio_btn.setEnabled(False)
        button_layout.addWidget(self.load_audio_btn)
        layout.addLayout(button_layout)
        
        # Webcam controls (only visible in webcam mode)
        self.webcam_controls_frame = QFrame()
        self.webcam_controls_layout = QHBoxLayout(self.webcam_controls_frame)
        self.webcam_controls_frame.setVisible(False)
        
        self.start_webcam_btn = QPushButton("Start Webcam")
        self.start_webcam_btn.clicked.connect(self.start_webcam)
        self.webcam_controls_layout.addWidget(self.start_webcam_btn)
        
        self.stop_webcam_btn = QPushButton("Stop Webcam")
        self.stop_webcam_btn.clicked.connect(self.stop_webcam)
        self.stop_webcam_btn.setEnabled(False)
        self.webcam_controls_layout.addWidget(self.stop_webcam_btn)
        
        self.record_webcam_btn = QPushButton("Start Recording")
        self.record_webcam_btn.clicked.connect(self.toggle_webcam_recording)
        self.record_webcam_btn.setEnabled(False)
        self.webcam_controls_layout.addWidget(self.record_webcam_btn)
        
        layout.addWidget(self.webcam_controls_frame)
        
        # File path labels
        self.video_path_label = QLabel("No video loaded")
        self.video_path_label.setWordWrap(True)
        self.video_path_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                background-color: #f5f5f5;
                border-radius: 4px;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.video_path_label)
        
        self.image_path_label = QLabel("No image loaded")
        self.image_path_label.setWordWrap(True)
        layout.addWidget(self.image_path_label)
        
        self.image_folder_label = QLabel("No image folder loaded")
        self.image_folder_label.setWordWrap(True)
        layout.addWidget(self.image_folder_label)
        
        self.audio_path_label = QLabel("No audio loaded")
        self.audio_path_label.setWordWrap(True)
        layout.addWidget(self.audio_path_label)
        
        group.setLayout(layout)
        parent_layout.addWidget(group)
        print("    File controls created")
    
    def create_basic_controls(self, parent_layout):
        """Create basic effect controls"""
        print("  Creating basic controls...")
        group = QGroupBox("Basic Effects")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        layout = QVBoxLayout()
        layout.setSpacing(15)  # Increased spacing between controls
        
        # Zoom (1.0-2.0, default 1.3)
        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(QLabel("Zoom Factor:"))
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(100)  # 1.00
        self.zoom_slider.setMaximum(200)   # 2.00
        self.zoom_slider.setValue(130)     # 1.30
        self.zoom_slider.valueChanged.connect(self.on_zoom_change)
        zoom_layout.addWidget(self.zoom_slider)
        self.zoom_label = QLabel("1.30")
        self.zoom_label.setFixedWidth(50)
        zoom_layout.addWidget(self.zoom_label)
        layout.addLayout(zoom_layout)
        
        # Rotation (0-15°, default 5°)
        rot_layout = QHBoxLayout()
        rot_layout.addWidget(QLabel("Rotation (°):"))
        self.rotation_slider = QSlider(Qt.Horizontal)
        self.rotation_slider.setMinimum(0)
        self.rotation_slider.setMaximum(150)  # 0.0-15.0 in tenths
        self.rotation_slider.setValue(50)     # 5.0
        self.rotation_slider.valueChanged.connect(self.on_rotation_change)
        rot_layout.addWidget(self.rotation_slider)
        self.rotation_label = QLabel("5.00°")
        self.rotation_label.setFixedWidth(50)
        rot_layout.addWidget(self.rotation_label)
        layout.addLayout(rot_layout)
        
        # Frame navigation - made more prominent
        frame_layout = QVBoxLayout()  # Changed to vertical for better layout
        frame_label_row = QHBoxLayout()
        frame_label_row.addWidget(QLabel("Frame Navigation:"))
        frame_label_row.addStretch()
        frame_layout.addLayout(frame_label_row)
        
        frame_slider_row = QHBoxLayout()
        self.frame_slider = QSlider(Qt.Horizontal)
        self.frame_slider.setMinimum(0)
        self.frame_slider.setMaximum(0)
        self.frame_slider.setMinimumHeight(30)  # Make slider taller/more visible
        self.frame_slider.valueChanged.connect(self.on_frame_change)
        frame_slider_row.addWidget(self.frame_slider)
        self.frame_label = QLabel("0 / 0")
        self.frame_label.setFixedWidth(100)
        self.frame_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        frame_slider_row.addWidget(self.frame_label)
        frame_layout.addLayout(frame_slider_row)
        layout.addLayout(frame_layout)
        
        group.setLayout(layout)
        parent_layout.addWidget(group)
        print("    Basic controls created")
    
    def create_advanced_controls(self, parent_layout):
        """Create advanced effect controls"""
        print("  Creating advanced controls...")
        group = QGroupBox("Advanced Effects")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        layout = QVBoxLayout()
        layout.setSpacing(15)  # Increased spacing
        
        # Intensity sensitivity (0.0-1.0, default 0.7)
        intensity_layout = QHBoxLayout()
        intensity_layout.addWidget(QLabel("Intensity Sensitivity:"))
        self.intensity_slider = QSlider(Qt.Horizontal)
        self.intensity_slider.setMinimum(0)
        self.intensity_slider.setMaximum(100)
        self.intensity_slider.setValue(70)  # 0.7
        self.intensity_slider.valueChanged.connect(self.on_intensity_change)
        intensity_layout.addWidget(self.intensity_slider)
        self.intensity_label = QLabel("0.70")
        self.intensity_label.setFixedWidth(50)
        intensity_layout.addWidget(self.intensity_label)
        layout.addLayout(intensity_layout)
        
        # Smoothness (0.0-1.0, default 0.8)
        smooth_layout = QHBoxLayout()
        smooth_layout.addWidget(QLabel("Smoothness:"))
        self.smoothness_slider = QSlider(Qt.Horizontal)
        self.smoothness_slider.setMinimum(0)
        self.smoothness_slider.setMaximum(100)
        self.smoothness_slider.setValue(80)  # 0.8
        self.smoothness_slider.valueChanged.connect(self.on_smoothness_change)
        smooth_layout.addWidget(self.smoothness_slider)
        self.smoothness_label = QLabel("0.80")
        self.smoothness_label.setFixedWidth(50)
        smooth_layout.addWidget(self.smoothness_label)
        layout.addLayout(smooth_layout)
        
        # Effect smoothing (0.0-1.0, default 0.3)
        effect_smooth_layout = QHBoxLayout()
        effect_smooth_layout.addWidget(QLabel("Effect Smoothing:"))
        self.effect_smoothing_slider = QSlider(Qt.Horizontal)
        self.effect_smoothing_slider.setMinimum(0)
        self.effect_smoothing_slider.setMaximum(100)
        self.effect_smoothing_slider.setValue(30)  # 0.3
        self.effect_smoothing_slider.valueChanged.connect(self.on_effect_smoothing_change)
        effect_smooth_layout.addWidget(self.effect_smoothing_slider)
        self.effect_smoothing_label = QLabel("0.30")
        self.effect_smoothing_label.setFixedWidth(50)
        effect_smooth_layout.addWidget(self.effect_smoothing_label)
        layout.addLayout(effect_smooth_layout)
        
        # Effect toggles
        self.color_grading_check = QCheckBox("Color Grading")
        self.color_grading_check.setChecked(True)
        self.color_grading_check.toggled.connect(self.update_preview)
        layout.addWidget(self.color_grading_check)
        
        self.blur_check = QCheckBox("Blur")
        self.blur_check.toggled.connect(self.update_preview)
        layout.addWidget(self.blur_check)
        
        self.brightness_check = QCheckBox("Brightness")
        self.brightness_check.setChecked(True)
        self.brightness_check.toggled.connect(self.update_preview)
        layout.addWidget(self.brightness_check)
        
        # Hue shift
        hue_layout = QHBoxLayout()
        hue_layout.addWidget(QLabel("Hue Shift:"))
        self.hue_slider = QSlider(Qt.Horizontal)
        self.hue_slider.setMinimum(0)
        self.hue_slider.setMaximum(60)
        self.hue_slider.setValue(0)
        self.hue_slider.valueChanged.connect(self.on_hue_change)
        hue_layout.addWidget(self.hue_slider)
        self.hue_label = QLabel("0°")
        self.hue_label.setFixedWidth(50)
        hue_layout.addWidget(self.hue_label)
        layout.addLayout(hue_layout)
        
        group.setLayout(layout)
        parent_layout.addWidget(group)
        print("    Advanced controls created")
    
    def create_layer_blending_controls(self, parent_layout):
        """Create layer blending controls"""
        print("  Creating layer blending controls...")
        group = QGroupBox("Layer Blending")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Effect mode
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Effect Mode:"))
        self.blend_mode_combo = QComboBox()
        self.blend_mode_combo.addItems(["Direct", "Multiply", "Screen", "Overlay", "Soft Light"])
        self.blend_mode_combo.currentIndexChanged.connect(self.update_preview)
        mode_layout.addWidget(self.blend_mode_combo)
        layout.addLayout(mode_layout)
        
        # Opacity (only enabled when not "Direct")
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Opacity:"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setMinimum(0)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setValue(50)
        self.opacity_slider.valueChanged.connect(self.on_opacity_change)
        opacity_layout.addWidget(self.opacity_slider)
        self.opacity_label = QLabel("0.50")
        self.opacity_label.setFixedWidth(50)
        opacity_layout.addWidget(self.opacity_label)
        layout.addLayout(opacity_layout)
        
        # Update opacity slider state based on mode
        self.blend_mode_combo.currentIndexChanged.connect(self.update_blending_controls)
        self.update_blending_controls()
        
        group.setLayout(layout)
        parent_layout.addWidget(group)
        print("    Layer blending controls created")
    
    def create_effect_controls(self, parent_layout):
        """Create artistic effect controls with frequency mixing"""
        print("  Creating effect controls...")
        group = QGroupBox("Artistic Effects")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Effect checkboxes
        effects = [
            ("Pixel Sort", "pixel_sort"),
            ("Kaleidoscope", "kaleidoscope"),
            ("Wave Distortion", "wave_distortion"),
            ("VHS", "vhs"),
            ("Posterization", "posterization"),
            ("Edge Detection", "edge_detection"),
            ("Data Corruption", "data_corruption"),
            ("Scan Lines", "scan_lines")
        ]
        self.effect_checks = {}
        for effect_name, effect_key in effects:
            check = QCheckBox(effect_name)
            check.toggled.connect(self.update_preview)
            layout.addWidget(check)
            self.effect_checks[effect_key] = check
        
        # Frequency mixing controls
        layout.addWidget(QLabel(""))  # Spacer
        freq_label = QLabel("Frequency Mixing:")
        freq_font = QFont()
        freq_font.setBold(True)
        freq_label.setFont(freq_font)
        layout.addWidget(freq_label)
        
        freq_desc = QLabel("Adjust frequency band contributions for artistic effects")
        freq_desc.setStyleSheet("color: gray; font-size: 9pt;")
        layout.addWidget(freq_desc)
        
        # Create frequency mixing controls for each effect
        self.create_frequency_mixing_controls(layout)
        
        group.setLayout(layout)
        parent_layout.addWidget(group)
        print("    Effect controls created")
    
    def create_action_buttons(self, parent_layout):
        """Create action buttons"""
        print("  Creating action buttons...")
        group = QGroupBox("Actions")
        layout = QVBoxLayout()
        
        self.preview_frame_btn = QPushButton("Preview Frame")
        self.preview_frame_btn.clicked.connect(self.preview_single_frame)
        layout.addWidget(self.preview_frame_btn)
        
        self.preview_sequence_btn = QPushButton("Preview Sequence (1 sec)")
        self.preview_sequence_btn.clicked.connect(self.preview_sequence)
        layout.addWidget(self.preview_sequence_btn)
        
        self.process_video_btn = QPushButton("Process Full Video")
        self.process_video_btn.clicked.connect(self.process_full_video)
        layout.addWidget(self.process_video_btn)
        
        group.setLayout(layout)
        parent_layout.addWidget(group)
        print("    Action buttons created")
    
    def create_preview_panel(self):
        """Create preview panel"""
        print("  Creating preview panel...")
        panel = QFrame()
        layout = QVBoxLayout(panel)
        
        # Preview mode selector
        mode_group = QGroupBox("Preview Mode")
        mode_layout = QVBoxLayout()
        self.preview_mode_group = QButtonGroup()
        
        self.preview_original_radio = QRadioButton("Original")
        self.preview_original_radio.setChecked(True)
        self.preview_processed_radio = QRadioButton("Processed")
        self.preview_side_by_side_radio = QRadioButton("Side by Side")
        
        self.preview_mode_group.addButton(self.preview_original_radio, 0)
        self.preview_mode_group.addButton(self.preview_processed_radio, 1)
        self.preview_mode_group.addButton(self.preview_side_by_side_radio, 2)
        
        self.preview_original_radio.toggled.connect(self.update_preview)
        self.preview_processed_radio.toggled.connect(self.update_preview)
        self.preview_side_by_side_radio.toggled.connect(self.update_preview)
        
        mode_layout.addWidget(self.preview_original_radio)
        mode_layout.addWidget(self.preview_processed_radio)
        mode_layout.addWidget(self.preview_side_by_side_radio)
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        # Preview canvas
        self.preview_label = QLabel("No preview available")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(640, 360)
        self.preview_label.setStyleSheet("background-color: black; color: white;")
        layout.addWidget(self.preview_label, stretch=1)
        
        # Progress bar (for processing)
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        self.progress_label = QLabel("0%")
        self.progress_label.setFixedWidth(50)
        progress_layout.addWidget(self.progress_label)
        layout.addLayout(progress_layout)
        
        # Audio progress bar (for webcam recording)
        audio_progress_layout = QHBoxLayout()
        audio_progress_label = QLabel("Audio:")
        audio_progress_label.setFixedWidth(50)
        audio_progress_layout.addWidget(audio_progress_label)
        self.audio_progress_bar = QProgressBar()
        self.audio_progress_bar.setMinimum(0)
        self.audio_progress_bar.setMaximum(100)
        self.audio_progress_bar.setValue(0)
        self.audio_progress_bar.setVisible(False)  # Hidden by default
        self.audio_progress_bar.setFormat("%p%")  # Show percentage
        audio_progress_layout.addWidget(self.audio_progress_bar)
        self.audio_time_label = QLabel("0:00 / 0:00")
        self.audio_time_label.setFixedWidth(100)
        self.audio_time_label.setVisible(False)  # Hidden by default
        audio_progress_layout.addWidget(self.audio_time_label)
        self.audio_loop_label = QLabel("")
        self.audio_loop_label.setFixedWidth(60)
        self.audio_loop_label.setVisible(False)
        self.audio_loop_label.setStyleSheet("color: orange; font-weight: bold;")
        audio_progress_layout.addWidget(self.audio_loop_label)
        layout.addLayout(audio_progress_layout)
        
        # Status bar
        self.status_label = QLabel("Ready - Load a video to begin")
        layout.addWidget(self.status_label)
        
        print("    Preview panel created")
        return panel
    
    def create_frequency_mixing_controls(self, parent_layout):
        """Create frequency mixing controls for artistic effects"""
        effects = [
            ('pixel_sort', 'Pixel Sort', self.pixel_sort_weights),
            ('kaleidoscope', 'Kaleidoscope', self.kaleidoscope_weights),
            ('wave_distortion', 'Wave Distortion', self.wave_distortion_weights),
            ('vhs', 'VHS', self.vhs_weights),
            ('posterization', 'Posterization', self.posterization_weights),
            ('edge_detection', 'Edge Detection', self.edge_detection_weights),
            ('data_corruption', 'Data Corruption', self.data_corruption_weights),
            ('scan_lines', 'Scan Lines', self.scan_lines_weights),
        ]
        
        # Store sliders and labels for updates
        self.freq_sliders = {}
        self.freq_labels = {}
        
        for effect_key, effect_name, weights in effects:
            # Effect name label
            effect_label = QLabel(f"{effect_name}:")
            effect_font = QFont()
            effect_font.setBold(True)
            effect_font.setPointSize(8)
            effect_label.setFont(effect_font)
            parent_layout.addWidget(effect_label)
            
            # Frequency bands frame
            freq_frame = QFrame()
            freq_layout = QHBoxLayout(freq_frame)
            freq_layout.setContentsMargins(20, 0, 0, 5)
            freq_layout.setSpacing(5)
            
            bands = [
                ('sub_bass', 'Sub-B'),
                ('bass', 'Bass'),
                ('mid', 'Mid'),
                ('treble', 'Treb'),
                ('high_treble', 'H-Treb')
            ]
            
            for band_key, band_label in bands:
                # Band container
                band_container = QFrame()
                band_layout = QVBoxLayout(band_container)
                band_layout.setContentsMargins(0, 0, 0, 0)
                band_layout.setSpacing(2)
                
                # Band label
                band_label_widget = QLabel(band_label)
                band_label_widget.setFont(QFont("Helvetica", 7))
                band_layout.addWidget(band_label_widget)
                
                # Slider
                slider = QSlider(Qt.Horizontal)
                slider.setMinimum(0)
                slider.setMaximum(100)  # 0.0-1.0 in hundredths
                slider.setValue(int(weights[band_key] * 100))
                slider.setMaximumWidth(80)
                
                # Store slider reference
                if effect_key not in self.freq_sliders:
                    self.freq_sliders[effect_key] = {}
                self.freq_sliders[effect_key][band_key] = slider
                
                # Connect to update function (using lambda with default args to capture loop variables)
                def make_handler(e, b):
                    return lambda val: self.on_frequency_weight_change(e, b, val)
                slider.valueChanged.connect(make_handler(effect_key, band_key))
                band_layout.addWidget(slider)
                
                # Value label
                value_label = QLabel(f"{weights[band_key]:.1f}")
                value_label.setFont(QFont("Helvetica", 7))
                value_label.setFixedWidth(35)
                value_label.setAlignment(Qt.AlignCenter)
                band_layout.addWidget(value_label)
                
                # Store label reference
                if effect_key not in self.freq_labels:
                    self.freq_labels[effect_key] = {}
                self.freq_labels[effect_key][band_key] = value_label
                
                freq_layout.addWidget(band_container)
            
            freq_layout.addStretch()
            parent_layout.addWidget(freq_frame)
        
        print("    Frequency mixing controls created")
    
    def on_frequency_weight_change(self, effect_key, band_key, value):
        """Handle frequency weight changes"""
        # Update the weight value
        weight_value = value / 100.0
        weights = getattr(self, f"{effect_key}_weights")
        weights[band_key] = weight_value
        
        # Update label
        if effect_key in self.freq_labels and band_key in self.freq_labels[effect_key]:
            self.freq_labels[effect_key][band_key].setText(f"{weight_value:.1f}")
        
        # Update preview
        self.update_preview()
    
    def update_blending_controls(self):
        """Update blending controls based on mode"""
        mode = self.blend_mode_combo.currentText()
        if mode == "Direct":
            self.opacity_slider.setEnabled(False)
        else:
            self.opacity_slider.setEnabled(True)
    
    def load_logo(self):
        """Load application logo"""
        logo_path = "SoundReactive_Logo_Transparent_BG.png"
        if os.path.exists(logo_path):
            try:
                pixmap = QPixmap(logo_path)
                if not pixmap.isNull():
                    # Scale to larger size (400x160 as set in header)
                    scaled_pixmap = pixmap.scaled(400, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.logo_label.setPixmap(scaled_pixmap)
            except Exception as e:
                print(f"Could not load logo: {e}")
    
    def show_about_dialog(self):
        """Show About dialog with app information"""
        about_text = """
        <h2>SoundReactive</h2>
        <h3>Audio-Reactive Video Generator</h3>
        
        <p><b>Version:</b> 1.0.0</p>
        
        <p>Transform your videos, images, and live webcam feeds into dynamic, 
        music-reactive experiences! This powerful application analyzes audio 
        frequencies and automatically applies synchronized visual effects in real-time.</p>
        
        <p><b>Features:</b></p>
        <ul>
            <li>Real-time effect tweaking and preview</li>
            <li>Multiple input modes (Video, Image, Folder, Webcam)</li>
            <li>8 artistic effects with frequency mixing</li>
            <li>Advanced audio analysis with 5 frequency bands</li>
            <li>Live webcam recording with audio playback</li>
        </ul>
        
        <p><b>Author:</b>Fegliogative aka Jorge Gomes</p>
        <p><b>License:</b>CC4.0 BY-NC-SA</p>
        
        <p>Built with Python, PyQt5, OpenCV, and Librosa</p>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("About SoundReactive")
        msg.setTextFormat(Qt.RichText)
        msg.setText(about_text)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()
    
    # Event handlers (placeholders - will be implemented)
    def on_mode_change(self):
        if self.mode_video_radio.isChecked():
            self.mode = "video"
            self.load_video_btn.setEnabled(True)
            self.load_image_btn.setEnabled(False)
            self.load_folder_btn.setEnabled(False)
            self.load_audio_btn.setEnabled(False)
            self.webcam_controls_frame.setVisible(False)
            self.stop_webcam()  # Stop webcam if running
        elif self.mode_image_radio.isChecked():
            self.mode = "image"
            self.load_video_btn.setEnabled(False)
            self.load_image_btn.setEnabled(True)
            self.load_folder_btn.setEnabled(False)
            self.load_audio_btn.setEnabled(True)
            self.webcam_controls_frame.setVisible(False)
            self.stop_webcam()  # Stop webcam if running
        elif self.mode_folder_radio.isChecked():
            self.mode = "folder"
            self.load_video_btn.setEnabled(False)
            self.load_image_btn.setEnabled(False)
            self.load_folder_btn.setEnabled(True)
            self.load_audio_btn.setEnabled(True)
            self.webcam_controls_frame.setVisible(False)
            self.stop_webcam()  # Stop webcam if running
        else:  # webcam mode
            self.mode = "webcam"
            self.load_video_btn.setEnabled(False)
            self.load_image_btn.setEnabled(False)
            self.load_folder_btn.setEnabled(False)
            self.load_audio_btn.setEnabled(True)
            self.webcam_controls_frame.setVisible(True)
    
    def on_zoom_change(self, value):
        self.zoom_label.setText(f"{value / 100:.2f}")
        self.update_preview()
    
    def on_rotation_change(self, value):
        self.rotation_label.setText(f"{value / 10:.2f}°")
        self.update_preview()
    
    def on_effect_smoothing_change(self, value):
        self.effect_smoothing_label.setText(f"{value / 100:.2f}")
        self.effect_smoothing_factor = value / 100
        self.update_preview()
    
    def on_frame_change(self, value):
        if value != self.current_frame_idx:
            self.current_frame_idx = value
            
            if self.mode == "video" and self.video_cap and self.video_cap.isOpened():
                self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, value)
                ret, frame = self.video_cap.read()
                if ret:
                    self.current_frame = frame
                    self.update_preview()
            elif self.mode == "image" and self.base_image is not None:
                self.current_frame = self.base_image.copy()
                self.update_preview()
            elif self.mode == "folder" and self.image_list and self.audio_duration:
                # Calculate which image to show based on current frame
                current_time = value / self.fps
                num_images = len(self.image_list)
                duration_per_image = self.audio_duration / num_images
                image_index = int(current_time / duration_per_image)
                image_index = min(image_index, num_images - 1)
                
                # Load and resize the appropriate image
                img = cv2.imread(self.image_list[image_index])
                if img is not None:
                    resized = self._resize_image_to_fit(img, self.width, self.height)
                    self.current_frame = resized
                    self.base_image = resized  # Update base image for effects
                    self.update_preview()
        
        self.update_frame_label()
    
    def on_intensity_change(self, value):
        self.intensity_label.setText(f"{value / 100:.2f}")
        self.update_preview()
    
    def on_smoothness_change(self, value):
        self.smoothness_label.setText(f"{value / 100:.2f}")
        self.effect_smoothing_factor = value / 100
        self.update_preview()
    
    def on_hue_change(self, value):
        self.hue_label.setText(f"{value}°")
        self.update_preview()
    
    def on_opacity_change(self, value):
        self.opacity_label.setText(f"{value / 100:.2f}")
        self.update_preview()
    
    def update_frame_label(self):
        self.frame_label.setText(f"{self.current_frame_idx} / {max(0, self.total_frames - 1)}")
    
    def mix_frequency_bands(self, sub_bass, bass, mid, treble, high_treble, weights):
        """Mix frequency bands with given weights"""
        w_sub_bass = weights['sub_bass']
        w_bass = weights['bass']
        w_mid = weights['mid']
        w_treble = weights['treble']
        w_high_treble = weights['high_treble']
        
        total_weight = w_sub_bass + w_bass + w_mid + w_treble + w_high_treble
        if total_weight < 1e-8:
            return 0.0
        
        mixed = (sub_bass * w_sub_bass + bass * w_bass + mid * w_mid + 
                 treble * w_treble + high_treble * w_high_treble) / total_weight
        return np.clip(mixed, 0.0, 1.0)
    
    def apply_temporal_smoothing(self, effect_name, current_intensity):
        """Apply temporal smoothing to effect intensity"""
        if effect_name not in self.prev_effect_intensities:
            self.prev_effect_intensities[effect_name] = current_intensity
            return current_intensity
        
        alpha = 1.0 - self.effect_smoothing_factor
        smoothed = alpha * current_intensity + (1.0 - alpha) * self.prev_effect_intensities[effect_name]
        self.prev_effect_intensities[effect_name] = smoothed
        return smoothed
    
    def get_effect_parameters(self):
        """Get current effect parameters based on audio analysis"""
        if self.current_frame is None:
            return None
        
        current_time = self.current_frame_idx / self.fps
        
        if not self.energy_curves or self.frame_times is None or len(self.frame_times) == 0:
            sub_bass = bass = mid = treble = high_treble = 0.5
        else:
            sub_bass = np.interp(current_time, self.frame_times, self.energy_curves.get('sub_bass', np.zeros(len(self.frame_times))))
            bass = np.interp(current_time, self.frame_times, self.energy_curves.get('bass', np.zeros(len(self.frame_times))))
            mid = np.interp(current_time, self.frame_times, self.energy_curves.get('mid', np.zeros(len(self.frame_times))))
            treble = np.interp(current_time, self.frame_times, self.energy_curves.get('treble', np.zeros(len(self.frame_times))))
            high_treble = np.interp(current_time, self.frame_times, self.energy_curves.get('high_treble', np.zeros(len(self.frame_times))))
            
            sub_bass = np.clip(sub_bass, 0.0, 1.0)
            bass = np.clip(bass, 0.0, 1.0)
            mid = np.clip(mid, 0.0, 1.0)
            treble = np.clip(treble, 0.0, 1.0)
            high_treble = np.clip(high_treble, 0.0, 1.0)
        
        intensity_sens = self.intensity_slider.value() / 100.0
        zoom_val = self.zoom_slider.value() / 100.0
        rotation_val = self.rotation_slider.value() / 10.0
        
        # Calculate zoom (beat-triggered)
        zoom = 1.0
        current_time = self.current_frame_idx / self.fps
        if self.bass_beat_frames is not None and len(self.bass_beat_frames) > 0 and len(self.frame_times) > 0:
            bass_beat_times = self.frame_times[self.bass_beat_frames]
            time_distances = np.abs(bass_beat_times - current_time)
            nearest_beat_distance = np.min(time_distances) if len(time_distances) > 0 else float('inf')
            beat_window = 0.2
            if nearest_beat_distance <= beat_window:
                beat_proximity = 1.0 - (nearest_beat_distance / beat_window)
                beat_proximity = np.clip(beat_proximity, 0.0, 1.0)
                bass_intensity = (sub_bass * 0.2 + bass * 1.0) / 1.2
                bass_intensity = np.clip(bass_intensity, 0.0, 1.0)
                zoom_intensity = beat_proximity * 0.7 + bass_intensity * 0.3
                zoom_intensity = (1.0 - intensity_sens) + (intensity_sens * zoom_intensity)
                zoom = 1.0 + (zoom_val - 1.0) * zoom_intensity
        else:
            zoom_intensity = (sub_bass * 0.2 + bass * 1.0) / 1.2
            zoom_intensity = (1.0 - intensity_sens) + (intensity_sens * zoom_intensity)
            zoom = 1.0 + (zoom_val - 1.0) * zoom_intensity
        
        rotation_intensity = (treble * 1.0 + high_treble * 0.5) / 1.5
        rotation_intensity = (1.0 - intensity_sens) + (intensity_sens * rotation_intensity)
        rotation = rotation_val * rotation_intensity
        
        hue_shift = mid * (self.hue_slider.value()) if self.color_grading_check.isChecked() else 0.0
        saturation = 1.0 + (treble * 0.3) if self.color_grading_check.isChecked() else 1.0
        brightness = 1.0 + ((bass + mid) * 0.3) if self.brightness_check.isChecked() else 1.0
        
        # Snare flash
        if self.snare_hit_frames is not None and len(self.snare_hit_frames) > 0 and len(self.frame_times) > 0:
            snare_hit_times = self.frame_times[self.snare_hit_frames]
            snare_time_distances = np.abs(snare_hit_times - current_time)
            nearest_snare_distance = np.min(snare_time_distances) if len(snare_time_distances) > 0 else float('inf')
            snare_window = 0.15
            if nearest_snare_distance <= snare_window:
                snare_proximity = 1.0 - (nearest_snare_distance / snare_window)
                snare_proximity = np.clip(snare_proximity, 0.0, 1.0)
                flash_intensity = snare_proximity * 0.8
                brightness = brightness + flash_intensity
                brightness = np.clip(brightness, 1.0, 2.0)
        
        blur_intensity = bass * 0.5 if self.blur_check.isChecked() else 0.0
        
        # Artistic effects
        pixel_sort_intensity = 0.0
        if self.effect_checks['pixel_sort'].isChecked():
            base_intensity = self.mix_frequency_bands(sub_bass, bass, mid, treble, high_treble, self.pixel_sort_weights)
            if base_intensity > 1e-8:
                pixel_sort_intensity = base_intensity * (0.5 + intensity_sens * 0.5)
                pixel_sort_intensity = np.clip(pixel_sort_intensity, 0.0, 1.0)
                pixel_sort_intensity = self.apply_temporal_smoothing('pixel_sort', pixel_sort_intensity)
        
        kaleidoscope_intensity = 0.0
        if self.effect_checks['kaleidoscope'].isChecked():
            base_intensity = self.mix_frequency_bands(sub_bass, bass, mid, treble, high_treble, self.kaleidoscope_weights)
            if base_intensity > 1e-8:
                kaleidoscope_intensity = base_intensity * (0.5 + intensity_sens * 0.5)
                kaleidoscope_intensity = np.clip(kaleidoscope_intensity, 0.0, 1.0)
                kaleidoscope_intensity = self.apply_temporal_smoothing('kaleidoscope', kaleidoscope_intensity)
        
        wave_distortion_intensity = 0.0
        if self.effect_checks['wave_distortion'].isChecked():
            base_intensity = self.mix_frequency_bands(sub_bass, bass, mid, treble, high_treble, self.wave_distortion_weights)
            if base_intensity > 1e-8:
                wave_distortion_intensity = base_intensity * (0.5 + intensity_sens * 0.5)
                wave_distortion_intensity = np.clip(wave_distortion_intensity, 0.0, 1.0)
                wave_distortion_intensity = self.apply_temporal_smoothing('wave_distortion', wave_distortion_intensity)
        
        vhs_intensity = 0.0
        if self.effect_checks['vhs'].isChecked():
            base_intensity = self.mix_frequency_bands(sub_bass, bass, mid, treble, high_treble, self.vhs_weights)
            if base_intensity > 1e-8:
                vhs_intensity = base_intensity * (0.5 + intensity_sens * 0.5)
                vhs_intensity = np.clip(vhs_intensity, 0.0, 1.0)
                vhs_intensity = self.apply_temporal_smoothing('vhs', vhs_intensity)
        
        posterization_intensity = 0.0
        if self.effect_checks['posterization'].isChecked():
            base_intensity = self.mix_frequency_bands(sub_bass, bass, mid, treble, high_treble, self.posterization_weights)
            if base_intensity > 1e-8:
                posterization_intensity = base_intensity * (0.5 + intensity_sens * 0.5)
                posterization_intensity = np.clip(posterization_intensity, 0.0, 1.0)
                posterization_intensity = self.apply_temporal_smoothing('posterization', posterization_intensity)
        
        edge_detection_intensity = 0.0
        if self.effect_checks['edge_detection'].isChecked():
            base_intensity = self.mix_frequency_bands(sub_bass, bass, mid, treble, high_treble, self.edge_detection_weights)
            if base_intensity > 1e-8:
                edge_detection_intensity = base_intensity * (0.5 + intensity_sens * 0.5)
                edge_detection_intensity = np.clip(edge_detection_intensity, 0.0, 1.0)
                edge_detection_intensity = self.apply_temporal_smoothing('edge_detection', edge_detection_intensity)
        
        data_corruption_intensity = 0.0
        if self.effect_checks['data_corruption'].isChecked():
            base_intensity = self.mix_frequency_bands(sub_bass, bass, mid, treble, high_treble, self.data_corruption_weights)
            if base_intensity > 1e-8:
                data_corruption_intensity = base_intensity * (0.5 + intensity_sens * 0.5)
                data_corruption_intensity = np.clip(data_corruption_intensity, 0.0, 1.0)
                data_corruption_intensity = self.apply_temporal_smoothing('data_corruption', data_corruption_intensity)
        
        scan_lines_intensity = 0.0
        if self.effect_checks['scan_lines'].isChecked():
            base_intensity = self.mix_frequency_bands(sub_bass, bass, mid, treble, high_treble, self.scan_lines_weights)
            if base_intensity > 1e-8:
                scan_lines_intensity = base_intensity * (0.5 + intensity_sens * 0.5)
                scan_lines_intensity = np.clip(scan_lines_intensity, 0.0, 1.0)
                scan_lines_intensity = self.apply_temporal_smoothing('scan_lines', scan_lines_intensity)
        
        return {
            'zoom': zoom, 'rotation': rotation, 'hue_shift': hue_shift,
            'saturation': saturation, 'brightness': brightness,
            'blur_intensity': blur_intensity,
            'pixel_sort_intensity': pixel_sort_intensity,
            'kaleidoscope_intensity': kaleidoscope_intensity,
            'wave_distortion_intensity': wave_distortion_intensity,
            'vhs_intensity': vhs_intensity,
            'posterization_intensity': posterization_intensity,
            'edge_detection_intensity': edge_detection_intensity,
            'data_corruption_intensity': data_corruption_intensity,
            'scan_lines_intensity': scan_lines_intensity
        }
    
    def apply_effects_to_frame(self, frame):
        """Apply effects to a frame"""
        if frame is None:
            return None
        
        params = self.get_effect_parameters()
        if params is None:
            return frame
        
        processor = VideoProcessor.__new__(VideoProcessor)
        processor.fps = self.fps
        
        blend_mode = self.blend_mode_combo.currentText().lower()
        layer_opacity = self.opacity_slider.value() / 100.0
        
        return processor.apply_effects(
            frame,
            zoom=params['zoom'],
            rotation=params['rotation'],
            hue_shift=params['hue_shift'],
            saturation=params['saturation'],
            brightness=params['brightness'],
            blur_intensity=params['blur_intensity'],
            glitch_intensity=0.0,  # Not in UI yet
            artifacts_intensity=0.0,  # Not in UI yet
            pixel_sort_intensity=params['pixel_sort_intensity'],
            kaleidoscope_intensity=params['kaleidoscope_intensity'],
            wave_distortion_intensity=params['wave_distortion_intensity'],
            vhs_intensity=params['vhs_intensity'],
            posterization_intensity=params['posterization_intensity'],
            edge_detection_intensity=params['edge_detection_intensity'],
            data_corruption_intensity=params['data_corruption_intensity'],
            scan_lines_intensity=params['scan_lines_intensity'],
            effect_mode="direct",
            blend_mode=blend_mode,
            layer_opacity=layer_opacity
        )
    
    def update_preview(self):
        """Update preview display"""
        if self.current_frame is None:
            self.preview_label.setText("No video loaded")
            return
        
        mode = "original"
        if self.preview_processed_radio.isChecked():
            mode = "processed"
        elif self.preview_side_by_side_radio.isChecked():
            mode = "sidebyside"
        
        if mode == "original":
            display_frame = self.current_frame.copy()
        elif mode == "processed":
            display_frame = self.apply_effects_to_frame(self.current_frame.copy())
        else:  # sidebyside
            original = self.current_frame.copy()
            processed = self.apply_effects_to_frame(self.current_frame.copy())
            display_frame = np.hstack([original, processed])
        
        # Convert BGR to RGB
        display_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        
        # Resize for display
        h, w = display_frame.shape[:2]
        label_size = self.preview_label.size()
        scale = min(label_size.width() / w, label_size.height() / h, 1.0)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        display_frame = cv2.resize(display_frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        # Convert to QPixmap
        q_image = QImage(display_frame.data, new_w, new_h, new_w * 3, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.preview_label.setPixmap(pixmap)
    
    def load_video(self):
        """Load video file with enhanced feedback and validation"""
        # Open file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Video File", 
            "", 
            "Video Files (*.mp4 *.avi *.mov *.mkv *.MP4 *.AVI *.MOV *.MKV);;All Files (*)"
        )
        
        if not file_path:
            return
        
        # Validate file exists
        if not os.path.exists(file_path):
            QMessageBox.critical(self, "Error", f"File not found:\n{file_path}")
            return
        
        # Check file size (warn if very large)
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > 500:
            reply = QMessageBox.question(
                self, 
                "Large File Warning", 
                f"This video file is {file_size_mb:.1f} MB.\n"
                f"Processing may take a while. Continue?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # Update UI
        self.video_path = file_path
        video_name = os.path.basename(file_path)
        self.video_path_label.setText(f"Video: {video_name}")
        self.status_label.setText(f"Loading video: {video_name}...")
        self.processing_signals.progress_update.emit(5, f"Loading video file...")
        
        # Release previous video if open
        if self.video_cap:
            self.video_cap.release()
        
        # Open video file
        self.processing_signals.progress_update.emit(10, "Opening video file...")
        self.video_cap = cv2.VideoCapture(file_path)
        
        if not self.video_cap.isOpened():
            QMessageBox.critical(
                self, 
                "Error", 
                f"Could not open video file:\n{file_path}\n\n"
                f"Please ensure:\n"
                f"- The file is a valid video format\n"
                f"- The file is not corrupted\n"
                f"- You have read permissions for this file"
            )
            self.video_path = None
            self.video_path_label.setText("No video loaded")
            self.status_label.setText("Ready - Load a video to begin")
            return
        
        # Get video properties
        self.processing_signals.progress_update.emit(20, "Reading video properties...")
        self.total_frames = int(self.video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.video_cap.get(cv2.CAP_PROP_FPS)
        width = int(self.video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = self.total_frames / self.fps if self.fps > 0 else 0
        
        # Validate video properties
        if self.total_frames == 0:
            QMessageBox.critical(
                self, 
                "Error", 
                "Could not read video properties.\n"
                "The file may be corrupted or in an unsupported format."
            )
            self.video_cap.release()
            self.video_cap = None
            self.video_path = None
            self.video_path_label.setText("No video loaded")
            self.status_label.setText("Ready - Load a video to begin")
            return
        
        if self.fps <= 0:
            QMessageBox.warning(
                self,
                "Warning",
                f"Could not determine frame rate. Using default: 30 FPS"
            )
            self.fps = 30.0
        
        # Store dimensions
        self.width = width
        self.height = height
        
        # Update frame slider
        self.processing_signals.progress_update.emit(30, "Initializing video player...")
        self.frame_slider.setMaximum(max(0, self.total_frames - 1))
        self.current_frame_idx = 0
        self.frame_slider.setValue(0)
        self.update_frame_label()
        
        # Load first frame
        self.processing_signals.progress_update.emit(40, "Loading first frame...")
        ret, frame = self.video_cap.read()
        if ret:
            self.current_frame = frame
            self.update_preview()
        else:
            QMessageBox.warning(
                self,
                "Warning",
                "Could not read first frame from video.\n"
                "The video may be corrupted."
            )
        
        # Display video info
        video_info = (
            f"Video: {video_name}\n"
            f"Resolution: {width}x{height}\n"
            f"FPS: {self.fps:.2f}\n"
            f"Frames: {self.total_frames:,}\n"
            f"Duration: {duration:.2f}s\n"
            f"Size: {file_size_mb:.1f} MB"
        )
        self.video_path_label.setText(video_info)
        
        # Start audio analysis in background
        self.processing_signals.progress_update.emit(50, "Extracting audio and analyzing frequencies...")
        self.status_label.setText("Extracting audio and analyzing frequencies... This may take a moment.")
        threading.Thread(target=self.analyze_audio, daemon=True).start()
    
    def load_image(self):
        """Load image file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image File", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff *.webp);;All Files (*)"
        )
        if not file_path:
            return
        
        self.image_path = file_path
        self.base_image = cv2.imread(file_path)
        
        if self.base_image is None:
            QMessageBox.critical(self, "Error", "Could not load image file")
            return
        
        if self.audio_path:
            self.video_path_label.setText(f"Image: {os.path.basename(file_path)} | Audio: {os.path.basename(self.audio_path)}")
        else:
            self.video_path_label.setText(f"Image: {os.path.basename(file_path)}")
        
        h, w = self.base_image.shape[:2]
        self.current_frame = self.base_image.copy()
        self.width = w
        self.height = h
        
        if self.audio_path:
            self.status_label.setText("Analyzing audio frequencies...")
            threading.Thread(target=self.analyze_audio_image_mode, daemon=True).start()
        else:
            self.update_preview()
    
    def load_image_folder(self):
        """Load folder containing images"""
        folder_path = QFileDialog.getExistingDirectory(
            self, "Select Folder Containing Images"
        )
        if not folder_path:
            return
        
        self.processing_signals.progress_update.emit(10, self._get_random_message('folder_loading'))
        
        # Get all image files from folder
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp', '.PNG', '.JPG', '.JPEG', '.BMP', '.TIFF', '.WEBP'}
        image_files = []
        for file in os.listdir(folder_path):
            if any(file.endswith(ext) for ext in image_extensions):
                image_files.append(os.path.join(folder_path, file))
        
        if not image_files:
            QMessageBox.warning(self, "No Images Found", "No image files found in the selected folder.")
            self.processing_signals.progress_update.emit(0, "No images found")
            return
        
        # Sort files alphabetically for consistent ordering
        image_files.sort()
        
        self.image_folder_path = folder_path
        self.image_list = image_files
        
        self.processing_signals.progress_update.emit(50, f"Found {len(image_files)} images, loading first image...")
        
        # Load first image to get dimensions and show preview
        first_image = cv2.imread(image_files[0])
        if first_image is None:
            QMessageBox.critical(self, "Error", f"Could not load first image: {image_files[0]}")
            self.processing_signals.progress_update.emit(0, "Error loading image")
            return
        
        h, w = first_image.shape[:2]
        self.width = w
        self.height = h
        
        # Resize first image to fit (for preview)
        resized = self._resize_image_to_fit(first_image, w, h)
        self.base_image = resized
        self.current_frame = resized.copy()
        
        # Update labels
        if self.audio_path:
            self.image_folder_label.setText(f"Folder: {len(image_files)} images | Audio: {os.path.basename(self.audio_path)}")
        else:
            self.image_folder_label.setText(f"Folder: {len(image_files)} images loaded")
        
        self.processing_signals.progress_update.emit(100, f"Loaded {len(image_files)} images from folder")
        self.update_preview()
        
        # If audio is already loaded, analyze it
        if self.audio_path:
            self.status_label.setText("Analyzing audio frequencies...")
            threading.Thread(target=self.analyze_audio_image_mode, daemon=True).start()
    
    def load_audio(self):
        """Load audio file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Audio File", "", "Audio Files (*.mp3 *.wav *.m4a *.aac *.flac);;All Files (*)"
        )
        if not file_path:
            return
        
        self.audio_path = file_path
        
        if self.mode == "image" and self.image_path:
            self.video_path_label.setText(f"Image: {os.path.basename(self.image_path)} | Audio: {os.path.basename(file_path)}")
        elif self.mode == "folder" and self.image_list:
            self.image_folder_label.setText(f"Folder: {len(self.image_list)} images | Audio: {os.path.basename(file_path)}")
        else:
            self.audio_path_label.setText(f"Audio: {os.path.basename(file_path)}")
        
        if (self.mode == "image" and self.image_path) or (self.mode == "folder" and self.image_list) or (self.mode == "webcam"):
            self.status_label.setText("Analyzing audio frequencies...")
            threading.Thread(target=self.analyze_audio_image_mode, daemon=True).start()
    
    def _update_progress(self, percent, message):
        """Thread-safe progress update"""
        self.progress_bar.setValue(percent)
        self.progress_label.setText(f"{percent}%")
        if message:
            self.status_label.setText(message)
    
    def _update_frame_preview(self, frame):
        """Thread-safe frame preview update"""
        if frame is not None:
            # Convert BGR to RGB
            display_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Resize for display
            h, w = display_frame.shape[:2]
            label_size = self.preview_label.size()
            scale = min(label_size.width() / w, label_size.height() / h, 1.0)
            new_w = int(w * scale)
            new_h = int(h * scale)
            
            display_frame = cv2.resize(display_frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
            
            # Convert to QPixmap
            q_image = QImage(display_frame.data, new_w, new_h, new_w * 3, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.preview_label.setPixmap(pixmap)
    
    def _update_analysis_status(self, message):
        """Thread-safe analysis status update"""
        self.status_label.setText(message)
    
    def _get_random_message(self, category):
        """Get a random message from a category"""
        return random.choice(self.status_messages.get(category, ["Processing..."]))
    
    def analyze_audio(self):
        """Analyze audio in background thread (video mode)"""
        try:
            self.processing_signals.analysis_progress.emit(self._get_random_message('audio_extraction'))
            self.processing_signals.progress_update.emit(10, self._get_random_message('audio_extraction'))
            
            with tempfile.TemporaryDirectory() as tmpdir:
                audio_path = os.path.join(tmpdir, 'audio.wav')
                cmd = ['ffmpeg', '-i', self.video_path, '-q:a', '9', '-y', audio_path]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    self.processing_signals.progress_update.emit(0, "Error extracting audio")
                    return
                
                self.processing_signals.progress_update.emit(30, self._get_random_message('audio_analysis'))
                self.processing_signals.analysis_progress.emit(self._get_random_message('audio_analysis'))
                
                analyzer = AudioAnalyzer(audio_path, sr=22050)
                self.processing_signals.progress_update.emit(60, "Computing spectrogram...")
                
                self.energy_curves, self.frame_times = analyzer.analyze_enhanced()
                self.bass_beat_frames = analyzer.bass_beat_frames if hasattr(analyzer, 'bass_beat_frames') else None
                self.snare_hit_frames = analyzer.snare_hit_frames if hasattr(analyzer, 'snare_hit_frames') else None
                
                self.processing_signals.progress_update.emit(100, f"Ready - {self.total_frames} frames @ {self.fps:.1f} FPS")
                QTimer.singleShot(0, self.update_preview)
        except Exception as e:
            self.processing_signals.progress_update.emit(0, f"Error: {str(e)}")
    
    def analyze_audio_image_mode(self):
        """Analyze audio in background thread (image mode)"""
        try:
            if not self.audio_path or not os.path.exists(self.audio_path):
                self.processing_signals.progress_update.emit(0, "Error: Invalid audio file path")
                return
            
            self.processing_signals.progress_update.emit(20, self._get_random_message('audio_analysis'))
            self.processing_signals.analysis_progress.emit(self._get_random_message('audio_analysis'))
            
            analyzer = AudioAnalyzer(self.audio_path, sr=22050)
            self.processing_signals.progress_update.emit(40, "Loading audio file...")
            analyzer.load_audio()
            
            self.processing_signals.progress_update.emit(60, "Computing spectrogram...")
            analyzer.compute_spectrogram()
            
            self.processing_signals.progress_update.emit(80, "Analyzing frequency bands...")
            self.energy_curves, self.frame_times = analyzer.analyze_enhanced()
            self.bass_beat_frames = analyzer.bass_beat_frames if hasattr(analyzer, 'bass_beat_frames') else None
            self.snare_hit_frames = analyzer.snare_hit_frames if hasattr(analyzer, 'snare_hit_frames') else None
            
            import librosa
            y, sr = librosa.load(self.audio_path, sr=None)
            self.audio_duration = len(y) / sr
            self.total_frames = int(self.audio_duration * self.fps)
            
            QTimer.singleShot(0, lambda: self.frame_slider.setMaximum(max(0, self.total_frames - 1)))
            QTimer.singleShot(0, lambda: self.frame_slider.setValue(0))
            self.current_frame_idx = 0
            
            if self.mode == "folder":
                mode_text = f"Folder mode ({len(self.image_list)} images)"
            elif self.mode == "webcam":
                mode_text = "Webcam mode"
            else:
                mode_text = "Image mode"
            
            if self.mode != "webcam":
                self.processing_signals.progress_update.emit(100, f"Ready - {mode_text}: {self.total_frames} frames @ {self.fps:.1f} FPS")
            else:
                self.processing_signals.progress_update.emit(100, f"Ready - {mode_text}: Audio analyzed, effects will apply to webcam")
            
            QTimer.singleShot(0, self.update_preview)
        except Exception as e:
            self.processing_signals.progress_update.emit(0, f"Error: {str(e)}")
    
    def preview_single_frame(self):
        """Preview effects on current frame"""
        if self.current_frame is None:
            QMessageBox.information(self, "Info", "Please load a video first")
            return
        self.update_preview()
    
    def preview_sequence(self):
        """Preview effects on a 1-second sequence"""
        if self.current_frame is None or not self.video_cap:
            QMessageBox.information(self, "Info", "Please load a video first")
            return
        
        output_path, _ = QFileDialog.getSaveFileName(
            self, "Save Preview Sequence", "", "MP4 Files (*.mp4);;All Files (*)"
        )
        if not output_path:
            return
        
        self.status_label.setText("Generating preview sequence...")
        threading.Thread(target=self._generate_preview_sequence, args=(output_path,), daemon=True).start()
    
    def _generate_preview_sequence(self, output_path):
        """Generate preview sequence in background"""
        try:
            start_frame = self.current_frame_idx
            num_frames = int(self.fps)
            end_frame = min(start_frame + num_frames, self.total_frames)
            
            self.processing_signals.progress_update.emit(0, "Generating preview sequence...")
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, self.fps,
                                (self.current_frame.shape[1], self.current_frame.shape[0]))
            
            self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            
            frames_to_process = end_frame - start_frame
            original_frame_idx = self.current_frame_idx
            
            for i, frame_idx in enumerate(range(start_frame, end_frame)):
                ret, frame = self.video_cap.read()
                if not ret:
                    break
                
                # Set current frame index for effect calculation
                self.current_frame_idx = frame_idx
                
                processed = self.apply_effects_to_frame(frame.copy())
                out.write(processed)
                
                progress = int((i + 1) / frames_to_process * 100.0)
                message = f"Processing preview frame {i + 1}/{frames_to_process}"
                self.processing_signals.progress_update.emit(progress, message)
                
                # Show frame preview every few frames
                if i % 5 == 0 or i == frames_to_process - 1:
                    self.processing_signals.frame_update.emit(processed)
            
            # Restore original frame index
            self.current_frame_idx = original_frame_idx
            out.release()
            
            self.processing_signals.progress_update.emit(100, f"Preview sequence saved to {os.path.basename(output_path)}")
            QTimer.singleShot(1000, lambda: self.processing_signals.progress_update.emit(0, "Ready"))
            QTimer.singleShot(0, lambda: QMessageBox.information(self, "Success", f"Preview sequence saved!\n{output_path}"))
        except Exception as e:
            self.processing_signals.progress_update.emit(0, f"Error: {str(e)}")
            QTimer.singleShot(0, lambda msg=str(e): QMessageBox.critical(self, "Error", f"Failed to generate preview: {msg}"))
    
    def process_full_video(self):
        """Process full video/image"""
        if self.mode == "video":
            if not self.video_path:
                QMessageBox.information(self, "Info", "Please load a video first")
                return
        elif self.mode == "image":
            if not self.image_path or not self.audio_path:
                QMessageBox.information(self, "Info", "Please load both image and audio files")
                return
        elif self.mode == "folder":
            if not self.image_list or not self.audio_path:
                QMessageBox.information(self, "Info", "Please load both image folder and audio file")
                return
        
        if not self.energy_curves:
            QMessageBox.information(self, "Info", "Please wait for audio analysis to complete")
            return
        
        output_path, _ = QFileDialog.getSaveFileName(
            self, "Save Processed Video", "", "MP4 Files (*.mp4);;All Files (*)"
        )
        if not output_path:
            return
        
        self.status_label.setText("Processing full video... This may take a while.")
        threading.Thread(target=self._process_full_video_thread, args=(output_path,), daemon=True).start()
    
    def _resize_image_to_fit(self, image, target_width, target_height):
        """Resize image to fit target dimensions while maintaining aspect ratio, then center it"""
        h, w = image.shape[:2]
        
        # Calculate scaling to fit
        scale = min(target_width / w, target_height / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # Resize image
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
        
        # Create canvas and center the image
        canvas = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        y_offset = (target_height - new_h) // 2
        x_offset = (target_width - new_w) // 2
        canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
        
        return canvas
    
    def _crossfade_images(self, img1, img2, alpha):
        """Blend two images with crossfade (alpha: 0.0 = img1, 1.0 = img2)"""
        alpha = np.clip(alpha, 0.0, 1.0)
        return cv2.addWeighted(img1, 1.0 - alpha, img2, alpha, 0)
    
    def _process_image_to_video_with_progress(self, processor, output_path, energy_curves, frame_times, 
                                               bass_beat_frames, snare_hit_frames):
        """Process image to video with progress reporting and frame-by-frame visualization"""
        # Get total frames
        total_frames = processor.total_frames
        
        # Setup video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, self.fps, (self.width, self.height))
        
        # Interpolate energy curves for all frames
        video_frame_times = np.linspace(0, processor.audio_duration, total_frames)
        sub_bass_interp = np.interp(video_frame_times, frame_times, energy_curves.get('sub_bass', np.zeros(len(frame_times))))
        bass_interp = np.interp(video_frame_times, frame_times, energy_curves.get('bass', np.zeros(len(frame_times))))
        mid_interp = np.interp(video_frame_times, frame_times, energy_curves.get('mid', np.zeros(len(frame_times))))
        treble_interp = np.interp(video_frame_times, frame_times, energy_curves.get('treble', np.zeros(len(frame_times))))
        high_treble_interp = np.interp(video_frame_times, frame_times, energy_curves.get('high_treble', np.zeros(len(frame_times))))
        
        # Get beat times
        if bass_beat_frames is not None and len(bass_beat_frames) > 0:
            bass_beat_times = frame_times[bass_beat_frames]
        else:
            bass_beat_times = np.array([])
        
        if snare_hit_frames is not None and len(snare_hit_frames) > 0:
            snare_hit_times = frame_times[snare_hit_frames]
        else:
            snare_hit_times = np.array([])
        
        # Handle folder mode vs single image mode
        if self.mode == "folder" and len(self.image_list) > 1:
            # Folder mode: multiple images with crossfade
            num_images = len(self.image_list)
            duration_per_image = processor.audio_duration / num_images
            frames_per_image = int(duration_per_image * self.fps)
            crossfade_duration = 1.0  # 1 second crossfade
            crossfade_frames = int(crossfade_duration * self.fps)
            
            # Load and resize all images
            loaded_images = []
            for img_path in self.image_list:
                img = cv2.imread(img_path)
                if img is not None:
                    resized = self._resize_image_to_fit(img, self.width, self.height)
                    loaded_images.append(resized)
            
            if not loaded_images:
                self.processing_signals.progress_update.emit(0, "Error: No valid images loaded")
                out.release()
                return
            
            # Process each frame
            for frame_idx in range(total_frames):
                self.current_frame_idx = frame_idx
                current_time = frame_idx / self.fps
                
                # Determine which image(s) to use
                image_index = int(current_time / duration_per_image)
                image_index = min(image_index, len(loaded_images) - 1)
                
                # Calculate position within current image segment
                segment_start_time = image_index * duration_per_image
                segment_time = current_time - segment_start_time
                
                # Get base frame (with crossfade if transitioning)
                if image_index < len(loaded_images) - 1 and segment_time > (duration_per_image - crossfade_duration):
                    # In crossfade zone
                    next_image_index = image_index + 1
                    fade_progress = (segment_time - (duration_per_image - crossfade_duration)) / crossfade_duration
                    fade_progress = np.clip(fade_progress, 0.0, 1.0)
                    base_frame = self._crossfade_images(
                        loaded_images[image_index],
                        loaded_images[next_image_index],
                        fade_progress
                    )
                else:
                    # Normal image display
                    base_frame = loaded_images[image_index].copy()
                
                # Apply effects
                processed_frame = self.apply_effects_to_frame(base_frame)
                out.write(processed_frame)
                
                # Update progress
                if frame_idx % 3 == 0 or frame_idx == total_frames - 1:
                    progress = int((frame_idx + 1) / total_frames * 85)
                    message = f"{self._get_random_message('processing_frame')} ({frame_idx + 1}/{total_frames}) - Image {image_index + 1}/{len(loaded_images)}"
                    self.processing_signals.progress_update.emit(progress, message)
                    self.processing_signals.frame_update.emit(processed_frame)
        else:
            # Single image mode (original behavior)
            for frame_idx in range(total_frames):
                self.current_frame_idx = frame_idx
                
                # Start with base image
                frame = self.base_image.copy()
                
                # Apply effects
                processed_frame = self.apply_effects_to_frame(frame)
                out.write(processed_frame)
                
                # Update progress
                if frame_idx % 3 == 0 or frame_idx == total_frames - 1:
                    progress = int((frame_idx + 1) / total_frames * 85)
                    message = f"{self._get_random_message('processing_frame')} ({frame_idx + 1}/{total_frames})"
                    self.processing_signals.progress_update.emit(progress, message)
                    self.processing_signals.frame_update.emit(processed_frame)
        
        out.release()
    
    def _process_video_with_progress(self, video_path, output_path, energy_curves, frame_times,
                                     bass_beat_frames=None, snare_hit_frames=None):
        """Process video with progress reporting and frame-by-frame visualization"""
        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError(f"Could not open video: {video_path}")
        
        # Get video properties
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        if total_frames == 0:
            cap.release()
            raise RuntimeError("Video has no frames")
        
        # Setup video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        if not out.isOpened():
            cap.release()
            raise RuntimeError("Could not create output video writer")
        
        # Interpolate energy curves for all frames
        video_duration = total_frames / fps
        video_frame_times = np.linspace(0, video_duration, total_frames)
        
        # Interpolate energy curves to video frame times
        sub_bass_interp = np.interp(video_frame_times, frame_times, energy_curves.get('sub_bass', np.zeros(len(frame_times))))
        bass_interp = np.interp(video_frame_times, frame_times, energy_curves.get('bass', np.zeros(len(frame_times))))
        mid_interp = np.interp(video_frame_times, frame_times, energy_curves.get('mid', np.zeros(len(frame_times))))
        treble_interp = np.interp(video_frame_times, frame_times, energy_curves.get('treble', np.zeros(len(frame_times))))
        high_treble_interp = np.interp(video_frame_times, frame_times, energy_curves.get('high_treble', np.zeros(len(frame_times))))
        
        # Get beat times
        if bass_beat_frames is not None and len(bass_beat_frames) > 0:
            bass_beat_times = frame_times[bass_beat_frames]
        else:
            bass_beat_times = np.array([])
        
        if snare_hit_frames is not None and len(snare_hit_frames) > 0:
            snare_hit_times = frame_times[snare_hit_frames]
        else:
            snare_hit_times = np.array([])
        
        # Process each frame
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Update current frame index for effect calculation
            self.current_frame_idx = frame_idx
            current_time = frame_idx / fps
            
            # Get effect parameters for this frame
            intensity_sens = self.intensity_slider.value() / 100.0
            zoom_val = self.zoom_slider.value() / 100.0
            rotation_val = self.rotation_slider.value() / 10.0
            
            # Get energy values for this frame
            sub_bass_val = sub_bass_interp[frame_idx]
            bass_val = bass_interp[frame_idx]
            mid_val = mid_interp[frame_idx]
            treble_val = treble_interp[frame_idx]
            high_treble_val = high_treble_interp[frame_idx]
            
            # Calculate zoom (beat-triggered)
            zoom = 1.0
            if self.bass_beat_frames is not None and len(self.bass_beat_frames) > 0 and len(bass_beat_times) > 0:
                time_distances = np.abs(bass_beat_times - current_time)
                nearest_beat_distance = np.min(time_distances) if len(time_distances) > 0 else float('inf')
                beat_window = 0.2
                if nearest_beat_distance <= beat_window:
                    beat_proximity = 1.0 - (nearest_beat_distance / beat_window)
                    beat_proximity = np.clip(beat_proximity, 0.0, 1.0)
                    bass_intensity = (sub_bass_val * 0.2 + bass_val * 1.0) / 1.2
                    bass_intensity = np.clip(bass_intensity, 0.0, 1.0)
                    zoom_intensity = beat_proximity * 0.7 + bass_intensity * 0.3
                    zoom_intensity = (1.0 - intensity_sens) + (intensity_sens * zoom_intensity)
                    zoom = 1.0 + (zoom_val - 1.0) * zoom_intensity
            else:
                zoom_intensity = (sub_bass_val * 0.2 + bass_val * 1.0) / 1.2
                zoom_intensity = (1.0 - intensity_sens) + (intensity_sens * zoom_intensity)
                zoom = 1.0 + (zoom_val - 1.0) * zoom_intensity
            
            # Calculate rotation
            rotation_intensity = (treble_val * 1.0 + high_treble_val * 0.5) / 1.5
            rotation_intensity = (1.0 - intensity_sens) + (intensity_sens * rotation_intensity)
            rotation = rotation_val * rotation_intensity
            
            # Calculate hue shift, saturation, brightness
            hue_shift = mid_val * (self.hue_slider.value()) if self.color_grading_check.isChecked() else 0.0
            saturation = 1.0 + (treble_val * 0.3) if self.color_grading_check.isChecked() else 1.0
            brightness = 1.0 + ((bass_val + mid_val) * 0.3) if self.brightness_check.isChecked() else 1.0
            
            # Snare flash
            if snare_hit_frames is not None and len(snare_hit_frames) > 0 and len(snare_hit_times) > 0:
                snare_time_distances = np.abs(snare_hit_times - current_time)
                nearest_snare_distance = np.min(snare_time_distances) if len(snare_time_distances) > 0 else float('inf')
                snare_window = 0.15
                if nearest_snare_distance <= snare_window:
                    snare_proximity = 1.0 - (nearest_snare_distance / snare_window)
                    snare_proximity = np.clip(snare_proximity, 0.0, 1.0)
                    flash_intensity = snare_proximity * 0.8
                    brightness = brightness + flash_intensity
                    brightness = np.clip(brightness, 1.0, 2.0)
            
            blur_intensity = bass_val * 0.5 if self.blur_check.isChecked() else 0.0
            
            # Calculate artistic effect intensities
            pixel_sort_intensity = 0.0
            if self.effect_checks['pixel_sort'].isChecked():
                base_intensity = self.mix_frequency_bands(sub_bass_val, bass_val, mid_val, treble_val, high_treble_val, self.pixel_sort_weights)
                if base_intensity > 1e-8:
                    pixel_sort_intensity = base_intensity * (0.5 + intensity_sens * 0.5)
                    pixel_sort_intensity = np.clip(pixel_sort_intensity, 0.0, 1.0)
                    pixel_sort_intensity = self.apply_temporal_smoothing('pixel_sort', pixel_sort_intensity)
            
            kaleidoscope_intensity = 0.0
            if self.effect_checks['kaleidoscope'].isChecked():
                base_intensity = self.mix_frequency_bands(sub_bass_val, bass_val, mid_val, treble_val, high_treble_val, self.kaleidoscope_weights)
                if base_intensity > 1e-8:
                    kaleidoscope_intensity = base_intensity * (0.5 + intensity_sens * 0.5)
                    kaleidoscope_intensity = np.clip(kaleidoscope_intensity, 0.0, 1.0)
                    kaleidoscope_intensity = self.apply_temporal_smoothing('kaleidoscope', kaleidoscope_intensity)
            
            wave_distortion_intensity = 0.0
            if self.effect_checks['wave_distortion'].isChecked():
                base_intensity = self.mix_frequency_bands(sub_bass_val, bass_val, mid_val, treble_val, high_treble_val, self.wave_distortion_weights)
                if base_intensity > 1e-8:
                    wave_distortion_intensity = base_intensity * (0.5 + intensity_sens * 0.5)
                    wave_distortion_intensity = np.clip(wave_distortion_intensity, 0.0, 1.0)
                    wave_distortion_intensity = self.apply_temporal_smoothing('wave_distortion', wave_distortion_intensity)
            
            vhs_intensity = 0.0
            if self.effect_checks['vhs'].isChecked():
                base_intensity = self.mix_frequency_bands(sub_bass_val, bass_val, mid_val, treble_val, high_treble_val, self.vhs_weights)
                if base_intensity > 1e-8:
                    vhs_intensity = base_intensity * (0.5 + intensity_sens * 0.5)
                    vhs_intensity = np.clip(vhs_intensity, 0.0, 1.0)
                    vhs_intensity = self.apply_temporal_smoothing('vhs', vhs_intensity)
            
            posterization_intensity = 0.0
            if self.effect_checks['posterization'].isChecked():
                base_intensity = self.mix_frequency_bands(sub_bass_val, bass_val, mid_val, treble_val, high_treble_val, self.posterization_weights)
                if base_intensity > 1e-8:
                    posterization_intensity = base_intensity * (0.5 + intensity_sens * 0.5)
                    posterization_intensity = np.clip(posterization_intensity, 0.0, 1.0)
                    posterization_intensity = self.apply_temporal_smoothing('posterization', posterization_intensity)
            
            edge_detection_intensity = 0.0
            if self.effect_checks['edge_detection'].isChecked():
                base_intensity = self.mix_frequency_bands(sub_bass_val, bass_val, mid_val, treble_val, high_treble_val, self.edge_detection_weights)
                if base_intensity > 1e-8:
                    edge_detection_intensity = base_intensity * (0.5 + intensity_sens * 0.5)
                    edge_detection_intensity = np.clip(edge_detection_intensity, 0.0, 1.0)
                    edge_detection_intensity = self.apply_temporal_smoothing('edge_detection', edge_detection_intensity)
            
            data_corruption_intensity = 0.0
            if self.effect_checks['data_corruption'].isChecked():
                base_intensity = self.mix_frequency_bands(sub_bass_val, bass_val, mid_val, treble_val, high_treble_val, self.data_corruption_weights)
                if base_intensity > 1e-8:
                    data_corruption_intensity = base_intensity * (0.5 + intensity_sens * 0.5)
                    data_corruption_intensity = np.clip(data_corruption_intensity, 0.0, 1.0)
                    data_corruption_intensity = self.apply_temporal_smoothing('data_corruption', data_corruption_intensity)
            
            scan_lines_intensity = 0.0
            if self.effect_checks['scan_lines'].isChecked():
                base_intensity = self.mix_frequency_bands(sub_bass_val, bass_val, mid_val, treble_val, high_treble_val, self.scan_lines_weights)
                if base_intensity > 1e-8:
                    scan_lines_intensity = base_intensity * (0.5 + intensity_sens * 0.5)
                    scan_lines_intensity = np.clip(scan_lines_intensity, 0.0, 1.0)
                    scan_lines_intensity = self.apply_temporal_smoothing('scan_lines', scan_lines_intensity)
            
            # Get blend mode and opacity
            blend_mode = self.blend_mode_combo.currentText().lower()
            layer_opacity = self.opacity_slider.value() / 100.0
            
            # Apply effects using VideoProcessor
            processor = VideoProcessor.__new__(VideoProcessor)
            processor.fps = fps
            
            processed_frame = processor.apply_effects(
                frame,
                zoom=zoom,
                rotation=rotation,
                hue_shift=hue_shift,
                saturation=saturation,
                brightness=brightness,
                blur_intensity=blur_intensity,
                glitch_intensity=0.0,  # Not in UI
                artifacts_intensity=0.0,  # Not in UI
                pixel_sort_intensity=pixel_sort_intensity,
                kaleidoscope_intensity=kaleidoscope_intensity,
                wave_distortion_intensity=wave_distortion_intensity,
                vhs_intensity=vhs_intensity,
                posterization_intensity=posterization_intensity,
                edge_detection_intensity=edge_detection_intensity,
                data_corruption_intensity=data_corruption_intensity,
                scan_lines_intensity=scan_lines_intensity,
                effect_mode="direct",
                blend_mode=blend_mode,
                layer_opacity=layer_opacity
            )
            
            # Write frame
            out.write(processed_frame)
            
            # Update progress
            if frame_idx % 3 == 0 or frame_idx == total_frames - 1:
                progress = int((frame_idx + 1) / total_frames * 85)
                message = f"{self._get_random_message('processing_frame')} ({frame_idx + 1}/{total_frames})"
                self.processing_signals.progress_update.emit(progress, message)
                self.processing_signals.frame_update.emit(processed_frame)
            
            frame_idx += 1
        
        # Cleanup
        cap.release()
        out.release()
        self.current_frame_idx = 0
    
    def _process_full_video_thread(self, output_path):
        """Process full video/image in background thread"""
        try:
            self.processing_signals.progress_update.emit(0, self._get_random_message('processing_start'))
            
            with tempfile.TemporaryDirectory() as tmpdir:
                video_no_audio_path = os.path.join(tmpdir, 'video_no_audio.mp4')
                
                if self.mode == "image" or self.mode == "folder":
                    # For folder mode, use first image path for processor initialization
                    # (processor only needs audio duration, we handle images separately)
                    image_path = self.image_path if self.mode == "image" else self.image_list[0]
                    processor = ImageToVideoProcessor(
                        image_path, self.audio_path, fps=self.fps,
                        width=self.width, height=self.height
                    )
                    
                    # Process with progress reporting
                    self._process_image_to_video_with_progress(
                        processor, video_no_audio_path, self.energy_curves, self.frame_times,
                        bass_beat_frames=self.bass_beat_frames,
                        snare_hit_frames=self.snare_hit_frames
                    )
                    
                    self.processing_signals.progress_update.emit(90, self._get_random_message('merging'))
                    self._merge_audio_video(video_no_audio_path, self.audio_path, output_path)
                    
                    self.processing_signals.progress_update.emit(100, self._get_random_message('complete'))
                    QTimer.singleShot(0, lambda: QMessageBox.information(self, "Success", f"Video processed successfully!\n{output_path}"))
                    return
                
                # Video mode processing
                if self.mode == "video" and self.video_path and self.video_cap:
                    self.processing_signals.progress_update.emit(5, self._get_random_message('processing_start'))
                    
                    # Extract audio from original video
                    audio_path = os.path.join(tmpdir, 'extracted_audio.wav')
                    self.processing_signals.progress_update.emit(10, self._get_random_message('audio_extraction'))
                    cmd = ['ffmpeg', '-i', self.video_path, '-q:a', '9', '-y', audio_path]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    
                    if result.returncode != 0:
                        self.processing_signals.progress_update.emit(0, "Error extracting audio from video")
                        QTimer.singleShot(0, lambda: QMessageBox.critical(self, "Error", f"Failed to extract audio:\n{result.stderr}"))
                        return
                    
                    # Process video with progress reporting
                    self._process_video_with_progress(
                        self.video_path, video_no_audio_path, self.energy_curves, self.frame_times,
                        bass_beat_frames=self.bass_beat_frames,
                        snare_hit_frames=self.snare_hit_frames
                    )
                    
                    self.processing_signals.progress_update.emit(90, self._get_random_message('merging'))
                    self._merge_audio_video(video_no_audio_path, audio_path, output_path)
                    
                    self.processing_signals.progress_update.emit(100, self._get_random_message('complete'))
                    QTimer.singleShot(0, lambda: QMessageBox.information(self, "Success", f"Video processed successfully!\n{output_path}"))
                    return
                else:
                    self.processing_signals.progress_update.emit(0, "Error: No video loaded")
                    QTimer.singleShot(0, lambda: QMessageBox.warning(self, "Error", "Please load a video file first"))
        except Exception as e:
            self.processing_signals.progress_update.emit(0, f"Error: {str(e)}")
            QTimer.singleShot(0, lambda msg=str(e): QMessageBox.critical(self, "Error", f"Failed to process video: {msg}"))
    
    def start_webcam(self):
        """Start webcam capture"""
        try:
            self.processing_signals.progress_update.emit(10, self._get_random_message('webcam_starting'))
            
            self.webcam_cap = cv2.VideoCapture(0)
            if not self.webcam_cap.isOpened():
                QMessageBox.critical(self, "Error", "Could not open webcam. Please check if it's available.")
                self.processing_signals.progress_update.emit(0, "Webcam not available")
                return
            
            # Get webcam properties
            self.width = int(self.webcam_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.webcam_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.fps = self.webcam_cap.get(cv2.CAP_PROP_FPS)
            if self.fps <= 0:
                self.fps = 30.0  # Default if webcam doesn't report FPS
            
            self.start_webcam_btn.setEnabled(False)
            self.stop_webcam_btn.setEnabled(True)
            self.record_webcam_btn.setEnabled(True)
            
            status_msg = f"Webcam started: {self.width}x{self.height} @ {self.fps:.1f} FPS"
            if self.energy_curves:
                status_msg += " - Audio-reactive effects active!"
            else:
                status_msg += " - Load audio to enable effects"
            
            self.processing_signals.progress_update.emit(100, status_msg)
            
            # Start webcam capture thread
            self.webcam_thread = threading.Thread(target=self._webcam_capture_loop, daemon=True)
            self.webcam_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start webcam: {str(e)}")
            self.processing_signals.progress_update.emit(0, f"Error: {str(e)}")
    
    def stop_webcam(self):
        """Stop webcam capture"""
        if self.is_recording:
            self.toggle_webcam_recording()  # Stop recording first
        
        # Stop audio playback
        self._stop_audio_playback()
        
        if self.webcam_cap:
            self.webcam_cap.release()
            self.webcam_cap = None
        
        self.start_webcam_btn.setEnabled(True)
        self.stop_webcam_btn.setEnabled(False)
        self.record_webcam_btn.setEnabled(False)
        
        if self.recording_writer:
            self.recording_writer.release()
            self.recording_writer = None
        
        self.current_frame = None
        self.update_preview()
        self.status_label.setText("Webcam stopped")
    
    def _start_audio_playback(self):
        """Start audio playback for webcam recording"""
        if not self.audio_path or not os.path.exists(self.audio_path):
            return
        
        try:
            # Create media player if it doesn't exist
            if self.audio_player is None:
                self.audio_player = QMediaPlayer()
                self.audio_player.positionChanged.connect(self._on_audio_position_changed)
                self.audio_player.durationChanged.connect(self._on_audio_duration_changed)
                self.audio_player.mediaStatusChanged.connect(self._on_audio_status_changed)
            
            # Set media content
            media_content = QMediaContent(QUrl.fromLocalFile(self.audio_path))
            self.audio_player.setMedia(media_content)
            
            # Show audio progress bar
            self.audio_progress_bar.setVisible(True)
            self.audio_time_label.setVisible(True)
            self.audio_loop_label.setVisible(True)
            self.audio_loop_count = 0
            self.audio_loop_label.setText("")
            self.audio_loop_label.setToolTip("Shows loop count when audio repeats during recording")
            
            # Start playback
            self.audio_player.play()
            
        except Exception as e:
            print(f"Error starting audio playback: {e}")
            QMessageBox.warning(self, "Audio Playback", f"Could not start audio playback: {str(e)}")
    
    def _stop_audio_playback(self):
        """Stop audio playback"""
        if self.audio_player:
            self.audio_player.stop()
        
        # Hide audio progress bar
        self.audio_progress_bar.setVisible(False)
        self.audio_time_label.setVisible(False)
        self.audio_loop_label.setVisible(False)
        self.audio_progress_bar.setValue(0)
        self.audio_time_label.setText("0:00 / 0:00")
        self.audio_loop_label.setText("")
        self.audio_loop_count = 0
    
    def _on_audio_position_changed(self, position):
        """Handle audio position changes - update progress bar"""
        if self.audio_player and self.audio_player.duration() > 0:
            progress = int((position / self.audio_player.duration()) * 100)
            self.audio_progress_bar.setValue(progress)
            
            # Update time labels
            current_sec = position // 1000
            total_sec = self.audio_player.duration() // 1000
            current_min = current_sec // 60
            current_sec = current_sec % 60
            total_min = total_sec // 60
            total_sec = total_sec % 60
            
            self.audio_time_label.setText(f"{current_min}:{current_sec:02d} / {total_min}:{total_sec:02d}")
            
            # Detect loop (position resets to near 0)
            if position < 100 and self.audio_loop_count > 0:
                # This might be a new loop, but we'll detect it in status changed
                pass
    
    def _on_audio_duration_changed(self, duration):
        """Handle audio duration changes"""
        if duration > 0:
            self.audio_progress_bar.setMaximum(100)
            total_sec = duration // 1000
            total_min = total_sec // 60
            total_sec = total_sec % 60
            # Duration will be updated in position changed handler
    
    def _on_audio_status_changed(self, status):
        """Handle audio status changes - loop audio if recording is still active"""
        # QMediaPlayer.MediaStatus enum values
        # 0 = NoMedia, 1 = LoadingMedia, 2 = LoadedMedia, 3 = StalledMedia
        # 4 = BufferingMedia, 5 = BufferedMedia, 6 = EndOfMedia, 7 = InvalidMedia
        
        if status == 6:  # EndOfMedia
            # Audio finished - loop if still recording
            if self.is_recording and self.audio_player:
                self.audio_loop_count += 1
                loop_text = f"Loop {self.audio_loop_count + 1}" if self.audio_loop_count > 0 else ""
                QTimer.singleShot(0, lambda text=loop_text: self.audio_loop_label.setText(text))
                QTimer.singleShot(100, lambda: self.audio_player.setPosition(0))
                QTimer.singleShot(150, lambda: self.audio_player.play())
    
    def toggle_webcam_recording(self):
        """Start or stop recording webcam"""
        if not self.is_recording:
            # Start recording
            output_path, _ = QFileDialog.getSaveFileName(
                self, "Save Webcam Recording", "", "MP4 Files (*.mp4);;All Files (*)"
            )
            if not output_path:
                return
            
            # Initialize video writer
            # Use H.264 codec for better compatibility with audio merging
            fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264 codec
            # Fallback to mp4v if avc1 doesn't work
            self.recording_writer = cv2.VideoWriter(
                output_path, fourcc, self.fps, (self.width, self.height)
            )
            if not self.recording_writer.isOpened():
                # Try mp4v as fallback
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                self.recording_writer = cv2.VideoWriter(
                    output_path, fourcc, self.fps, (self.width, self.height)
                )
            
            if not self.recording_writer.isOpened():
                QMessageBox.critical(self, "Error", "Could not initialize video writer")
                return
            
            self.is_recording = True
            self.record_webcam_btn.setText("Stop Recording")
            self.recording_output_path = output_path
            self.recording_start_time = time.time()
            self.recording_frame_count = 0
            
            # Start audio playback if audio is loaded
            if self.audio_path and os.path.exists(self.audio_path):
                self._start_audio_playback()
                message = f"{self._get_random_message('webcam_recording')} - Audio playing - {os.path.basename(output_path)}"
            else:
                message = f"{self._get_random_message('webcam_recording')} - No audio (effects disabled) - {os.path.basename(output_path)}"
            
            self.processing_signals.progress_update.emit(0, message)
        else:
            # Stop recording
            self.is_recording = False
            
            # Stop audio playback first
            self._stop_audio_playback()
            
            # Release video writer and ensure file is finalized
            if self.recording_writer:
                self.recording_writer.release()
                self.recording_writer = None
            
            # Small delay to ensure file is written to disk
            time.sleep(0.5)
            
            self.record_webcam_btn.setText("Start Recording")
            
            # Merge audio if available
            # Note: We'll loop the audio to match video duration
            if hasattr(self, 'recording_output_path') and self.recording_output_path:
                if self.audio_path and os.path.exists(self.audio_path):
                    self.processing_signals.progress_update.emit(90, "Merging audio with recording...")
                    final_output = self.recording_output_path.replace('.mp4', '_with_audio.mp4')
                    
                    # Calculate video duration
                    video_duration = self.recording_frame_count / self.fps
                    
                    try:
                        # Merge audio (will loop if video is longer than audio)
                        self._merge_audio_video_looped(self.recording_output_path, self.audio_path, final_output, video_duration)
                        self.processing_signals.progress_update.emit(100, f"Recording saved: {os.path.basename(final_output)}")
                        QMessageBox.information(self, "Success", f"Recording saved with audio!\n{final_output}")
                    except Exception as e:
                        # If merging fails, still save the video without audio
                        error_msg = f"Failed to merge audio: {str(e)}\n\nVideo saved without audio: {self.recording_output_path}"
                        self.processing_signals.progress_update.emit(100, f"Recording saved (no audio): {os.path.basename(self.recording_output_path)}")
                        QMessageBox.warning(self, "Audio Merge Failed", error_msg)
                else:
                    self.processing_signals.progress_update.emit(100, f"Recording saved: {os.path.basename(self.recording_output_path)}")
                    QMessageBox.information(self, "Success", f"Recording saved!\n{self.recording_output_path}")
    
    def _webcam_capture_loop(self):
        """Webcam capture loop running in background thread"""
        import time
        
        webcam_start_time = time.time()
        
        while self.webcam_cap and self.webcam_cap.isOpened():
            ret, frame = self.webcam_cap.read()
            if not ret:
                break
            
            # Update current frame
            self.current_frame = frame
            
            # Apply effects if audio is loaded and analyzed
            if self.energy_curves is not None and self.audio_duration:
                # Calculate current time based on audio player position if available
                # Otherwise use elapsed time
                if self.audio_player and self.audio_player.duration() > 0:
                    # Use actual audio playback position for perfect sync
                    audio_pos_ms = self.audio_player.position()
                    current_time = (audio_pos_ms / 1000.0) % self.audio_duration
                else:
                    # Fallback: calculate from elapsed time
                    elapsed = time.time() - webcam_start_time
                    current_time = elapsed % self.audio_duration
                
                # Update frame index for effect calculation
                self.current_frame_idx = int(current_time * self.fps)
                
                # Apply effects
                try:
                    processed_frame = self.apply_effects_to_frame(frame.copy())
                except Exception as e:
                    # If effects fail, use original frame
                    processed_frame = frame.copy()
            else:
                # No audio or effects - just show webcam feed
                processed_frame = frame.copy()
            
            # Update preview (thread-safe)
            self.processing_signals.frame_update.emit(processed_frame)
            
            # Write to recording if active
            if self.is_recording and self.recording_writer:
                self.recording_writer.write(processed_frame)
                self.recording_frame_count += 1
                
                # Update status with recording info
                if self.recording_frame_count % 30 == 0:  # Every second
                    duration = self.recording_frame_count / self.fps
                    message = f"{self._get_random_message('webcam_recording')} - {duration:.1f}s"
                    QTimer.singleShot(0, lambda m=message: self.processing_signals.progress_update.emit(
                        int((duration / 60) * 100) if duration < 60 else 99, m
                    ))
            
            # Control frame rate (roughly)
            time.sleep(max(0.001, 1.0 / self.fps - 0.01))  # Small buffer for processing time
    
    def _merge_audio_video(self, video_path, audio_path, output_path):
        """Merge audio and video using ffmpeg"""
        cmd = ['ffmpeg', '-i', video_path, '-i', audio_path, '-c:v', 'copy', '-c:a', 'aac', '-shortest', '-y', output_path]
        subprocess.run(cmd, capture_output=True)
    
    def _merge_audio_video_looped(self, video_path, audio_path, output_path, video_duration):
        """Merge audio and video, looping audio if video is longer"""
        try:
            # Verify files exist
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            # First, get audio duration
            import librosa
            y, sr = librosa.load(audio_path, sr=None)
            audio_duration = len(y) / sr
            
            print(f"Merging audio: video={video_duration:.2f}s, audio={audio_duration:.2f}s")
            
            if video_duration <= audio_duration:
                # Video is shorter or equal - use shortest
                # Re-encode video to ensure compatibility (some codecs don't support audio merging with -c:v copy)
                cmd = [
                    'ffmpeg', '-i', video_path, '-i', audio_path,
                    '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
                    '-c:a', 'aac', '-b:a', '192k',
                    '-map', '0:v:0', '-map', '1:a:0',
                    '-shortest', '-y', output_path
                ]
                print(f"Running: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    raise RuntimeError(f"FFmpeg error: {result.stderr}")
            else:
                # Video is longer - loop audio to match video duration
                # Create a looped audio file first
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_audio:
                    looped_audio_path = tmp_audio.name
                
                # Calculate how many loops needed
                num_loops = int(np.ceil(video_duration / audio_duration))
                print(f"Video longer than audio - creating {num_loops} loops")
                
                # Create looped audio using ffmpeg
                # Use stream_loop to loop the audio
                cmd_loop = [
                    'ffmpeg', '-stream_loop', str(num_loops - 1),
                    '-i', audio_path,
                    '-t', str(video_duration),
                    '-c:a', 'pcm_s16le',  # Ensure WAV format
                    '-y', looped_audio_path
                ]
                print(f"Creating looped audio: {' '.join(cmd_loop)}")
                result_loop = subprocess.run(cmd_loop, capture_output=True, text=True)
                if result_loop.returncode != 0:
                    raise RuntimeError(f"FFmpeg loop error: {result_loop.stderr}")
                
                # Verify looped audio was created
                if not os.path.exists(looped_audio_path):
                    raise RuntimeError("Failed to create looped audio file")
                
                # Merge with video
                # Re-encode video to ensure compatibility (some codecs don't support audio merging with -c:v copy)
                cmd = [
                    'ffmpeg', '-i', video_path, '-i', looped_audio_path,
                    '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
                    '-c:a', 'aac', '-b:a', '192k',
                    '-map', '0:v:0', '-map', '1:a:0',
                    '-shortest', '-y', output_path
                ]
                print(f"Merging with looped audio: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    raise RuntimeError(f"FFmpeg merge error: {result.stderr}")
                
                # Clean up temporary file
                try:
                    os.unlink(looped_audio_path)
                except:
                    pass
            
            # Verify output file was created
            if not os.path.exists(output_path):
                raise RuntimeError(f"Output file was not created: {output_path}")
            
            print(f"Successfully merged audio: {output_path}")
            
        except Exception as e:
            error_msg = f"Error merging audio: {str(e)}"
            print(error_msg)
            QMessageBox.critical(self, "Audio Merge Error", error_msg)
            raise


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    print("Creating PyQt5 GUI...")
    window = SoundReactiveGUI()
    window.show()
    
    print("Starting event loop...")
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
