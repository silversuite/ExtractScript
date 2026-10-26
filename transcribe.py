#!/usr/bin/env python3
"""
Video Transcript Extractor using Vosk
Extracts transcripts from video files (mp4, avi, etc.) - Works offline!
"""

import sys
import os
import wave
import json
import re
from pathlib import Path
import tempfile
from pydub import AudioSegment
from vosk import Model, KaldiRecognizer

# Add ffmpeg to PATH if it's in the user's home directory
ffmpeg_path = os.path.expanduser("~/ffmpeg/ffmpeg-git-20240629-amd64-static")
if os.path.exists(ffmpeg_path):
    os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ.get("PATH", "")
    AudioSegment.converter = os.path.join(ffmpeg_path, "ffmpeg")


def add_punctuation(segments, total_duration):
    """
    Add punctuation based on segment boundaries (natural speech pauses)
    Merge segments to create more natural sentences
    """
    print("Adding punctuation to transcript...")
    
    if not segments:
        return ""
    
    # Merge segments into longer sentences (target 15-20 words per sentence)
    merged_segments = []
    current_text = ""
    current_words = 0
    
    for segment in segments:
        text = segment['text'].strip()
        if not text:
            continue
        
        word_count = len(text.split())
        
        # If adding this would make the sentence too long, start a new one
        if current_words + word_count > 20 and current_words > 8:
            merged_segments.append(current_text)
            current_text = text
            current_words = word_count
        else:
            # Merge with current
            if current_text:
                current_text += " " + text
            else:
                current_text = text
            current_words += word_count
    
    # Don't forget the last one
    if current_text:
        merged_segments.append(current_text)
    
    # Now add punctuation to merged segments
    result_sentences = []
    
    for i, text in enumerate(merged_segments):
        if not text:
            continue
        
        # Capitalize first letter
        text = text[0].upper() + text[1:] if text else text
        
        # Check if next segment starts with a question word
        if i < len(merged_segments) - 1:
            next_text = merged_segments[i + 1].strip().lower()
            first_word = next_text.split()[0] if next_text else ""
            question_words = {'what', 'where', 'when', 'why', 'how', 'who', 'which', 'whose', 'whom'}
            
            if first_word in question_words:
                text = text + '?'
            else:
                text = text + '.'
        else:
            # Last segment
            text = text + '.'
        
        result_sentences.append(text)
    
    return '\n'.join(result_sentences)


def transcribe_video(video_path, model_path="model", add_punct=True):
    """
    Transcribe a video file using Vosk (offline)
    
    Args:
        video_path: Path to the video file
        model_path: Path to Vosk model directory
        add_punct: Whether to add punctuation to the transcript
    """
    if not os.path.exists(video_path):
        print(f"Error: Video file not found: {video_path}")
        sys.exit(1)
    
    if not os.path.exists(model_path):
        print(f"Error: Vosk model not found at: {model_path}")
        print("\nPlease download a model from:")
        print("https://alphacephei.com/vosk/models")
        print("\nDownload and extract to the current directory as 'model'")
        print("For English: https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip")
        sys.exit(1)
    
    print(f"Processing video: {video_path}")
    print("Extracting audio from video...")
    
    # Extract audio from video using pydub
    try:
        audio = AudioSegment.from_file(video_path)
    except Exception as e:
        print(f"Error reading video file: {e}")
        print("Make sure ffmpeg is installed on your system")
        sys.exit(1)
    
    # Convert to WAV format (mono, 16kHz for Vosk)
    print("Converting audio to WAV format (mono, 16kHz)...")
    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(16000)
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
        temp_path = temp_audio.name
        audio.export(temp_path, format="wav")
    
    try:
        # Load Vosk model
        print(f"Loading Vosk model from: {model_path}")
        model = Model(model_path)
        
        # Setup recognizer
        rec = KaldiRecognizer(model, 16000)
        
        print("Transcribing...")
        print("This may take a while depending on video length...")
        
        # Process audio file
        wf = wave.open(temp_path, "rb")
        
        segments = []
        
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                if "text" in result and result["text"].strip():
                    segments.append(result)
        
        # Get final result
        final_result = json.loads(rec.FinalResult())
        if "text" in final_result and final_result["text"].strip():
            segments.append(final_result)
        
        wf.close()
        
        # Build text from segments
        result_text = " ".join([s["text"] for s in segments]).strip()
        
        # Add punctuation if requested
        if add_punct and segments:
            result_text = add_punctuation(segments, len(audio) / 1000)
        
        # Generate output filename
        video_name = Path(video_path).stem
        output_file = f"{video_name}_transcript.txt"
        
        # Save transcript
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result_text)
        
        print(f"\nTranscription complete!")
        print(f"Output saved to: {output_file}")
        print(f"Audio duration: {len(audio) / 1000:.2f} seconds")
        print(f"Transcript length: {len(result_text)} characters")
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <video_file> [model_path] [--no-punct]")
        print("\nExample: python transcribe.py video.mp4")
        print("Example: python transcribe.py video.mp4 model")
        print("Example: python transcribe.py video.mp4 model --no-punct")
        sys.exit(1)
    
    video_path = sys.argv[1]
    model_path = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else "model"
    add_punct = "--no-punct" not in sys.argv
    
    transcribe_video(video_path, model_path, add_punct)
