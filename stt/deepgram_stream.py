import os
import json
import threading
import sounddevice as sd
import websocket
import time
import numpy as np

sd._initialize()  # ensure hostapis loaded


class DeepgramStreamer:
    def __init__(self, on_text, device_index=24):
        self.api_key = os.getenv("DEEPGRAM_API_KEY")
        if not self.api_key:
            raise RuntimeError("DEEPGRAM_API_KEY not set")

        self.on_text = on_text
        self.device_index = device_index
        self.ws = None
        self.running = False

        info = sd.query_devices(self.device_index)
        self.native_rate = int(info["default_samplerate"])  # 48000

    # ---------- WS CALLBACKS ----------

    def _on_message(self, ws, message):
        try:
            msg = json.loads(message)

            if msg.get("type") != "Results":
                return

            channel = msg.get("channel")
            if not channel:
                return

            alts = channel.get("alternatives", [])
            if not alts:
                return

            text = alts[0].get("transcript", "")
            if text:
                self.on_text(text)

        except Exception as e:
            print("Message parse error:", e)

    def _on_error(self, ws, error):
        print("WS error:", error)

    def _on_close(self, ws, close_status_code, close_msg):
        print("WS closed:", close_status_code, close_msg)

    # ---------- CONTROL ----------

    def start(self):
        if self.running:
            return

        self.running = True

        self.ws = websocket.WebSocketApp(
            "wss://api.deepgram.com/v1/listen"
            "?encoding=linear16"
            "&sample_rate=16000"
            "&channels=1"
            "&model=nova-2"
            "&interim_results=true"
            "&punctuate=true",
            header=[f"Authorization: Token {self.api_key}"],
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )

        threading.Thread(
            target=self.ws.run_forever,
            daemon=True
        ).start()


    def stop(self):
        self.running = False
        time.sleep(0.1)

        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass
            self.ws = None

    # ---------- AUDIO ----------
    def _on_open(self, ws):
        print("WS opened")

        # 🔥 start audio ONLY after socket is open
        threading.Thread(
            target=self._send_audio,
            daemon=True
        ).start()

    def _send_audio(self):
        try:
            with sd.InputStream(
                device=self.device_index,      # Stereo Mix (MME)
                samplerate=self.native_rate,   # usually 44100
                channels=2,
                dtype="int16",
                blocksize=1024
            ) as stream:

                while self.running:
                    if not self.ws or not self.ws.sock or not self.ws.sock.connected:
                        continue

                    data, _ = stream.read(1024)

                    # 🔥 stereo → mono
                    audio = data.mean(axis=1)
                    audio = audio.astype(np.float32) / 32768.0

                    target_len = int(len(audio) * 16000 / self.native_rate)
                    if target_len <= 0:
                        continue

                    resampled = np.interp(
                        np.linspace(0, len(audio), target_len, endpoint=False),
                        np.arange(len(audio)),
                        audio
                    )

                    resampled = (resampled * 32768).astype(np.int16)

                    self.ws.send(
                        resampled.tobytes(),
                        opcode=websocket.ABNF.OPCODE_BINARY
                    )

        except Exception as e:
            print("Audio stream error:", e)
