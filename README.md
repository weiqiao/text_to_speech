# Convert Text to Speech
## Install
```
pip install edge-tts pydub
```
If you want WAV output, you also need ffmpeg installed:
```
macOS: brew install ffmpeg
Ubuntu: sudo apt-get install ffmpeg
Windows: choco install ffmpeg
```

## Usage
```
python tts_edge.py --text "Hi! This is a demo of the Text-to-Speech script. It turns text into natural-sounding audio." --out demo.mp3 --voice en-US-GuyNeural
```
### WAV output
```
python tts_edge.py --text_file narration.txt --out narration.wav --voice en-US-JennyNeural --rate=-5%
```
