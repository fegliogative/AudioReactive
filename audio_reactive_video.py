#!/usr/bin/env python3
"""
Audio-Reactive Video Generator (Enhanced)
Analyzes audio frequencies and applies dynamic visual effects to video
Supports both legacy peak-based and enhanced continuous reactivity modes

Usage:
    # Legacy mode (peak-based effects)
    python3 audio_reactive_video.py input.mp4 output.mp4
    
    # Enhanced mode (continuous reactivity)
    python3 audio_reactive_video.py input.mp4 output.mp4 --enhanced
    
    # Enhanced with custom parameters
    python3 audio_reactive_video.py input.mp4 output.mp4 --enhanced --zoom 1.5 --rotation 8 --enable-color-grading
"""

import argparse
import sys
import os
from pathlib import Path
from audio_analysis import AudioAnalyzer
from video_processor import VideoProcessor
from image_to_video import ImageToVideoProcessor
import tempfile


def extract_audio(video_path: str, audio_path: str) -> None:
    """Extract audio from video using ffmpeg"""
    import subprocess
    
    print(f"Extracting audio from video...")
    cmd = [
        'ffmpeg', '-i', video_path, '-q:a', '9', '-n', audio_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error extracting audio: {result.stderr}")
        raise RuntimeError("Failed to extract audio")


def merge_audio_video(video_path: str, audio_path: str, output_path: str) -> None:
    """Merge processed video with original audio using ffmpeg"""
    import subprocess
    
    print(f"Merging video with original audio...")
    cmd = [
        'ffmpeg', '-i', video_path, '-i', audio_path,
        '-c:v', 'copy', '-c:a', 'aac', '-map', '0:v:0', '-map', '1:a:0',
        '-y', output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error merging audio: {result.stderr}")
        raise RuntimeError("Failed to merge audio")


def main():
    parser = argparse.ArgumentParser(
        description="Generate audio-reactive video with dynamic visual effects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Legacy mode (peak-based effects)
  python3 audio_reactive_video.py input.mp4 output.mp4
  
  # Enhanced mode (continuous reactivity)
  python3 audio_reactive_video.py input.mp4 output.mp4 --enhanced
  
  # Enhanced with custom zoom and rotation
  python3 audio_reactive_video.py input.mp4 output.mp4 --enhanced --zoom 1.5 --rotation 8
  
  # Enhanced with all effects enabled
  python3 audio_reactive_video.py input.mp4 output.mp4 --enhanced --enable-color-grading --enable-blur --enable-brightness
  
  # Custom frequency ranges (legacy mode)
  python3 audio_reactive_video.py input.mp4 output.mp4 --bass-range 30 120 --treble-range 2000 10000
  
  # Enhanced with custom intensity sensitivity
  python3 audio_reactive_video.py input.mp4 output.mp4 --enhanced --intensity-sensitivity 0.9 --smoothness 0.8
        """
    )
    
    parser.add_argument('input', help='Input video file (MP4) or image file (PNG, JPG)')
    parser.add_argument('output', help='Output video file (MP4)')
    parser.add_argument(
        '--audio', type=str, default=None,
        help='Audio file (MP3, WAV) - required when input is an image'
    )
    parser.add_argument(
        '--image-mode', action='store_true',
        help='Enable image-to-video mode (requires --audio)'
    )
    parser.add_argument(
        '--fps', type=float, default=30.0,
        help='Output video frame rate for image mode (default: 30.0)'
    )
    parser.add_argument(
        '--width', type=int, default=None,
        help='Output video width for image mode (default: image width)'
    )
    parser.add_argument(
        '--height', type=int, default=None,
        help='Output video height for image mode (default: image height)'
    )
    
    # Mode selection
    parser.add_argument(
        '--enhanced', action='store_true',
        help='Use enhanced mode with continuous frequency reactivity and multi-band analysis'
    )
    
    # Basic effect parameters (work in both modes)
    parser.add_argument(
        '--zoom', type=float, default=1.3,
        help='Zoom factor for bass effects (default: 1.3)'
    )
    parser.add_argument(
        '--rotation', type=float, default=5.0,
        help='Rotation angle in degrees for treble effects (default: 5.0)'
    )
    
    # Legacy mode parameters
    parser.add_argument(
        '--duration', type=float, default=0.5,
        help='Effect duration in seconds for legacy mode (default: 0.5)'
    )
    parser.add_argument(
        '--bass-range', type=int, nargs=2, default=[40, 100],
        metavar=('MIN', 'MAX'),
        help='Bass frequency range in Hz for legacy mode (default: 40 100)'
    )
    parser.add_argument(
        '--treble-range', type=int, nargs=2, default=[3000, 8000],
        metavar=('MIN', 'MAX'),
        help='Treble frequency range in Hz for legacy mode (default: 3000 8000)'
    )
    
    # Enhanced mode: Frequency band ranges
    parser.add_argument(
        '--sub-bass-range', type=int, nargs=2, default=[20, 60],
        metavar=('MIN', 'MAX'),
        help='Sub-bass frequency range in Hz (default: 20 60)'
    )
    parser.add_argument(
        '--bass-range-enhanced', type=int, nargs=2, default=[60, 250],
        metavar=('MIN', 'MAX'),
        help='Bass frequency range in Hz for enhanced mode (default: 60 250)'
    )
    parser.add_argument(
        '--mid-range', type=int, nargs=2, default=[250, 2000],
        metavar=('MIN', 'MAX'),
        help='Mid frequency range in Hz (default: 250 2000)'
    )
    parser.add_argument(
        '--treble-range-enhanced', type=int, nargs=2, default=[2000, 6000],
        metavar=('MIN', 'MAX'),
        help='Treble frequency range in Hz for enhanced mode (default: 2000 6000)'
    )
    parser.add_argument(
        '--high-treble-range', type=int, nargs=2, default=[6000, 12000],
        metavar=('MIN', 'MAX'),
        help='High-treble frequency range in Hz (default: 6000 12000)'
    )
    
    # Enhanced mode: Band contributions
    parser.add_argument(
        '--sub-bass-zoom', type=float, default=0.2,
        help='Sub-bass contribution to zoom (0.0-1.0, default: 0.2)'
    )
    parser.add_argument(
        '--bass-zoom', type=float, default=1.0,
        help='Bass contribution to zoom (0.0-1.0, default: 1.0)'
    )
    parser.add_argument(
        '--treble-rotation', type=float, default=1.0,
        help='Treble contribution to rotation (0.0-1.0, default: 1.0)'
    )
    parser.add_argument(
        '--high-treble-rotation', type=float, default=0.5,
        help='High-treble contribution to rotation (0.0-1.0, default: 0.5)'
    )
    parser.add_argument(
        '--mid-hue-shift', type=float, default=30.0,
        help='Maximum hue shift in degrees for mid-range (default: 30.0)'
    )
    
    # Enhanced mode: Advanced effects
    parser.add_argument(
        '--enable-color-grading', action='store_true',
        help='Enable frequency-based color grading (hue shift, saturation)'
    )
    parser.add_argument(
        '--enable-blur', action='store_true',
        help='Enable motion blur on strong bass hits'
    )
    parser.add_argument(
        '--enable-brightness', action='store_true',
        help='Enable brightness pulsing with frequency energy'
    )
    
    # Enhanced mode: Reactivity parameters
    parser.add_argument(
        '--intensity-sensitivity', type=float, default=0.7,
        help='How sensitive effects are to intensity (0.0-1.0, default: 0.7)'
    )
    parser.add_argument(
        '--smoothness', type=float, default=0.8,
        help='Interpolation smoothness (0.0=linear, 1.0=very smooth, default: 0.8)'
    )
    
    # Audio parameters
    parser.add_argument(
        '--sr', type=int, default=22050,
        help='Audio sample rate in Hz (default: 22050)'
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found")
        sys.exit(1)
    
    # Check if input is an image
    image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}
    input_ext = os.path.splitext(args.input.lower())[1]
    is_image = input_ext in image_extensions
    
    # If image, require audio file
    if is_image or args.image_mode:
        if not args.audio:
            print("Error: --audio is required when input is an image or --image-mode is enabled")
            sys.exit(1)
        if not os.path.exists(args.audio):
            print(f"Error: Audio file '{args.audio}' not found")
            sys.exit(1)
    
    if os.path.exists(args.output):
        response = input(f"Output file '{args.output}' already exists. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            sys.exit(0)
    
    # Validate parameters
    if args.zoom < 1.0:
        print("Error: Zoom factor must be >= 1.0")
        sys.exit(1)
    
    if not args.enhanced:
        # Legacy mode validations
        if args.duration <= 0:
            print("Error: Effect duration must be > 0")
            sys.exit(1)
        
        if args.bass_range[0] >= args.bass_range[1]:
            print("Error: Bass range min must be less than max")
            sys.exit(1)
        
        if args.treble_range[0] >= args.treble_range[1]:
            print("Error: Treble range min must be less than max")
            sys.exit(1)
    else:
        # Enhanced mode validations
        if args.intensity_sensitivity < 0.0 or args.intensity_sensitivity > 1.0:
            print("Error: Intensity sensitivity must be between 0.0 and 1.0")
            sys.exit(1)
        
        if args.smoothness < 0.0 or args.smoothness > 1.0:
            print("Error: Smoothness must be between 0.0 and 1.0")
            sys.exit(1)
    
    try:
        # Create temporary directory for intermediate files
        with tempfile.TemporaryDirectory() as tmpdir:
            print("\n" + "="*60)
            if is_image or args.image_mode:
                print("AUDIO-REACTIVE IMAGE-TO-VIDEO GENERATOR")
            elif args.enhanced:
                print("AUDIO-REACTIVE VIDEO GENERATOR (ENHANCED MODE)")
            else:
                print("AUDIO-REACTIVE VIDEO GENERATOR (LEGACY MODE)")
            print("="*60 + "\n")
            
            # Handle image mode
            if is_image or args.image_mode:
                audio_path = args.audio
                video_no_audio_path = os.path.join(tmpdir, 'video_no_audio.mp4')
                
                # Step 1: Analyze audio
                print("\n--- Audio Analysis ---")
                analyzer = AudioAnalyzer(audio_path, sr=args.sr)
                energy_curves, frame_times = analyzer.analyze_enhanced(
                    sub_bass_range=tuple(args.sub_bass_range),
                    bass_range=tuple(args.bass_range_enhanced),
                    mid_range=tuple(args.mid_range),
                    treble_range=tuple(args.treble_range_enhanced),
                    high_treble_range=tuple(args.high_treble_range)
                )
                
                bass_beat_frames = analyzer.bass_beat_frames if hasattr(analyzer, 'bass_beat_frames') else None
                snare_hit_frames = analyzer.snare_hit_frames if hasattr(analyzer, 'snare_hit_frames') else None
                
                print(f"Energy curves computed for {len(energy_curves)} frequency bands")
                
                # Step 2: Process image to video
                print("\n--- Image-to-Video Processing ---")
                processor = ImageToVideoProcessor(
                    args.input,
                    audio_path,
                    fps=args.fps,
                    width=args.width,
                    height=args.height
                )
                processor.process_image_to_video(
                    video_no_audio_path,
                    energy_curves,
                    frame_times,
                    bass_beat_frames=bass_beat_frames,
                    snare_hit_frames=snare_hit_frames,
                    zoom_factor=args.zoom,
                    rotation_angle=args.rotation,
                    sub_bass_zoom=args.sub_bass_zoom,
                    bass_zoom=args.bass_zoom,
                    treble_rotation=args.treble_rotation,
                    high_treble_rotation=args.high_treble_rotation,
                    mid_hue_shift=args.mid_hue_shift,
                    enable_color_grading=args.enable_color_grading,
                    enable_blur=args.enable_blur,
                    enable_brightness=args.enable_brightness,
                    enable_glitch=args.enable_glitch if hasattr(args, 'enable_glitch') else False,
                    enable_artifacts=args.enable_artifacts if hasattr(args, 'enable_artifacts') else False,
                    beat_triggered_zoom=True,
                    beat_window=0.2,
                    snare_triggered_flash=True,
                    snare_window=0.15,
                    intensity_sensitivity=args.intensity_sensitivity,
                    smoothness=args.smoothness
                )
                
                # Step 3: Merge audio with video
                print("\n--- Audio Merge ---")
                merge_audio_video(video_no_audio_path, audio_path, args.output)
                
                print("\n" + "="*60)
                print("SUCCESS!")
                print(f"Output video saved to: {args.output}")
                print("="*60 + "\n")
                return
            
            # Video mode (existing code)
            audio_path = os.path.join(tmpdir, 'extracted_audio.wav')
            video_no_audio_path = os.path.join(tmpdir, 'video_no_audio.mp4')
            
            # Step 1: Extract audio
            extract_audio(args.input, audio_path)
            
            # Step 2: Analyze audio
            print("\n--- Audio Analysis ---")
            analyzer = AudioAnalyzer(audio_path, sr=args.sr)
            
            if args.enhanced:
                # Enhanced mode: Multi-band analysis with continuous energy curves
                energy_curves, frame_times = analyzer.analyze_enhanced(
                    sub_bass_range=tuple(args.sub_bass_range),
                    bass_range=tuple(args.bass_range_enhanced),
                    mid_range=tuple(args.mid_range),
                    treble_range=tuple(args.treble_range_enhanced),
                    high_treble_range=tuple(args.high_treble_range)
                )
                
                # Get beat frames
                bass_beat_frames = analyzer.bass_beat_frames if hasattr(analyzer, 'bass_beat_frames') else None
                snare_hit_frames = analyzer.snare_hit_frames if hasattr(analyzer, 'snare_hit_frames') else None
                
                print(f"Energy curves computed for {len(energy_curves)} frequency bands")
                
            else:
                # Legacy mode: Peak-based analysis
                bass_frames, treble_frames, frame_times = analyzer.analyze(
                    bass_freq_range=tuple(args.bass_range),
                    treble_freq_range=tuple(args.treble_range)
                )
            
            # Step 3: Process video
            print("\n--- Video Processing ---")
            processor = VideoProcessor(args.input)
            
            if args.enhanced:
                # Enhanced mode: Continuous reactivity with beat-triggered zoom
                processor.process_video_enhanced(
                    video_no_audio_path,
                    energy_curves,
                    frame_times,
                    bass_beat_frames=bass_beat_frames,
                    snare_hit_frames=snare_hit_frames,
                    zoom_factor=args.zoom,
                    rotation_angle=args.rotation,
                    sub_bass_zoom=args.sub_bass_zoom,
                    bass_zoom=args.bass_zoom,
                    treble_rotation=args.treble_rotation,
                    high_treble_rotation=args.high_treble_rotation,
                    mid_hue_shift=args.mid_hue_shift,
                    enable_color_grading=args.enable_color_grading,
                    enable_blur=args.enable_blur,
                    enable_brightness=args.enable_brightness,
                    enable_glitch=args.enable_glitch if hasattr(args, 'enable_glitch') else False,
                    enable_artifacts=args.enable_artifacts if hasattr(args, 'enable_artifacts') else False,
                    beat_triggered_zoom=True,  # Default: beat-triggered zoom
                    beat_window=0.2,
                    snare_triggered_flash=True,  # Default: snare-triggered flash
                    snare_window=0.15,
                    intensity_sensitivity=args.intensity_sensitivity,
                    smoothness=args.smoothness
                )
            else:
                # Legacy mode: Peak-based effects
                processor.process_video(
                    video_no_audio_path,
                    bass_frames,
                    treble_frames,
                    frame_times,
                    zoom_factor=args.zoom,
                    rotation_angle=args.rotation,
                    effect_duration=args.duration
                )
            
            processor.close()
            
            # Step 4: Merge audio back
            print("\n--- Audio Merge ---")
            merge_audio_video(video_no_audio_path, audio_path, args.output)
            
            print("\n" + "="*60)
            print("SUCCESS!")
            print(f"Output video saved to: {args.output}")
            if args.enhanced:
                print("\nEnhanced features used:")
                if args.enable_color_grading:
                    print("  ✓ Color grading")
                if args.enable_blur:
                    print("  ✓ Motion blur")
                if args.enable_brightness:
                    print("  ✓ Brightness pulsing")
                print(f"  ✓ Multi-band frequency analysis")
                print(f"  ✓ Continuous reactivity")
                print(f"  ✓ Intensity-based effects")
            print("="*60 + "\n")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
