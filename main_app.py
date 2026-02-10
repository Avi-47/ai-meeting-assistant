import os
import threading
import queue
import keyboard
from dotenv import load_dotenv

from stt.deepgram_stream import DeepgramStreamer
from context.question_extractor import extract_question
from intent.intent_matcher import detect_intent
from intent.templates import TEMPLATES
from llm.responder import generate_answer
from logs.async_logger import AsyncConversationLogger
from ui.overlay import Overlay

load_dotenv()

# ------------------ SETUP ------------------

overlay = Overlay()
conv_logger = AsyncConversationLogger()
ui_queue = queue.Queue()

final_text = ""

# ------------------ DEEPGRAM CALLBACK ------------------

def on_live_text(text: str):
    global final_text
    final_text = text
    ui_queue.put(("live", text))

    intent = detect_intent(text)
    if intent != "GENERIC":
        instant = TEMPLATES[intent]
        ui_queue.put(("instant", instant))

dg = DeepgramStreamer(on_live_text, device_index=1) 

# ------------------ HOTKEY ACTIONS ------------------

def start_recording():
    global final_text
    final_text = ""
    overlay.show_live_text("🎤 Listening...")
    dg.start()

def stop_recording():
    dg.stop()

    if not final_text.strip():
        return

    conv_logger.log("user", final_text)

    question = extract_question(final_text)
    intent = detect_intent(question)

    # ⚡ instant answer
    instant = TEMPLATES.get(intent, TEMPLATES["GENERIC"])
    ui_queue.put(("instant", instant))

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
            else:
                overlay.show_live_text(payload)
    except queue.Empty:
        pass

    overlay.root.after(80, ui_dispatcher)

# ------------------ HOTKEYS ------------------

keyboard.add_hotkey("alt+m", start_recording)
keyboard.add_hotkey("alt+n", stop_recording)

# ------------------ START ------------------

overlay.root.after(80, ui_dispatcher)
overlay.run()
