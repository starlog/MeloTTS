from flask import Flask, request, jsonify
from melo.api import TTS
from pydub import AudioSegment
from pydub.playback import play

app = Flask(__name__)

# Initialize the TTS model
speed = 1.3
device = 'cpu' # or cuda:0
model = TTS(language='KR', device=device)
speaker_ids = model.hps.data.spk2id

@app.route('/', methods=['POST'])
def generate_audio():
    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    output_path = 'kr.wav'
    model.tts_to_file(text, speaker_ids['KR'], output_path, speed=speed)

    # Play the audio
    audio = AudioSegment.from_wav(output_path)
    play(audio)

    return jsonify({'message': 'Audio played successfully'}), 200

if __name__ == '__main__':
    app.run(host='localhost', port=5555)
