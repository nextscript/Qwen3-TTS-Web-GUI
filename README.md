# Qwen3-TTS Web GUI

A modern web GUI for text-to-speech using the **Qwen3-TTS-12Hz-1.7B-CustomVoice** model.

## Features

* 🎙️ Text-to-speech with 9 different voices
* 🌍 Support for more than 10 languages, including German, English, Chinese, Japanese, Korean, and French
* 🎛️ Natural-language voice instructions for controlling tone and emotion
* ▶️ Direct audio playback in the browser
* 💾 Download generated audio as a WAV file
* 📜 History with saved entries
* 🌙 Modern dark design built with Bootstrap 5

## Requirements

* Python 3.10 or newer
* GPU recommended, but CPU execution is also supported
* Approximately 4–8 GB of RAM

## Installation

```bash
# Create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

```bash
python app.py
```

The web GUI will then be available at **http://localhost:5000**.

## Model

This project uses the following model:

**Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice**

[🔗 View on Hugging Face](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice)

### Available Speakers

| Speaker  | Description                                                                |
| -------- | -------------------------------------------------------------------------- |
| Vivian   | Bright, slightly husky female voice speaking Chinese                       |
| Serena   | Warm and gentle female voice speaking Chinese                              |
| Uncle_Fu | Mature male voice with a deep and rich tone, speaking Chinese              |
| Dylan    | Young male voice from Beijing, speaking Chinese with a Beijing dialect     |
| Eric     | Energetic male voice from Chengdu, speaking Chinese with a Sichuan dialect |
| Ryan     | Dynamic male voice with a strong sense of rhythm, speaking English         |
| Aiden    | Friendly American male voice speaking English                              |
| Ono_Anna | Playful Japanese female voice speaking Japanese                            |
| Sohee    | Warm Korean female voice speaking Korean                                   |
