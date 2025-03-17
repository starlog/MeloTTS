from flask import Flask, request, jsonify
import requests
from melo.api import TTS
from pydub import AudioSegment
from pydub.playback import play
import shutil
import os
import argparse
import io
import uuid
import hashlib

app = Flask(__name__)

# Initialize the TTS model
speed = 1.3
device = 'cuda' # or cuda:0
temp_dir = '/tmp'

# Cache dictionary to store text -> filename mapping
tts_cache = {}

model = TTS(language='KR', device=device)
speaker_ids = model.hps.data.spk2id

@app.route('/tts', methods=['POST'])
def generate_audio():
    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    # Create a hash of the text to use as a key for consistency
    text_hash = hashlib.md5(text.encode()).hexdigest()
    
    # Check if the text has been processed before
    if text_hash in tts_cache:
        cached_filename = tts_cache[text_hash]
        output_path = os.path.join(temp_dir, cached_filename)
        
        # Check if the file still exists
        if os.path.exists(output_path):
            print(f"Using cached audio for text: '{text[:30]}...' (if longer)")
        else:
            # If file was deleted, regenerate and update cache
            output_path = generate_tts_file(text, text_hash)
    else:
        # Generate new audio file with unique name
        output_path = generate_tts_file(text, text_hash)
    
    # Send audio file directly as multipart/form-data with field name 'file'
    payload = {}
    files = [
        ('file', (os.path.basename(output_path), open(output_path, 'rb'), 'audio/wav'))
    ]
    headers = {}
    response = requests.request("POST", args.speaker, headers=headers, data=payload, files=files)
    
    # Clean up local file - commented out to maintain cache
    # if os.path.exists(output_path):
    #     os.remove(output_path)
    
    if response.status_code != 200:
        return jsonify({'error': f'Failed to send audio file. Status code: {response.status_code}'}), 500

    return jsonify({'message': 'Audio sent successfully'}), 200

def generate_tts_file(text, text_hash):
    """Generate TTS file and store in cache"""
    # Create unique filename based on uuid
    unique_filename = f"tts_{text_hash}_{uuid.uuid4().hex[:8]}.wav"
    output_path = os.path.join(temp_dir, unique_filename)
    
    # Generate audio file
    model.tts_to_file(text, speaker_ids['KR'], output_path, speed=speed)
    
    # Store in cache
    tts_cache[text_hash] = unique_filename
    print(f"Generated new audio file '{unique_filename}' for text: '{text[:30]}...' (if longer)")
    
    return output_path

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Speaker server configuration')
    parser.add_argument('--port', type=int, default=5002, help='Port on which the speaker server runs')
    parser.add_argument('--speaker', type=str, default='http://localhost:5001/play-audio', help='Speaker server address')

    args = parser.parse_args()

    # Print out parsed arguments for information
    print("===================================================================================================")
    print(f"tts-server run with: port={args.port}, speaker={args.speaker}")
    print("===================================================================================================")

    app.run(host='localhost', port=args.port)
