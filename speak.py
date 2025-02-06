from flask import Flask, request, jsonify
import requests
from melo.api import TTS
from pydub import AudioSegment
from pydub.playback import play

app = Flask(__name__)

# Initialize the TTS model
speed = 1.3
device = 'cuda' # or cuda:0
output_path = '\mnt\d\kr.wav'

model = TTS(language='KR', device=device)
speaker_ids = model.hps.data.spk2id

@app.route('/', methods=['POST'])
def generate_audio():
    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    model.tts_to_file(text, speaker_ids['KR'], output_path, speed=speed)

    # Send HTTP POST request to http://localhost:8080/
    response = requests.post('http://localhost:8080/', json={"command": "play", "data": "d:\\kr.wav"})
    if response.status_code != 200:
        return jsonify({'error': 'Failed to send play command'}), 500

    return jsonify({'message': 'Audio played successfully'}), 200

if __name__ == '__main__':
    app.run(host='localhost', port=5555)
