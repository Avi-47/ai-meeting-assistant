INTENTS = {
    "deployment": "DEPLOYMENT_RISK",
    "deploy": "DEPLOYMENT_RISK",
    "production": "DEPLOYMENT_RISK",
    "rollback": "DEPLOYMENT_RISK",
    "risk": "DEPLOYMENT_RISK",

    "scale": "SCALABILITY",
    "scalability": "SCALABILITY",
    "traffic": "SCALABILITY",

    "deadline": "TIMELINE",
    "timeline": "TIMELINE",
    "delivery": "TIMELINE",
}

def detect_intent(text: str) -> str:
    text = text.lower()
    for keyword, intent in INTENTS.items():
        if keyword in text:
            return intent
    return "GENERIC"
