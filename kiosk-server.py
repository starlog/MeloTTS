from flask import Flask, request, jsonify
import requests
from melo.api import TTS
from pydub import AudioSegment
from pydub.playback import play
import shutil
import os
import argparse

app = Flask(__name__)

# Initialize the TTS model
speed = 1.3
device = 'cuda' # or cuda:0
output_path = 'kr.wav'

model = TTS(language='KR', device=device)
speaker_ids = model.hps.data.spk2id

@app.route('/', methods=['POST'])
def generate_audio():
    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    model.tts_to_file(text, speaker_ids['KR'], output_path, speed=speed)
    shutil.move(output_path, os.path.join(args.file_location, output_path))

    # Adjust file location if it starts with '/mnt/'
    file_location = args.file_location
    if file_location.startswith('/mnt/'):
        drive_letter = file_location[5].upper()
        file_location = f'{drive_letter}:\\' + file_location[7:]
        print(f"Generating output file at {file_location}{output_path}")

    return jsonify({"command": "play", "data": f"{file_location}{output_path}"}), 200

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Speaker server configuration')
    parser.add_argument('--port', type=int, default=5555, help='Port on which the speaker server runs')
    parser.add_argument('--file_location', type=str, default='/mnt/c/kiosk/', help='Where the server generates output file')

    args = parser.parse_args()

    # Print out parsed arguments for information
    print("===================================================================================================")
    print(f"tts-server run with: port={args.port}, file_location={args.file_location}")
    print("===================================================================================================")

    app.run(host='localhost', port=args.port)
