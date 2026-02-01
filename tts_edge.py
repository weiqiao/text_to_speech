import argparse
import asyncio
import os
import re
from pathlib import Path

import edge_tts

# Optional: only needed if you want to convert mp3 -> wav
def mp3_to_wav(mp3_path: str, wav_path: str):
    from pydub import AudioSegment
    audio = AudioSegment.from_file(mp3_path, format="mp3")
    audio.export(wav_path, format="wav")


def normalize_text(text: str) -> str:
    # Make punctuation / spacing a bit more TTS-friendly
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


def normalize_rate(rate: str) -> str:
    rate = rate.strip()
    if not rate:
        return "+0%"
    if rate[0] not in "+-":
        rate = f"+{rate}"
    if not rate.endswith("%"):
        rate = f"{rate}%"
    return rate


def normalize_pitch(pitch: str) -> str:
    pitch = pitch.strip()
    if not pitch:
        return "+0Hz"
    if pitch[0] not in "+-":
        pitch = f"+{pitch}"
    if not pitch.endswith("Hz"):
        pitch = f"{pitch}Hz"
    return pitch


async def synthesize(text: str, out_path: str, voice: str, rate: str, pitch: str):
    out_path = str(out_path)
    Path(os.path.dirname(out_path) or ".").mkdir(parents=True, exist_ok=True)

    ext = Path(out_path).suffix.lower()
    if ext not in [".mp3", ".wav"]:
        raise ValueError("Output file must end with .mp3 or .wav")

    # edge-tts writes audio as mp3
    tmp_mp3 = out_path if ext == ".mp3" else str(Path(out_path).with_suffix(".mp3"))

    text = normalize_text(text)
    rate = normalize_rate(rate)
    pitch = normalize_pitch(pitch)
    communicate = edge_tts.Communicate(text, voice=voice, rate=rate, pitch=pitch)
    await communicate.save(tmp_mp3)

    if ext == ".wav":
        mp3_to_wav(tmp_mp3, out_path)
        # Clean up the intermediate mp3
        try:
            os.remove(tmp_mp3)
        except OSError:
            pass


def main():
    parser = argparse.ArgumentParser(description="Natural TTS using Microsoft neural voices (edge-tts).",
                                     allow_abbrev=False)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", type=str, help="Text to speak.")
    group.add_argument("--text_file", type=str, help="Path to a .txt file to speak.")

    parser.add_argument("--out", type=str, default="voiceover.mp3", help="Output audio path (.mp3 or .wav).")
    parser.add_argument("--voice", type=str, default="en-US-JennyNeural",
                        help="Voice name, e.g. en-US-JennyNeural, en-US-GuyNeural, en-GB-SoniaNeural")
    parser.add_argument("--rate", type=str, default="+0%",
                        help='Speaking rate, e.g. "-10%", "0%", "+10%". '
                             'For negative values in zsh, use --rate=-5%.')
    parser.add_argument("--pitch", type=str, default="+0Hz",
                        help='Pitch, e.g. "-2Hz", "0Hz", "+2Hz". '
                             'For negative values in zsh, use --pitch=-2Hz.')
    args = parser.parse_args()

    if args.text_file:
        text = Path(args.text_file).read_text(encoding="utf-8")
    else:
        text = args.text

    asyncio.run(synthesize(text=text, out_path=args.out, voice=args.voice, rate=args.rate, pitch=args.pitch))
    print(f"Saved: {args.out}")


if __name__ == "__main__":
    main()
