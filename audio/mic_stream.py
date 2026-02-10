import sounddevice as sd
import queue

audio_queue = queue.Queue()
stream = None

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    audio_queue.put(indata.copy())

def start_mic(samplerate=16000):
    global stream
    if stream is None:
        stream = sd.InputStream(
            samplerate=samplerate,
            channels=1,
            callback=audio_callback
        )
        stream.start()

def stop_mic():
    global stream
    if stream:
        stream.stop()
        stream.close()
        stream = None

def get_audio_queue():
    return audio_queue