import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_answer(question: str) -> str:
    if not question.strip():
        return "⚠️ No clear question detected."

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a calm, confident professional. "
                        "Give concise, polished, corporate-style answers. "
                        "No filler words."
                    )
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            temperature=0.3,
            max_tokens=120,
        )

        return completion.choices[0].message.content.strip()

    except Exception as e:
        return f"⚠️ AI error: {str(e)}"
