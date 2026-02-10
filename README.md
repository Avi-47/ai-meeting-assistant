AI Meeting Assistant

A local AI-powered meeting assistant that listens to your speech, extracts questions, detects intents, and generates instant and refined answers in real-time.

⚠️ Note: Currently, only main.py is fully functional. Please use it to run the assistant.

Features

Push-to-talk recording with hotkeys (Alt+M to start, Alt+N to stop)

Real-time transcription using Whisper

Question extraction from transcribed audio

Intent detection with instant response templates

AI-generated answers using a local LLM pipeline

Overlay UI showing live and final responses

Conversation logging to track interactions

Requirements

Python 3.10+

Install dependencies:

pip install -r requirements.txt


Optional: Create a .env file for any secret keys (currently not used by main.py)

Usage

Run the assistant with:

python main.py

Hotkeys

Alt + M → Start recording

Alt + N → Stop recording

The overlay will show live transcriptions, instant template answers, and final AI-generated answers.

Project Structure
audio/           # Microphone recording modules
context/         # Question extraction
intent/          # Intent detection and templates
llm/             # AI response generation
logs/            # Conversation logging
stt/             # Speech-to-text modules
triggers/        # Hotkey management
ui/              # Overlay user interface
main.py          # Fully working assistant
main_app.py      # Work in progress
requirements.txt # Python dependencies

Notes

Keep your secret keys (like Deepgram or Hugging Face tokens) in .env or key.txt — do not push them to GitHub.

main_app.py is a work-in-progress and may not run correctly yet.

Contributions are welcome!
