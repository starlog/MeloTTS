# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Core Development Commands

### Installation and Setup
```bash
# Install in development mode
pip install -e .

# Install required models (Japanese support)
python -m unidic download

# Docker build (alternative installation)
docker build -t melotts .
```

### Running the Application
```bash
# Web UI
melo-ui
# Or: python melo/app.py

# CLI usage
melo "Text to read" output.wav --language EN --speaker EN-US --speed 1.5

# TTS server
python tts-server.py

# Kiosk server
python kiosk-server.py
```

### Testing
```bash
# Run model tests
python test/test_base_model_tts_package.py [LANGUAGE]
# Where LANGUAGE can be: EN, ES, FR, ZH, JP, KR

# Run test with S3 download
python test/test_base_model_tts_package_from_S3.py [LANGUAGE]
```

## Architecture Overview

### Core Components

1. **API Layer** (`melo/api.py`):
   - `TTS` class: Main interface for text-to-speech synthesis
   - Handles model initialization, device selection, and audio generation
   - Supports multiple languages: EN, ES, FR, ZH, JP, KR

2. **Model Architecture** (`melo/models.py`):
   - `SynthesizerTrn`: Core VITS-based synthesis model
   - Implements multi-speaker, multi-language support
   - Uses attention mechanisms and flow-based generation

3. **Text Processing** (`melo/text/`):
   - Language-specific phonemizers for each supported language
   - BERT integration for enhanced text understanding
   - Handles mixed language scenarios (e.g., Chinese with English)

4. **Server Components**:
   - `tts-server.py`: Flask-based API with caching support
   - `kiosk-server.py`: Alternative server implementation
   - `melo/app.py`: Gradio web UI

### Language Support

The system supports multiple languages with specialized processing:
- **English**: Multiple accents (US, British, Indian, Australian)
- **Chinese**: Supports mixed Chinese-English text
- **Spanish, French, Japanese, Korean**: Native language support

Each language has dedicated modules in `melo/text/` for phoneme conversion and text normalization.

### Model Training
Training infrastructure is available via `melo/train.py` with configuration in `melo/configs/`.

## Key Dependencies

- PyTorch and torchaudio for neural network operations
- Transformers (v4.27.4) for BERT integration
- Language-specific tools: unidic (Japanese), g2pkk (Korean), gruut (European languages)
- Audio processing: librosa, pydub
- Web frameworks: Flask, Gradio

## Performance Considerations

- Supports both CPU and GPU inference (auto-detection)
- Real-time inference capable on CPU
- Caching implemented in `tts-server.py` for repeated text
- Model downloads are cached locally after first use