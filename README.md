# Video Transcript Extractor

A Python project to extract transcripts from video files (MP4, AVI, etc.) using Vosk speech recognition. Works completely offline!

## Prerequisites

- Python 3.7+
- ffmpeg (required for audio extraction)

The project includes a static ffmpeg build in `~/ffmpeg/` directory, so no system installation is needed.

## Installation

1. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Download a Vosk model (automatically done for English):
```bash
# The script will download the small English model automatically
# Or download manually from: https://alphacephei.com/vosk/models
```

## Usage

Basic usage:
```bash
python transcribe.py <video_file>
```

With custom model path:
```bash
python transcribe.py <video_file> [model_path]
```

## Examples

Transcribe with default settings:
```bash
python transcribe.py "Project Otter Walkthrough Webinar.mp4"
```

Transcribe with a different model:
```bash
python transcribe.py "video.mp4" vosk-model-small-en-us-0.15
```

## Available Models

Download models from https://alphacephei.com/vosk/models:

- `vosk-model-small-en-us-0.15` - Small English model (~40MB) - Good balance
- `vosk-model-en-us-0.22` - Full English model (~1.8GB) - Best accuracy
- Various other languages available (Spanish, French, German, etc.)

## Notes

- Works completely offline (no internet required after model download)
- Processing time depends on video length and model size
- Output is saved as plain text file
- Video files are converted to audio locally
- First run will download the model automatically
