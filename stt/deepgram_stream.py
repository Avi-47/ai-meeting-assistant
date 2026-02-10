import os
import json
import threading
import sounddevice as sd
import websocket
import time

class DeepgramStreamer:
    def __init__(self, on_text, device_index=29):
        self.api_key = os.getenv("DEEPGRAM_API_KEY")
        if not self.api_key:
            raise RuntimeError("DEEPGRAM_API_KEY not set")

        self.on_text = on_text
        self.device_index = device_index
        self.ws = None
        self.running = False

    def start(self):
        if self.running:
            return

        self.running = True

        url = (
            "wss://api.deepgram.com/v1/listen"
            "?encoding=linear16"
            "&sample_rate=44100"
            "&channels=2"
            "&model=nova-2"
            "&interim_results=true"
            "&punctuate=true"
        )

        self.ws = websocket.WebSocket()
        self.ws.connect(
            url,
            header=[f"Authorization: Token {self.api_key}"]
        )

        threading.Thread(target=self._send_audio, daemon=True).start()
        threading.Thread(target=self._receive_text, daemon=True).start()

    def stop(self):
        self.running = False
        time.sleep(0.1)  # let threads exit cleanly

        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass
            self.ws = None

    def _send_audio(self):
        try:
            with sd.InputStream(
                samplerate=44100,
                device=29,      # Stereo Mix
                channels=1,     # 🔥 FORCE MONO
                dtype="int16",
                blocksize=1024
            ) as stream:
                while self.running:
                    data, _ = stream.read(1024)
                    if self.ws:
                        self.ws.send(data.tobytes(), opcode=websocket.ABNF.OPCODE_BINARY)
        except Exception as e:
            print("Audio stream error:", e)

    def _receive_text(self):
        while self.running and self.ws:
            try:
                msg = json.loads(self.ws.recv())

                if "channel" in msg:
                    alternatives = msg["channel"].get("alternatives", [])
                    if alternatives:
                        text = alternatives[0].get("transcript", "")
                        if text:
                            self.on_text(text)
            except Exception:
                break
