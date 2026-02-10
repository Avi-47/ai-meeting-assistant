import numpy as np
from faster_whisper import WhisperModel

model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

class StreamingWhisper:
    def __init__(self):
        pass   # 🔥 no prev_text logic at all

    def transcribe_partial(self, audio: np.ndarray):
        segments, _ = model.transcribe(
            audio,
            language="en",
            beam_size=1,
            vad_filter=False,
            without_timestamps=True
        )

        text = " ".join(seg.text for seg in segments).strip()

        # 🔥 ALWAYS return whatever Whisper has
        if text:
            return text

        return None
