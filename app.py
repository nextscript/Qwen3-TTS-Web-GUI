"""
Qwen3-TTS Web GUI Backend
Flask server for text-to-speech with model marketplace
"""

import io
import os
import sys
import json
import base64
import uuid
import time
import torch
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from qwen_tts import Qwen3TTSModel
import soundfile as sf

# Redirect ALL HuggingFace caching to project folder
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HF_CACHE_DIR = os.path.join(SCRIPT_DIR, "hf_cache")
os.makedirs(HF_CACHE_DIR, exist_ok=True)
os.makedirs(os.path.join(HF_CACHE_DIR, "hub"), exist_ok=True)

# Output directory for generated audio
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Set HF_HOME before any huggingface imports
os.environ["HF_HOME"] = HF_CACHE_DIR

# Remove old cache in user home if it exists
old_cache = os.path.expanduser("~/.cache/huggingface/hub")
if os.path.exists(old_cache):
    try:
        import shutil
        print(f"\n[INFO] Removing old HuggingFace cache: {old_cache}")
        shutil.rmtree(old_cache)
        print("[OK] Old cache removed")
    except Exception as e:
        print(f"[WARN] Could not remove old cache: {e}")

# Also remove old transformers cache
old_transformers_cache = os.path.expanduser("~/.cache/huggingface/transformers")
if os.path.exists(old_transformers_cache):
    try:
        import shutil
        print(f"\n[INFO] Removing old transformers cache: {old_transformers_cache}")
        shutil.rmtree(old_transformers_cache)
        print("[OK] Old transformers cache removed")
    except Exception as e:
        print(f"[WARN] Could not remove old transformers cache: {e}")

app = Flask(__name__)
CORS(app)

# Current model configuration
current_model_config = {
    "path": os.environ.get("TTS_MODEL_PATH", "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice"),
    "name": "Qwen3-TTS-12Hz-1.7B-CustomVoice",
    "type": "CustomVoice",
    "speakers": {
        "Vivian": "Bright, slightly edgy young female voice (Chinese)",
        "Serena": "Warm, gentle young female voice (Chinese)",
        "Uncle_Fu": "Seasoned male voice with low, mellow timbre (Chinese)",
        "Dylan": "Youthful Beijing male voice, clear and natural (Chinese, Beijing Dialect)",
        "Eric": "Lively Chengdu male voice, slightly husky brightness (Chinese, Sichuan Dialect)",
        "Ryan": "Dynamic male voice with strong rhythmic drive (English)",
        "Aiden": "Sunny American male voice with clear midrange (English)",
        "Ono_Anna": "Playful Japanese female voice, light and nimble (Japanese)",
        "Sohee": "Warm Korean female voice with rich emotion (Korean)",
    },
    "languages": ["Auto", "Chinese", "English", "Japanese", "Korean", "German", "French", "Russian", "Portuguese", "Spanish", "Italian"],
}

model = None
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float16


def load_model():
    """Load the TTS model on first request."""
    global model
    if model is None:
        model_path = current_model_config["path"]
        
        print(f"\n{'='*60}")
        print(f"  Loading model: {model_path}")
        print(f"  HF_HOME: {os.environ.get('HF_HOME', 'NOT SET')}")
        print(f"  Device: {DEVICE}")
        print(f"{'='*60}\n")
        
        # Load Qwen3-TTS model
        model = Qwen3TTSModel.from_pretrained(
            model_path,
            device_map=DEVICE,
            dtype=DTYPE,
            cache_dir=HF_CACHE_DIR,
            local_files_only=False,
            attn_implementation="sdpa" if torch.cuda.is_available() else None,
        )
        print("Model loaded successfully!")
        
        # Compile the model for faster inference
        if torch.cuda.is_available():
            try:
                # Compile the forward pass
                model.model.forward = torch.compile(
                    model.model.forward,
                    mode="reduce-overhead",
                    fullgraph=True,
                )
                print("[OK] torch.compile enabled for model.forward")
            except Exception as e:
                print(f"[WARN] torch.compile failed: {e}")
    return model


@app.route("/")
def index():
    return render_template(
        "index.html",
        speakers=current_model_config["speakers"],
        languages=current_model_config["languages"],
        current_model=current_model_config,
        hf_cache_dir=HF_CACHE_DIR
    )


