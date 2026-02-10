import time
import threading
import numpy as np
import keyboard
import queue

from stt.streaming_whisper import StreamingWhisper
from audio.push_to_talk import PushToTalkRecorder
from stt.transcriber import transcribe_chunk
from context.question_extractor import extract_question
from intent.intent_matcher import detect_intent
from intent.templates import TEMPLATES
from llm.responder import generate_answer
from logs.async_logger import AsyncConversationLogger
from ui.overlay import Overlay

# ------------------ SETUP ------------------

overlay = Overlay()
mic = PushToTalkRecorder()
whisper = StreamingWhisper()
conv_logger = AsyncConversationLogger()

recording = False
audio_window = []
processed = False

ui_queue = queue.Queue()

# ------------------ HOTKEY ACTIONS ------------------

def start_recording():
    global recording, audio_window, processed
    if recording:
        return

    print("🎤 Recording started")
    recording = True
    processed = False
    audio_window = []
    overlay.show_live_text("🎤 Listening...")
    mic.start()

def stop_recording():
    global recording
    if not recording:
        return

    print("🛑 Recording stopped")
    recording = False
    mic.stop()

# ------------------ MAIN WORKER LOOP ------------------

def main_loop():
    global audio_window, processed

    last_live_update = time.time()

    while True:
        time.sleep(0.01)

        # -------- LIVE LISTENING --------
        if recording:
            chunk = mic.read_chunk()
            if chunk is not None:
                print("🎧 audio chunk received", chunk.shape)
                audio_window.append(chunk)

            if time.time() - last_live_update > 0.4 and audio_window:
                audio = np.concatenate(audio_window, axis=0)

                # 🔥 FIX: flatten + float32 for Whisper
                audio = audio.flatten().astype(np.float32)

                partial = whisper.transcribe_partial(audio)

                if partial:
                    ui_queue.put(("live", partial))

                else:
                    # 🔥 Immediate feedback while gathering speech
                    ui_queue.put(("live", "Listening…"))

                last_live_update = time.time()


        # -------- FINAL PROCESSING --------
        if not recording and audio_window and not processed:
            processed = True

            audio = np.concatenate(audio_window, axis=0)
            audio_window.clear()

            final_text = transcribe_chunk(audio)
            if not final_text.strip():
                continue

            conv_logger.log("user", final_text)

            question = extract_question(final_text)
            intent = detect_intent(question)

            # ⚡ instant template
            instant_answer = TEMPLATES.get(intent, TEMPLATES["GENERIC"])
            ui_queue.put(("instant", instant_answer))
            


            # 🔥 polish in background
            def refine():
                refined = generate_answer(question)
                conv_logger.log("assistant", refined)
                ui_queue.put(("final", refined))

            threading.Thread(target=refine, daemon=True).start()

# ------------------ UI DISPATCHER ------------------

def ui_dispatcher():
    try:
        while True:
            msg_type, payload = ui_queue.get_nowait()

            if msg_type == "live":
                overlay.show_live_text("🗣️ " + payload)

            elif msg_type in ("instant", "final"):
                overlay.show_live_text(payload)

    except queue.Empty:
        pass

    overlay.root.after(80, ui_dispatcher)

# ------------------ HOTKEYS ------------------

keyboard.add_hotkey("alt+m", start_recording)
keyboard.add_hotkey("alt+n", stop_recording)

# ------------------ START ------------------

threading.Thread(target=main_loop, daemon=True).start()
overlay.root.after(80, ui_dispatcher)
overlay.run()
