import re

QUESTION_WORDS = [
    "what", "how", "why", "when", "where",
    "can", "could", "should", "will", "would",
    "do", "does", "did", "is", "are", "am",
    "have", "has", "had"
]

def extract_question(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 5]

    for s in reversed(sentences):
        words = s.lower().split()
        if any(q in words[:3] for q in QUESTION_WORDS):
            return s if s.endswith("?") else s + "?"

    return sentences[-1] if sentences else text
