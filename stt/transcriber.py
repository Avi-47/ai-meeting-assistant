from faster_whisper import WhisperModel
import numpy as np

model = WhisperModel("base",device="cpu", compute_type="int8")

def transcribe_chunk(audio_chunk):
    audio_chunk = audio_chunk.flatten().astype(np.float32)

    segments, _ = model.transcribe(audio_chunk, language= "en", beam_size=5, vad_filter = True)

    text = ""
    for seg in segments:
        text += seg.text + " "
    return text.strip()