@app.route("/generate", methods=["POST"])
def generate():
    """Generate TTS audio from text."""
    data = request.json
    text = data.get("text", "").strip()
    speaker = data.get("speaker", "Ryan")
    language = data.get("language", "Auto")
    instruct = data.get("instruct", "").strip()

    if not text:
        return jsonify({"error": "Text is empty"}), 400

    model = load_model()

    # Generate audio (no_grad for speed + memory savings)
    wav_bytes = None
    with torch.no_grad():
        try:
            # Use language parameter directly (Auto works for auto-detection)
            print(f"Using language: {language}")
            print(f"Using speaker: {speaker}")
            if instruct:
                print(f"Using instruction: {instruct}")
            
            wavs, sr = model.generate_custom_voice(
                text=text,
                language=language,
                speaker=speaker,
                instruct=instruct if instruct else None,
            )
        except Exception as e:
            print(f"Error during generation: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"Generation failed: {str(e)}"}), 500

    # Encode WAV bytes directly from numpy array (single write)
    wav_buffer = io.BytesIO()
    sf.write(wav_buffer, wavs[0] if isinstance(wavs, list) else wavs, sr, format="WAV")
    wav_bytes = wav_buffer.getvalue()
    wav_buffer.seek(0)

    # Save to file
    filename = f"tts_{uuid.uuid4().hex[:8]}_{speaker}_{int(time.time())}.wav"
    filepath = os.path.join(OUTPUT_DIR, filename)
    sf.write(filepath, wavs[0] if isinstance(wavs, list) else wavs, sr)

    # Save to history.json
    history_file = os.path.join(OUTPUT_DIR, "history.json")
    history_data = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
        except (json.JSONDecodeError, IOError):
            history_data = []
    
    history_data.insert(0, {
        "filename": filename,
        "text": text,
        "speaker": speaker,
        "language": language,
        "instruct": instruct,
        "created": time.time(),
    })
    # Keep only last 100 entries
    history_data = history_data[:100]
    
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history_data, f, ensure_ascii=False, indent=2)

    return jsonify({
        "audio_wav": base64.b64encode(wav_buffer.read()).decode("utf-8"),
        "sample_rate": int(sr),
        "filename": filename,
    })


@app.route("/speakers", methods=["GET"])
def get_speakers():
    """Return available speakers."""
    return jsonify({"speakers": current_model_config["speakers"]})


@app.route("/languages", methods=["GET"])
def get_languages():
    """Return available languages."""
    return jsonify({"languages": current_model_config["languages"]})


@app.route("/history", methods=["GET"])
def get_history():
    """Get list of generated audio files."""
    files = []
    history_file = os.path.join(OUTPUT_DIR, "history.json")
    
    # Try to load from history.json first
    history_data = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
        except (json.JSONDecodeError, IOError):
            history_data = []
    
    # If history.json is empty, scan output folder for .wav files
    if not history_data:
        print("[INFO] history.json empty, scanning output/ folder...")
        for f_name in sorted(os.listdir(OUTPUT_DIR), reverse=True):
            if f_name.endswith('.wav') and f_name != 'history.json':
                filepath = os.path.join(OUTPUT_DIR, f_name)
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    name_without_ext = f_name.replace('.wav', '')
                    parts = name_without_ext.split('_')
                    speaker = parts[-2] if len(parts) >= 3 else 'Unknown'
                    history_data.append({
                        "filename": f_name,
                        "text": f"{speaker} — Generated on {time.strftime('%Y-%m-%d %H:%M', time.localtime(stat.st_mtime))}",
                        "speaker": speaker,
                        "created": stat.st_mtime,
                    })
    
    # Clean up history.json: remove entries for files that no longer exist
    cleaned_data = [e for e in history_data if os.path.exists(os.path.join(OUTPUT_DIR, e.get("filename", "")))]
    if len(cleaned_data) != len(history_data):
        print(f"[INFO] history.json cleaned: {len(history_data) - len(cleaned_data)} stale entries removed")
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
        history_data = cleaned_data
    
    for entry in history_data:
        filename = entry.get("filename", "")
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        if os.path.exists(filepath):
            stat = os.stat(filepath)
            files.append({
                "filename": filename,
                "size": stat.st_size,
                "created": stat.st_mtime,
                "text": entry.get("text", "Unknown"),
                "speaker": entry.get("speaker", "Unknown"),
            })
    return jsonify({"files": files})


@app.route("/play/<filename>", methods=["GET"])
def play_audio(filename):
    """Play audio file."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(filepath):
        return send_file(filepath, mimetype='audio/wav')
    return jsonify({"error": "File not found"}), 404


@app.route("/delete/<filename>", methods=["POST"])
def delete_audio(filename):
    """Delete audio file."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        
        # Remove from history.json
        history_file = os.path.join(OUTPUT_DIR, "history.json")
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
            
            history_data = [entry for entry in history_data if entry.get("filename") != filename]
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, ensure_ascii=False, indent=2)
        
        return jsonify({"success": True})
    return jsonify({"error": "File not found"}), 404


@app.route("/output_size", methods=["GET"])
def get_output_size():
    """Get total size of output directory."""
    total_size = 0
    if os.path.exists(OUTPUT_DIR):
        for f in os.listdir(OUTPUT_DIR):
            fp = os.path.join(OUTPUT_DIR, f)
            if os.path.isfile(fp):
                total_size += os.path.getsize(fp)
    return jsonify({"size": total_size})








if __name__ == "__main__":
    print("=" * 60)
    print("  Qwen3-TTS Web GUI")
    print("=" * 60)
    print(f"  Model: {current_model_config['path']}")
    print(f"  HF_HOME: {os.environ.get('HF_HOME', 'NOT SET')}")
    print(f"  Device: {DEVICE}")
    print(f"  Dtype: {DTYPE}")
    print("=" * 60)
    print()
    app.run(host="0.0.0.0", port=5000, debug=True)
