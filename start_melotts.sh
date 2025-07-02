#!/bin/bash
# Wait for GPU to initialize
until nvidia-smi &>/dev/null; do
  echo "Waiting for NVIDIA GPU to become ready..."
  sleep 1
done
source /home/felix/anaconda3/etc/profile.d/conda.sh
conda activate melotts
python /home/felix/src/MeloTTS/tts-server.py
