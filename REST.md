# REST API Documentation

This document describes the REST APIs available in MeloTTS servers and external services it integrates with.

## Table of Contents
- [TTS Server API](#tts-server-api)
- [Kiosk Server API](#kiosk-server-api)
- [External Services](#external-services)
  - [Speaker Server API](#speaker-server-api)
  - [Model Download APIs](#model-download-apis)
- [Client Examples](#client-examples)

## TTS Server API

The TTS server (`tts-server.py`) provides a REST API for text-to-speech synthesis with caching support.

### Server Configuration

```bash
python tts-server.py --port 5002 --speaker http://localhost:9333/play
```

**Arguments:**
- `--port`: Server port (default: 5002)
- `--speaker`: External speaker server endpoint (default: http://localhost:9333/play)

### Endpoints

#### POST /tts

Generate speech from text and forward to speaker server.

**Request:**
```http
POST /tts
Content-Type: application/json

{
    "text": "안녕하세요! 오늘은 날씨가 정말 좋네요."
}
```

**Request Body:**
- `text` (string, required): Text to convert to speech

**Response:**

Success (200):
```json
{
    "message": "Audio sent successfully"
}
```

Error (400):
```json
{
    "error": "No text provided"
}
```

Error (500):
```json
{
    "error": "Failed to send audio file. Status code: 404"
}
```

**Server Behavior:**
1. Generates MD5 hash of input text for caching
2. Checks cache for existing audio file
3. If cached, uses existing file; otherwise generates new audio
4. Forwards audio file to configured speaker server as multipart/form-data
5. Maintains cache for future requests

**Technical Details:**
- Language: Korean (hardcoded)
- Speed: 1.3x (hardcoded)
- Audio format: WAV
- Cache location: `/tmp/`
- Cache key: MD5 hash of text
- File naming: `tts_{text_hash}_{uuid}.wav`

## Kiosk Server API

The kiosk server (`kiosk-server.py`) provides a simpler API for local file generation.

### Server Configuration

```bash
python kiosk-server.py --port 5555 --file_location /mnt/c/kiosk/
```

**Arguments:**
- `--port`: Server port (default: 5555)
- `--file_location`: Output directory for audio files (default: /mnt/c/kiosk/)

### Endpoints

#### POST /

Generate speech and save to local filesystem.

**Request:**
```http
POST /
Content-Type: application/json

{
    "text": "안녕하세요! 오늘은 날씨가 정말 좋네요."
}
```

**Request Body:**
- `text` (string, required): Text to convert to speech

**Response:**

Success (200):
```json
{
    "command": "play",
    "data": "C:\\kiosk\\kr.wav"
}
```

Error (400):
```json
{
    "error": "No text provided"
}
```

**Server Behavior:**
1. Generates audio file with fixed name `kr.wav`
2. Saves to configured file location
3. Converts Unix paths to Windows paths if needed (for WSL)
4. Returns play command with file path

**Technical Details:**
- Language: Korean (hardcoded)
- Speed: 1.3x (hardcoded)
- Audio format: WAV
- Output filename: `kr.wav` (fixed)
- Device: CUDA (hardcoded)

## Client Examples

### Python Client

```python
import requests
import json

# TTS Server Example
def generate_tts(text, server_url="http://localhost:5002"):
    response = requests.post(
        f"{server_url}/tts",
        headers={"Content-Type": "application/json"},
        data=json.dumps({"text": text})
    )
    
    if response.status_code == 200:
        print("Audio sent successfully")
    else:
        print(f"Error: {response.json()}")

# Kiosk Server Example
def generate_kiosk_audio(text, server_url="http://localhost:5555"):
    response = requests.post(
        server_url,
        headers={"Content-Type": "application/json"},
        data=json.dumps({"text": text})
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Audio saved to: {result['data']}")
        return result['data']
    else:
        print(f"Error: {response.json()}")
```

### cURL Examples

```bash
# TTS Server
curl -X POST http://localhost:5002/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "안녕하세요! 오늘은 날씨가 정말 좋네요."}'

# Kiosk Server
curl -X POST http://localhost:5555/ \
  -H "Content-Type: application/json" \
  -d '{"text": "안녕하세요! 오늘은 날씨가 정말 좋네요."}'
```

### JavaScript/Node.js Client

```javascript
// TTS Server Example
async function generateTTS(text) {
    const response = await fetch('http://localhost:5002/tts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: text })
    });
    
    const result = await response.json();
    console.log(result);
}

// Kiosk Server Example
async function generateKioskAudio(text) {
    const response = await fetch('http://localhost:5555/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: text })
    });
    
    const result = await response.json();
    console.log(`Audio file: ${result.data}`);
    return result.data;
}
```

## External Services

### Speaker Server API

The TTS server integrates with an external speaker server (likely Asterisk-based) to play audio.

#### POST /play

Plays an audio file on the speaker system.

**Default Endpoint:** `http://localhost:9333/play`

**Request:**
```http
POST /play
Content-Type: multipart/form-data

--boundary
Content-Disposition: form-data; name="file"; filename="tts_abc123_def456.wav"
Content-Type: audio/wav

<binary audio data>
--boundary--
```

**Expected Response:**
- Status: 200 OK for successful playback
- Any other status code is treated as an error

**Integration Notes:**
- The TTS server automatically forwards generated audio to this endpoint
- The speaker server should handle audio playback through connected speakers
- Based on commit history, this appears to be an Asterisk-based routing system

### Model Download APIs

MeloTTS automatically downloads pre-trained models from S3 when needed.

**Base URL:** `https://myshell-public-repo-host.s3.amazonaws.com/openvoice/basespeakers/`

**Available Models:**

| Language | Config URL | Checkpoint URL |
|----------|------------|----------------|
| EN | `{base}/EN/config.json` | `{base}/EN/checkpoint.pth` |
| EN_V2 | `{base}/EN_V2/config.json` | `{base}/EN_V2/checkpoint.pth` |
| ES | `{base}/ES/config.json` | `{base}/ES/checkpoint.pth` |
| FR | `{base}/FR/config.json` | `{base}/FR/checkpoint.pth` |
| ZH | `{base}/ZH/config.json` | `{base}/ZH/checkpoint.pth` |
| JP | `{base}/JP/config.json` | `{base}/JP/checkpoint.pth` |
| KR | `{base}/KR/config.json` | `{base}/KR/checkpoint.pth` |

**Pre-trained Models:**
- Generator: `{base}/pretrained/G.pth`
- Discriminator: `{base}/pretrained/D.pth`
- Duration: `{base}/pretrained/DUR.pth`

**Usage:**
- Models are downloaded automatically on first use
- Cached locally after download
- No authentication required (public S3 bucket)

## Integration Notes

### TTS Server Integration
The TTS server is designed to work with an external speaker service. It:
1. Generates audio from text
2. Forwards the audio file to the configured speaker endpoint
3. The speaker service is expected to accept multipart/form-data with a 'file' field

### Kiosk Server Integration
The kiosk server is designed for local file system integration:
1. Generates audio files in a specified directory
2. Returns the file path for external playback
3. Handles WSL path conversion for Windows compatibility

## Limitations

Both servers currently have these limitations:
- Language is hardcoded to Korean
- Speed is fixed at 1.3x
- No dynamic speaker selection
- No authentication/authorization
- TTS server requires external speaker service
- Kiosk server overwrites the same file on each request