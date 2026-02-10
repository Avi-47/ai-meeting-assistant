import sounddevice as sd
import queue
import numpy as np

class PushToTalkRecorder:
    def __init__(self, samplerate=16000):
        self.samplerate = samplerate
        self.q = queue.Queue()
        self.stream = None

    def _callback(self, indata, frames, time, status):
        if status:
            print(status)
        # indata shape: (frames, channels)
        self.q.put(indata.copy())

    def start(self):
        # clear old audio
        while not self.q.empty():
            self.q.get()

        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=1,
            callback=self._callback,
            blocksize=800   # ~50ms chunks (LOW LATENCY)
        )
        self.stream.start()

    def read_chunk(self):
        try:
            return self.q.get_nowait()
        except queue.Empty:
            return None

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
