# YouTube Auto SRT Generator

New algorithm using WhisperHallu and WhisperTimeSync: The lyrics in the output file will be the same as the input lyrics file, only the timestamps will be synchronized.

## Features

- Download audio from YouTube videos
- Generate accurate SRT subtitle files with synchronized timestamps
- Use your own lyrics file for precise transcription
- Support multiple Whisper model sizes (tiny, base, small, medium, large)

## Prerequisites

- Python 3.11+
- Virtual environment (venv)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/lengoc-tuyen/Youtube-Auto-SRT-Generator.git
cd Youtube-Auto-SRT-Generator
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv_alignment
source venv_alignment/bin/activate  # On macOS/Linux
# or
venv_alignment\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Setup WhisperTimeSync virtual environment:
```bash
cd WhisperTimeSync
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # If there's a requirements file
deactivate
cd ..
```

## Usage

1. Prepare your lyrics file:
   - Create a text file in `subtitles_output/` folder (e.g., `ifonly.txt`)
   - Add your song lyrics (one line per phrase/verse)
   - Update `LYRICS_FILE_NAME` in `main.py` if needed

2. Run the program:
```bash
python main.py
```

3. Enter the YouTube URL when prompted

4. The program will:
   - Download audio from YouTube
   - Run WhisperHallu to create timing source
   - Run WhisperTimeSync to align your lyrics with audio
   - Generate an SRT file with accurate timestamps

## Configuration

Edit `main.py` to configure:

- `OUTPUT_DIR`: Output directory for subtitle files (default: `subtitles_output`)
- `MODEL_SIZE`: Whisper model size (default: `small`)
  - `tiny`: ~1GB RAM, fast, low accuracy
  - `base`: ~1GB RAM, fast, decent accuracy
  - `small`: ~2GB RAM, medium speed, good accuracy
  - `medium`: ~5GB RAM, slow, very good accuracy
  - `large`: ~10GB RAM, very slow, excellent accuracy
- `LYRICS_FILE_NAME`: Name of your lyrics file (default: `ifonly.txt`)

## How It Works

1. **Download**: Downloads audio from YouTube video
2. **WhisperHallu**: Creates word-level timing source
3. **WhisperTimeSync**: Aligns your provided lyrics with the audio using the timing source
4. **Output**: Generates SRT file with your exact lyrics and synchronized timestamps

## Project Structure

```
makeSRT/
├── main.py                 # Main program
├── requirements.txt        # Python dependencies
├── WhisperHallu/          # WhisperHallu tool for timing
├── WhisperTimeSync/       # WhisperTimeSync tool for alignment
└── subtitles_output/      # Output folder for SRT files
```

## Output

The final SRT file will be saved in the `subtitles_output/` folder with the format:
```
<video_title>_aligned.srt
```

## Troubleshooting

- **Out of Memory Error**: Use a smaller model size (e.g., `tiny` or `base`)
- **Lyrics file not found**: Make sure your lyrics file exists in `subtitles_output/` folder
- **WhisperTimeSync error**: Ensure WhisperTimeSync's venv is properly set up

## Credits

- [WhisperHallu](https://github.com/your-whisperhallu-repo)
- [WhisperTimeSync](https://github.com/your-whispersync-repo)
- [OpenAI Whisper](https://github.com/openai/whisper)

## License

[Your License Here]
