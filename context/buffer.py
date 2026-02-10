from collections import deque
import time

class TranscriptBuffer:
    def __init__(self, max_seconds=60):
        self.buffer = deque()
        self.max_seconds = max_seconds

    def add(self, text):
        self.buffer.append((text, time.time()))
        self._cleanup()

    def _cleanup(self):
        now = time.time()
        while self.buffer and now - self.buffer[0][1] > self.max_seconds:
            self.buffer.popleft()

    def get_context(self):
        self._cleanup()
        return " ".join(t[0] for t in self.buffer)
