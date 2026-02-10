import os
import json
import threading
import sounddevice as sd
import websocket

API_KEY = os.getenv("DEEPGRAM_API_KEY")

if not API_KEY:
    raise RuntimeError("DEEPGRAM_API_KEY not set")

WS_URL = (
    "wss://api.deepgram.com/v1/listen"
    "?encoding=linear16"
    "&sample_rate=16000"
    "&channels=1"
    "&model=nova-2"
    "&interim_results=true"
    "&punctuate=true"
)

ws = websocket.WebSocket()

ws.connect(
    WS_URL,
    header=[f"Authorization: Token {API_KEY}"]
)

print("✅ Connected to Deepgram")

def send_audio():
    with sd.RawInputStream(
        samplerate=16000,
        channels=1,
        dtype="int16",
        blocksize=1024
    ) as mic:
        while True:
            data, _ = mic.read(1024)
            ws.send(bytes(data), opcode=websocket.ABNF.OPCODE_BINARY)

def receive():
    while True:
        msg = json.loads(ws.recv())
        if "channel" in msg:
            alt = msg["channel"]["alternatives"][0]
            text = alt.get("transcript", "")
            if text:
                print("LIVE:", text)

threading.Thread(target=send_audio, daemon=True).start()
receive()
