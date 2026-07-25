<img src="https://raw.githubusercontent.com/nextscript/Qwen3-TTS-Web-GUI/refs/heads/main/screenshot.png">

# Qwen3-TTS Web GUI

A web-based text-to-speech application powered by [Qwen3-TTS](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice) with GPU acceleration.

## Features

- **GPU Accelerated** — Automatic CUDA 13.2 PyTorch installation for RTX 50xx series (sm_120) with fallback to CUDA 12.4
- **Multi-Language Support** — Auto-detection, Chinese, English, Japanese, Korean, German, French, Russian, Portuguese, Spanish, Italian
- **Custom Voice Control** — 9 speakers with natural voice characteristics
- **Optional Instructions** — Control voice style (deep voice, whisper, shout, etc.)
- **Live History** — Real-time history updates after each generation
- **Dark Theme** — Modern Bootstrap 5 dark UI
- **WAV Output** — High-quality audio output with instant playback
- **Auto-Cleanup** — Automatically removes stale entries from history when files are deleted

## System Requirements

- **GPU**: NVIDIA GPU with CUDA 13.2 support (RTX 50xx series recommended)
- **OS**: Windows 11, Linux
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 20GB free space (model cache + generated audio)

## Quick Start

### 1. Run the Launcher

```bash
start.bat
```

The launcher will automatically:
1. Create a virtual environment if needed
2. Install GPU PyTorch (CUDA 13.2 for RTX 50xx, fallback to CUDA 12.4)
3. Install all dependencies
4. Start the Flask server at `http://localhost:5000`

### 2. Open the Web GUI

Navigate to **http://localhost:5000** in your browser.

## Usage

1. **Enter Speech Text** — Type or paste the text you want to synthesize
2. **Select Speaker** — Choose from 9 available voices
3. **Select Language** — Auto-detect or specify manually
4. **Optional Instruction** — Control voice style (e.g., "speak in a deep voice", "whisper")
5. Click **Generate** to synthesize audio

### Available Speakers

| Speaker | Description | Language |
|---------|-------------|----------|
| Vivian | Bright, slightly edgy young female voice | Chinese |
| Serena | Warm, gentle young female voice | Chinese |
| Uncle_Fu | Seasoned male voice with low, mellow timbre | Chinese |
| Dylan | Youthful Beijing male voice, clear and natural | Chinese (Beijing Dialect) |
| Eric | Lively Chengdu male voice, slightly husky brightness | Chinese (Sichuan Dialect) |
| Ryan | Dynamic male voice with strong rhythmic drive | English |
| Aiden | Sunny American male voice with clear midrange | English |
| Ono_Anna | Playful Japanese female voice, light and nimble | Japanese |
| Sohee | Warm Korean female voice with rich emotion | Korean |

### Voice Instructions (Optional)

| Instruction | Effect |
|-------------|--------|
| `speak in a deep voice` | Lower, deeper voice |
| `speak softly` | Gentle, quiet speech |
| `speak angrily` | Angry tone |
| `speak happily` | Happy, upbeat tone |
| `whisper` | Whispered speech |
| `shout` | Loud, shouting speech |
| `speak slowly` | Slow speech rate |
| `speak quickly` | Fast speech rate |


### DEMO Audio
[Uncle_Fu-DEMO.wav](https://gabalpha.github.io/read-audio/?p=https://github.com/user-attachments/files/30366876/Uncle_Fu-DEMO.wav)

[Serena-DEMO.wav](https://gabalpha.github.io/read-audio/?p=https://github.com/user-attachments/files/30366877/Serena-DEMO.wav)



Instructions must be written as complete sentences.

## Project Structure

```
text2speece/
├── app.py                  # Flask backend (GPU PyTorch, TTS generation)
├── launcher.py             # Auto-installer (GPU PyTorch + dependencies)
├── requirements.txt        # Python dependencies
├── start.bat               # Windows launcher
├── start.sh                # Linux/macOS launcher
├── templates/
│   └── index.html          # Web UI (English)
├── static/
│   ├── style.css           # Dark theme styles
│   └── app.js              # Frontend logic (live history, generation)
├── output/                 # Generated WAV files + history.json
├── hf_cache/               # HuggingFace model cache
└── venv/                   # Virtual environment
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TTS_MODEL_PATH` | `Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice` | HuggingFace model path |
| `HF_HOME` | `./hf_cache` | HuggingFace cache directory |

### Changing the Model

Set `TTS_MODEL_PATH` before running:

```bash
set TTS_MODEL_PATH=Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice
start.bat
```

## Troubleshooting

### GPU not detected

The launcher automatically tries CUDA 13.2 first (for RTX 50xx), then falls back to CUDA 12.4. If both fail, check:

1. NVIDIA drivers are up to date
2. CUDA toolkit is installed
3. GPU is compatible (compute capability >= 5.0)

### Slow generation

Ensure GPU PyTorch is installed (not CPU-only). Check the console output on startup:

```
[GPU-PyTorch] Installing PyTorch with GPU support...
[OK] GPU PyTorch installed
```

### History shows deleted files

The backend automatically cleans `history.json` on each request, removing entries for files that no longer exist on disk.

## Technology Stack

- **Backend**: Flask + PyTorch (CUDA 13.2) + Qwen3-TTS
- **Frontend**: Bootstrap 5 + Bootstrap Icons
- **Audio**: soundfile (libsndfile)
- **Model**: Qwen3-TTS-12Hz-1.7B-CustomVoice (HuggingFace)
